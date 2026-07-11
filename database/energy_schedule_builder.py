"""
DB-native Energy Schedule builder.

This module derives EnergyScheduleMonth/EnergyScheduleDay records from the
canonical uploaded data already stored in daily_files and transactions.
"""

from collections import defaultdict
from datetime import date
from typing import Dict, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DailyFile, Transaction, Portfolio
from database.energy_schedule_crud import (
    calculate_daily_entry,
    get_or_create_daily_entry,
)


MARKETS = ("GDAM", "DAM", "RTM")


def _mwh_from_mw_slots(values) -> float:
    return sum(values) * 0.25


def _dor_market_summary(db: Session, daily_file: DailyFile) -> Dict[str, float]:
    transactions = db.query(Transaction).filter(
        Transaction.daily_file_id == daily_file.id
    ).all()

    quantity_mwh = _mwh_from_mw_slots(
        [txn.quantity_mw or 0.0 for txn in transactions]
    )
    amount = sum(txn.amount or 0.0 for txn in transactions)
    charges = daily_file.charges or {}

    return {
        "scheduled_quantity_mwh": quantity_mwh,
        "nldc_fee": float(charges.get("nldc_application_fee") or 0.0),
        "ctu_charges": float(charges.get("ctu_transmission_charges") or 0.0),
        "total_cost": abs(float(amount or 0.0)),
        "other_charges": charges,
    }


def _sch_consumption_summary(db: Session, sch_files) -> Dict:
    by_slot = defaultdict(float)
    total_mw_slots = []

    for sch_file in sch_files:
        transactions = db.query(Transaction).filter(
            Transaction.daily_file_id == sch_file.id
        ).all()

        for txn in transactions:
            consumption_mw = (
                txn.interface_drawal_mw
                or txn.regional_drawal_mw
                or txn.quantity_mw
                or 0.0
            )
            by_slot[txn.time_slot] += consumption_mw
            total_mw_slots.append(consumption_mw)

    timeslots = [
        {"time_slot": slot, "consumption_mw": value}
        for slot, value in sorted(by_slot.items())
    ]

    return {
        "timeslots": timeslots,
        "total_mwh": _mwh_from_mw_slots(total_mw_slots),
    }


def rebuild_energy_schedule_for_day(
    db: Session,
    portfolio_id: int,
    trading_date: date,
) -> Dict:
    """
    Rebuild one EnergyScheduleDay from daily_files/transactions.
    """
    files = db.query(DailyFile).filter(
        and_(
            DailyFile.portfolio_id == portfolio_id,
            DailyFile.trading_date == trading_date,
        )
    ).all()

    daily_entry = get_or_create_daily_entry(db, portfolio_id, trading_date)

    dor_files = {
        f.sub_category: f
        for f in files
        if f.main_category == "DOR" and f.sub_category in MARKETS
    }
    sch_files = [
        f
        for f in files
        if f.main_category == "SCH" and f.sub_category in MARKETS
    ]

    for market in MARKETS:
        dor_file = dor_files.get(market)
        if not dor_file:
            continue

        summary = _dor_market_summary(db, dor_file)
        prefix = market.lower()
        setattr(daily_entry, f"{prefix}_nldc_fee", summary["nldc_fee"])
        setattr(daily_entry, f"{prefix}_ctu_charges", summary["ctu_charges"])
        setattr(daily_entry, f"{prefix}_cost", summary["total_cost"])
        setattr(
            daily_entry,
            f"{prefix}_scheduled_quantity_mwh",
            summary["scheduled_quantity_mwh"],
        )
        setattr(daily_entry, f"{prefix}_other_charges", summary["other_charges"])
        setattr(daily_entry, f"has_{prefix}_data", 1)

    if sch_files:
        sch_summary = _sch_consumption_summary(db, sch_files)
        daily_entry.consumption_after_losses_timeslots = sch_summary["timeslots"]
        daily_entry.total_consumption_after_losses_mwh = sch_summary["total_mwh"]
        daily_entry.has_sch_data = 1

    db.commit()
    db.refresh(daily_entry)

    daily_entry = calculate_daily_entry(db, daily_entry.id)

    return {
        "daily_entry_id": daily_entry.id,
        "trading_date": trading_date.isoformat(),
        "files_found": len(files),
        "dor_markets": sorted(dor_files.keys()),
        "sch_files": len(sch_files),
        "is_complete": bool(daily_entry.is_complete),
        "total_scheduled_mwh": daily_entry.total_scheduled_mwh,
        "total_consumption_after_losses_mwh": daily_entry.total_consumption_after_losses_mwh,
        "total_cost": daily_entry.total_cost,
    }


def rebuild_energy_schedules(
    db: Session,
    portfolio_id: Optional[int] = None,
) -> Dict:
    """
    Rebuild Energy Schedule entries for all dates with uploaded files.
    """
    portfolio_query = db.query(Portfolio)
    if portfolio_id is not None:
        portfolio_query = portfolio_query.filter(Portfolio.id == portfolio_id)

    results = []
    for portfolio in portfolio_query.all():
        dates = [
            row[0]
            for row in db.query(DailyFile.trading_date)
            .filter(DailyFile.portfolio_id == portfolio.id)
            .distinct()
            .order_by(DailyFile.trading_date)
            .all()
        ]

        for trading_date in dates:
            results.append(
                rebuild_energy_schedule_for_day(db, portfolio.id, trading_date)
            )

    return {
        "days_processed": len(results),
        "complete_days": sum(1 for item in results if item["is_complete"]),
        "results": results,
    }
