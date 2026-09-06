-- Energy schedule Excel-conversion consumption inputs.
-- Additive migration: does not alter existing savings or schedule tables.

CREATE TABLE IF NOT EXISTS energy_schedule_consumption (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    consumption_date DATE NOT NULL,
    c1_kwh DOUBLE PRECISION DEFAULT 0.0,
    c2_kwh DOUBLE PRECISION DEFAULT 0.0,
    c4_kwh DOUBLE PRECISION DEFAULT 0.0,
    c5_kwh DOUBLE PRECISION DEFAULT 0.0,
    base_tariff_per_unit DOUBLE PRECISION,
    source VARCHAR DEFAULT 'manual',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_energy_schedule_consumption_day UNIQUE (portfolio_id, consumption_date)
);

CREATE INDEX IF NOT EXISTS ix_energy_schedule_consumption_portfolio_id
    ON energy_schedule_consumption(portfolio_id);

CREATE INDEX IF NOT EXISTS ix_energy_schedule_consumption_date
    ON energy_schedule_consumption(consumption_date);
