"""
Energy Schedule CRUD Operations
--------------------------------
Database service functions for Energy Schedule workflow.
Handles creation, reading, updating, and deletion of monthly sheets and daily entries.

Author: Power Trading Application
Date: 2026-01-16
"""

from sqlalchemy.orm import Session
from database.models import EnergyScheduleMonth, EnergyScheduleDay, Portfolio
from datetime import datetime, date
from typing import Optional, List, Dict
import calendar


# ==================== MONTH SHEET OPERATIONS ====================

def get_or_create_month_sheet(
    db: Session,
    portfolio_id: int,
    year: int,
    month: int
) -> EnergyScheduleMonth:
    """
    Get existing month sheet or create new one.
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID
        year: Year (e.g., 2026)
        month: Month (1-12)
        
    Returns:
        EnergyScheduleMonth object
    """
    # Check if month sheet exists
    month_sheet = db.query(EnergyScheduleMonth).filter(
        EnergyScheduleMonth.portfolio_id == portfolio_id,
        EnergyScheduleMonth.year == year,
        EnergyScheduleMonth.month == month
    ).first()
    
    if month_sheet:
        return month_sheet
    
    # Create new month sheet
    month_name = f"{calendar.month_name[month]} {year}"
    month_sheet = EnergyScheduleMonth(
        portfolio_id=portfolio_id,
        year=year,
        month=month,
        month_name=month_name
    )
    
    db.add(month_sheet)
    db.commit()
    db.refresh(month_sheet)
    
    return month_sheet


def get_month_sheet(
    db: Session,
    portfolio_id: int,
    year: int,
    month: int
) -> Optional[EnergyScheduleMonth]:
    """
    Get month sheet if it exists.
    
    Returns:
        EnergyScheduleMonth object or None
    """
    return db.query(EnergyScheduleMonth).filter(
        EnergyScheduleMonth.portfolio_id == portfolio_id,
        EnergyScheduleMonth.year == year,
        EnergyScheduleMonth.month == month
    ).first()


def get_all_month_sheets(
    db: Session,
    portfolio_id: Optional[int] = None
) -> List[EnergyScheduleMonth]:
    """
    Get all month sheets, optionally filtered by portfolio.
    
    Args:
        db: Database session
        portfolio_id: Optional portfolio ID filter
        
    Returns:
        List of EnergyScheduleMonth objects
    """
    query = db.query(EnergyScheduleMonth)
    
    if portfolio_id:
        query = query.filter(EnergyScheduleMonth.portfolio_id == portfolio_id)
    
    return query.order_by(
        EnergyScheduleMonth.year.desc(),
        EnergyScheduleMonth.month.desc()
    ).all()


def update_month_summary(
    db: Session,
    month_sheet_id: int
) -> EnergyScheduleMonth:
    """
    Recalculate and update month sheet summary from daily entries.
    
    Args:
        db: Database session
        month_sheet_id: Month sheet ID
        
    Returns:
        Updated EnergyScheduleMonth object
    """
    month_sheet = db.query(EnergyScheduleMonth).filter(
        EnergyScheduleMonth.id == month_sheet_id
    ).first()
    
    if not month_sheet:
        raise ValueError(f"Month sheet {month_sheet_id} not found")
    
    # Get all daily entries for this month
    daily_entries = db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.month_sheet_id == month_sheet_id
    ).all()
    
    # Aggregate metrics
    total_scheduled = sum(entry.total_scheduled_mwh for entry in daily_entries)
    total_consumption = sum(entry.total_consumption_after_losses_mwh for entry in daily_entries)
    total_savings = sum(entry.energy_savings_mwh for entry in daily_entries)
    total_gdam = sum(entry.gdam_cost for entry in daily_entries)
    total_dam = sum(entry.dam_cost for entry in daily_entries)
    total_rtm = sum(entry.rtm_cost for entry in daily_entries)
    
    # Average CTU losses (weighted by scheduled quantity)
    ctu_entries = [e for e in daily_entries if e.total_scheduled_mwh > 0]
    if ctu_entries:
        avg_ctu_losses = sum(
            e.ctu_losses_percent * e.total_scheduled_mwh 
            for e in ctu_entries
        ) / total_scheduled if total_scheduled > 0 else 0
    else:
        avg_ctu_losses = 0
    
    # Update month sheet
    month_sheet.total_scheduled_mwh = total_scheduled
    month_sheet.total_consumption_after_losses_mwh = total_consumption
    month_sheet.total_energy_savings_mwh = total_savings
    month_sheet.total_gdam_cost = total_gdam
    month_sheet.total_dam_cost = total_dam
    month_sheet.total_rtm_cost = total_rtm
    month_sheet.average_ctu_losses_percent = avg_ctu_losses
    month_sheet.days_completed = len([e for e in daily_entries if e.is_complete])
    
    # Check if month is complete (all days have data)
    days_in_month = calendar.monthrange(month_sheet.year, month_sheet.month)[1]
    month_sheet.is_complete = 1 if month_sheet.days_completed == days_in_month else 0
    
    month_sheet.updated_at = datetime.now()
    
    db.commit()
    db.refresh(month_sheet)
    
    return month_sheet


