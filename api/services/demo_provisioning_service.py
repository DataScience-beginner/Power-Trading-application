"""Idempotent five-tenant synthetic demo provisioning."""

from datetime import date, datetime, time, timedelta
import math

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from api.schemas.forecasting import DemoProvisionRequest, DemoProvisionResponse, DemoTenantResponse
from api.security.chat_auth import hash_password
from database.chatbot_models import AppUser, UserPortfolioAccess
from database.forecasting_models import GenerationObservation
from database.models import Client, DailyFile, Portfolio, Transaction


DEMO_CLIENTS = [
    ("INW-MELLBRO", "Mellbro Sugars Pvt", 12.97, 80.22, 6000),
    ("INW-TEXTILES", "Kaveri Textiles Ltd", 11.02, 76.96, 4800),
    ("INW-CEMENT", "Deccan Cement Works", 16.51, 80.64, 7200),
    ("INW-AUTO", "Orion Auto Components", 13.08, 80.27, 4200),
    ("INW-STEEL", "Western Steel Industries", 19.08, 72.88, 8500),
]


def provision_demo(db: Session, payload: DemoProvisionRequest) -> DemoProvisionResponse:
    counts = {"clients": 0, "portfolios": 0, "users": 0, "generation_observations": 0, "daily_files": 0, "transactions": 0}
    tenants = []
    end_date = date.today() - timedelta(days=1)
    for client_index, (entity_id, name, lat, lon, capacity) in enumerate(DEMO_CLIENTS):
        client = db.query(Client).filter(or_(
            Client.entity_id == entity_id,
            func.lower(Client.entity_name) == name.lower(),
        )).first()
        if not client:
            client = Client(entity_id=entity_id, entity_name=name, lat=lat, lon=lon, capacity_kw=capacity, farm_type="solar")
            db.add(client); db.flush(); counts["clients"] += 1
        else:
            client.lat, client.lon, client.capacity_kw, client.farm_type = lat, lon, capacity, "solar"
        portfolios = []
        for portfolio_index in range(payload.portfolios_per_client):
            code = f"{entity_id}-P{portfolio_index + 1}"
            portfolio = db.query(Portfolio).filter(Portfolio.portfolio_code == code).first()
            if not portfolio:
                portfolio = Portfolio(client_id=client.id, portfolio_code=code, portfolio_name=f"{name} Portfolio {portfolio_index + 1}")
                db.add(portfolio); db.flush(); counts["portfolios"] += 1
            portfolios.append(portfolio)
            portfolio_capacity = capacity / payload.portfolios_per_client
            for day_offset in range(payload.days_of_history):
                observed_date = end_date - timedelta(days=payload.days_of_history - day_offset - 1)
                irradiation = 4.7 + 1.0 * math.sin((day_offset + client_index) / 4.2)
                temperature = 27 + 3 * math.sin((day_offset + portfolio_index) / 5.1)
                energy = portfolio_capacity * irradiation * (0.72 + client_index * 0.015) * (1 + 0.025 * math.sin(day_offset))
                observation = db.query(GenerationObservation).filter(
                    GenerationObservation.portfolio_id == portfolio.id,
                    GenerationObservation.observed_date == observed_date,
                    GenerationObservation.source_version == "demo-generation-v1",
                ).first()
                if not observation:
                    db.add(GenerationObservation(
                        client_id=client.id,
                        portfolio_id=portfolio.id,
                        observed_date=observed_date,
                        energy_kwh=round(energy, 2),
                        irradiation_kwh_m2=round(irradiation, 3),
                        temperature_c=round(temperature, 2),
                        source_type="demo_generator",
                        source_version="demo-generation-v1",
                        is_synthetic=True,
                        observation_metadata={"scenario": "multi-tenant-demo-v1"},
                    )); counts["generation_observations"] += 1
            _provision_trading_day(db, client_index, portfolio_index, portfolio, end_date, counts)
        email = f"client{client_index + 1}@demo.innowattenergy.com"
        user = db.query(AppUser).filter(AppUser.email == email).first()
        if not user:
            user = AppUser(
                email=email,
                display_name=f"{name} Demo User",
                password_hash=hash_password(payload.default_password),
                role="client_user",
                client_id=client.id,
            )
            db.add(user); db.flush(); counts["users"] += 1
        for portfolio in portfolios:
            access = db.query(UserPortfolioAccess).filter(
                UserPortfolioAccess.user_id == user.id,
                UserPortfolioAccess.portfolio_id == portfolio.id,
            ).first()
            if not access:
                db.add(UserPortfolioAccess(user_id=user.id, portfolio_id=portfolio.id))
        tenants.append(DemoTenantResponse(
            client_id=client.id,
            entity_id=client.entity_id,
            entity_name=name,
            portfolio_ids=[item.id for item in portfolios],
            portfolio_codes=[item.portfolio_code for item in portfolios],
            user_email=email,
        ))
    db.commit()
    return DemoProvisionResponse(
        status="ready",
        data_classification="synthetic",
        clients_total=len(tenants),
        tenants=tenants,
        records_created=counts,
        note="Demo users share the request password. Existing user passwords are never reset by repeat runs.",
    )


def _provision_trading_day(db: Session, client_index: int, portfolio_index: int, portfolio: Portfolio, trading_date: date, counts: dict) -> None:
    for report_type, transaction_type in [("DOR-DAM", "buy"), ("SCH-DAM", "scheduling")]:
        daily_file = db.query(DailyFile).filter(
            DailyFile.portfolio_id == portfolio.id,
            DailyFile.trading_date == trading_date,
            DailyFile.report_type == report_type,
        ).first()
        if daily_file:
            continue
        daily_file = DailyFile(
            portfolio_id=portfolio.id,
            trading_date=trading_date,
            delivery_date=trading_date,
            main_category=report_type.split("-")[0],
            sub_category="DAM",
            report_type=report_type,
            original_filename=f"synthetic-{portfolio.portfolio_code}-{report_type}.json",
            file_path="synthetic://multi-tenant-demo-v1",
            file_metadata={"is_synthetic": True, "scenario": "multi-tenant-demo-v1"},
            parsed_at=datetime.now(),
        )
        db.add(daily_file); db.flush(); counts["daily_files"] += 1
        for block in range(96):
            start = datetime.combine(trading_date, time.min) + timedelta(minutes=15 * block)
            quantity = 1.5 + client_index * 0.35 + portfolio_index * 0.2 + max(0, math.sin((block - 24) / 18))
            rate = 3500 + client_index * 180 + 900 * max(0, math.cos((block - 72) / 16))
            db.add(Transaction(
                daily_file_id=daily_file.id,
                date=trading_date,
                time_slot=f"{start:%H:%M} - {(start + timedelta(minutes=15)):%H:%M}",
                time_block_start=start,
                time_block_end=start + timedelta(minutes=15),
                transaction_type=transaction_type,
                quantity_mw=round(quantity if transaction_type == "buy" else quantity * 0.94, 4),
                rate_per_mwh=round(rate if transaction_type == "buy" else 0, 2),
                amount=round(quantity * rate / 4, 2) if transaction_type == "buy" else 0,
                net_scheduled_mw=round(quantity * 0.94, 4) if transaction_type == "scheduling" else 0,
            )); counts["transactions"] += 1
