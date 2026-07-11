-- AI-2 additive solar forecasting persistence. No existing tables are changed.

CREATE TABLE IF NOT EXISTS generation_observations (
    id VARCHAR(36) PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    observed_date DATE NOT NULL,
    energy_kwh DOUBLE PRECISION NOT NULL,
    irradiation_kwh_m2 DOUBLE PRECISION,
    temperature_c DOUBLE PRECISION,
    source_type VARCHAR(40) NOT NULL,
    source_version VARCHAR(40) NOT NULL,
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    quality_status VARCHAR(30) NOT NULL DEFAULT 'accepted',
    observation_metadata JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_generation_observation UNIQUE (portfolio_id, observed_date, source_version)
);
CREATE INDEX IF NOT EXISTS ix_generation_scope_date ON generation_observations(client_id, portfolio_id, observed_date);

CREATE TABLE IF NOT EXISTS forecast_runs (
    id VARCHAR(36) PRIMARY KEY,
    correlation_id VARCHAR(100) NOT NULL,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    forecast_type VARCHAR(40) NOT NULL,
    contract_version VARCHAR(40) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(40) NOT NULL,
    weather_provider VARCHAR(80) NOT NULL,
    weather_source VARCHAR(30) NOT NULL,
    data_classification VARCHAR(30) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    capacity_kw DOUBLE PRECISION NOT NULL,
    horizon_days INTEGER NOT NULL,
    training_points INTEGER NOT NULL,
    calibration_factor DOUBLE PRECISION NOT NULL,
    backtest_metrics JSON NOT NULL DEFAULT '{}',
    limitations JSON NOT NULL DEFAULT '[]',
    confidence DOUBLE PRECISION NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_forecast_run_scope ON forecast_runs(client_id, portfolio_id, created_at);

CREATE TABLE IF NOT EXISTS forecast_points (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES forecast_runs(id),
    forecast_date DATE NOT NULL,
    p10_kwh DOUBLE PRECISION NOT NULL,
    p50_kwh DOUBLE PRECISION NOT NULL,
    p90_kwh DOUBLE PRECISION NOT NULL,
    irradiation_kwh_m2 DOUBLE PRECISION NOT NULL,
    temperature_c DOUBLE PRECISION NOT NULL,
    cloud_cover_pct DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_forecast_run_date UNIQUE (run_id, forecast_date)
);