# ==================== DAILY ENTRY OPERATIONS ====================

def get_or_create_daily_entry(
    db: Session,
    portfolio_id: int,
    trading_date: date
) -> EnergyScheduleDay:
    """
    Get existing daily entry or create new one.
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID
        trading_date: Trading date
        
    Returns:
        EnergyScheduleDay object
    """
    # Get or create month sheet
    month_sheet = get_or_create_month_sheet(
        db, portfolio_id, trading_date.year, trading_date.month
    )
    
    # Check if daily entry exists
    daily_entry = db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.month_sheet_id == month_sheet.id,
        EnergyScheduleDay.trading_date == trading_date
    ).first()
    
    if daily_entry:
        return daily_entry
    
    # Create new daily entry
    daily_entry = EnergyScheduleDay(
        month_sheet_id=month_sheet.id,
        trading_date=trading_date,
        day_of_month=trading_date.day
    )
    
    db.add(daily_entry)
    db.commit()
    db.refresh(daily_entry)
    
    return daily_entry


def update_daily_entry_dor_data(
    db: Session,
    daily_entry_id: int,
    market_type: str,
    dor_data: Dict
) -> EnergyScheduleDay:
    """
    Update daily entry with DOR summary data (GDAM/DAM/RTM).
    
    Args:
        db: Database session
        daily_entry_id: Daily entry ID
        market_type: "GDAM", "DAM", or "RTM"
        dor_data: Parsed DOR data from DOR_EnergySchedule_Parser
        
    Returns:
        Updated EnergyScheduleDay object
    """
    daily_entry = db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.id == daily_entry_id
    ).first()
    
    if not daily_entry:
        raise ValueError(f"Daily entry {daily_entry_id} not found")
    
    summary = dor_data.get('summary', {})
    
    if market_type == 'GDAM':
        daily_entry.gdam_nldc_fee = summary.get('nldc_application_fee', 0.0)
        daily_entry.gdam_ctu_charges = summary.get('ctu_transmission_charges', {}).get('total', 0.0)
        daily_entry.gdam_cost = summary.get('total_cost', 0.0)
        daily_entry.gdam_scheduled_quantity_mwh = summary.get('scheduled_quantity', 0.0)
        daily_entry.gdam_other_charges = summary.get('other_charges', {})
        daily_entry.has_gdam_data = 1
        
    elif market_type == 'DAM':
        daily_entry.dam_nldc_fee = summary.get('nldc_application_fee', 0.0)
        daily_entry.dam_ctu_charges = summary.get('ctu_transmission_charges', {}).get('total', 0.0)
        daily_entry.dam_cost = summary.get('total_cost', 0.0)
        daily_entry.dam_scheduled_quantity_mwh = summary.get('scheduled_quantity', 0.0)
        daily_entry.dam_other_charges = summary.get('other_charges', {})
        daily_entry.has_dam_data = 1
        
    elif market_type == 'RTM':
        daily_entry.rtm_nldc_fee = summary.get('nldc_application_fee', 0.0)
        daily_entry.rtm_ctu_charges = summary.get('ctu_transmission_charges', {}).get('total', 0.0)
        daily_entry.rtm_cost = summary.get('total_cost', 0.0)
        daily_entry.rtm_scheduled_quantity_mwh = summary.get('scheduled_quantity', 0.0)
        daily_entry.rtm_other_charges = summary.get('other_charges', {})
        daily_entry.has_rtm_data = 1
    
    daily_entry.updated_at = datetime.now()
    
    db.commit()
    db.refresh(daily_entry)
    
    return daily_entry


def update_daily_entry_sch_data(
    db: Session,
    daily_entry_id: int,
    sch_data: Dict
) -> EnergyScheduleDay:
    """
    Update daily entry with SCH consumption data.
    
    Args:
        db: Database session
        daily_entry_id: Daily entry ID
        sch_data: Parsed SCH data from SCH_Energy_Schedule_Parser
        
    Returns:
        Updated EnergyScheduleDay object
    """
    daily_entry = db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.id == daily_entry_id
    ).first()
    
    if not daily_entry:
        raise ValueError(f"Daily entry {daily_entry_id} not found")
    
    consumption = sch_data.get('consumption_after_losses', {})
    losses = sch_data.get('losses', {})
    
    # Update consumption data
    daily_entry.consumption_after_losses_timeslots = consumption.get('timeslots', [])
    daily_entry.total_consumption_after_losses_mwh = consumption.get('total_mwh', 0.0)
    
    # Update loss percentages
    daily_entry.regional_loss_percent = losses.get('regional_percent', 0.0)
    daily_entry.state_loss_percent = losses.get('state_percent', 0.0)
    daily_entry.combined_loss_percent = losses.get('combined_percent', 0.0)
    
    daily_entry.has_sch_data = 1
    daily_entry.updated_at = datetime.now()
    
    db.commit()
    db.refresh(daily_entry)
    
    return daily_entry


def calculate_daily_entry(
    db: Session,
    daily_entry_id: int
) -> EnergyScheduleDay:
    """
    Calculate derived fields for daily entry.
    
    Performs calculations:
    - Total scheduled MWh (GDAM + DAM + RTM)
    - Total charges (NLDC + CTU)
    - CTU Losses % = (Scheduled - Consumption) / Scheduled * 100
    - Energy Savings
    
    Args:
        db: Database session
        daily_entry_id: Daily entry ID
        
    Returns:
        Updated EnergyScheduleDay object with calculations
    """
    daily_entry = db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.id == daily_entry_id
    ).first()
    
    if not daily_entry:
        raise ValueError(f"Daily entry {daily_entry_id} not found")
    
    # Calculate total scheduled MWh (sum of all markets)
    daily_entry.total_scheduled_mwh = (
        daily_entry.gdam_scheduled_quantity_mwh +
        daily_entry.dam_scheduled_quantity_mwh +
        daily_entry.rtm_scheduled_quantity_mwh
    )
    
    # Calculate total charges
    daily_entry.total_nldc_fee = (
        daily_entry.gdam_nldc_fee +
        daily_entry.dam_nldc_fee +
        daily_entry.rtm_nldc_fee
    )
    
    daily_entry.total_ctu_charges = (
        daily_entry.gdam_ctu_charges +
        daily_entry.dam_ctu_charges +
        daily_entry.rtm_ctu_charges
    )
    
    daily_entry.total_cost = (
        daily_entry.gdam_cost +
        daily_entry.dam_cost +
        daily_entry.rtm_cost
    )
    
    # Calculate CTU Losses %
    if daily_entry.total_scheduled_mwh > 0:
        ctu_losses_mwh = daily_entry.total_scheduled_mwh - daily_entry.total_consumption_after_losses_mwh
        daily_entry.ctu_losses_mwh = ctu_losses_mwh
        daily_entry.ctu_losses_percent = (ctu_losses_mwh / daily_entry.total_scheduled_mwh) * 100
    else:
        daily_entry.ctu_losses_mwh = 0.0
        daily_entry.ctu_losses_percent = 0.0
    
    # Calculate Energy Savings (CTU Losses in MWh)
    daily_entry.energy_savings_mwh = daily_entry.ctu_losses_mwh
    
    # Check if all data is present
    daily_entry.is_complete = 1 if (
        daily_entry.has_gdam_data and
        daily_entry.has_dam_data and
        daily_entry.has_rtm_data and
        daily_entry.has_sch_data
    ) else 0
    
    daily_entry.calculated_at = datetime.now()
    daily_entry.updated_at = datetime.now()
    
    db.commit()
    db.refresh(daily_entry)
    
    # Update month sheet summary
    update_month_summary(db, daily_entry.month_sheet_id)
    
    return daily_entry


def get_daily_entry_by_date(
    db: Session,
    portfolio_id: int,
    trading_date: date
) -> Optional[EnergyScheduleDay]:
    """
    Get daily entry for specific date and portfolio.
    
    Returns:
        EnergyScheduleDay object or None
    """
    month_sheet = get_month_sheet(
        db, portfolio_id, trading_date.year, trading_date.month
    )
    
    if not month_sheet:
        return None
    
    return db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.month_sheet_id == month_sheet.id,
        EnergyScheduleDay.trading_date == trading_date
    ).first()


def get_all_daily_entries(
    db: Session,
    month_sheet_id: int
) -> List[EnergyScheduleDay]:
    """
    Get all daily entries for a month sheet.
    
    Returns:
        List of EnergyScheduleDay objects
    """
    return db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.month_sheet_id == month_sheet_id
    ).order_by(
        EnergyScheduleDay.trading_date
    ).all()


def delete_daily_entry(
    db: Session,
    daily_entry_id: int
) -> bool:
    """
    Delete a daily entry.
    
    Returns:
        True if deleted, False if not found
    """
    daily_entry = db.query(EnergyScheduleDay).filter(
        EnergyScheduleDay.id == daily_entry_id
    ).first()
    
    if not daily_entry:
        return False
    
    month_sheet_id = daily_entry.month_sheet_id
    
    db.delete(daily_entry)
    db.commit()
    
    # Update month sheet summary
    update_month_summary(db, month_sheet_id)
    
    return True


def delete_month_sheet(
    db: Session,
    month_sheet_id: int
) -> bool:
    """
    Delete a month sheet and all its daily entries.
    
    Returns:
        True if deleted, False if not found
    """
    month_sheet = db.query(EnergyScheduleMonth).filter(
        EnergyScheduleMonth.id == month_sheet_id
    ).first()
    
    if not month_sheet:
        return False
    
    db.delete(month_sheet)
    db.commit()
    
    return True
