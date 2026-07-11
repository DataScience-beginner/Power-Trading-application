-- AI Phase 1 additive migration for quality runs and findings.
-- Requires AI Foundation V1 and leaves all current V0 tables unchanged.

CREATE TABLE IF NOT EXISTS data_quality_runs (
    id VARCHAR(36) PRIMARY KEY,
    correlation_id VARCHAR(100) NOT NULL,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    policy_version VARCHAR(40) NOT NULL DEFAULT 'data-quality-v1',
    policy_configuration JSON NOT NULL DEFAULT '{}',
    engine_version VARCHAR(40) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(30) NOT NULL DEFAULT 'completed',
    files_evaluated INTEGER NOT NULL DEFAULT 0,
    transactions_evaluated INTEGER NOT NULL DEFAULT 0,
    finding_counts JSON NOT NULL DEFAULT '{}',
    data_classification VARCHAR(30) NOT NULL DEFAULT 'unknown',
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_quality_findings (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES data_quality_runs(id),
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    daily_file_id INTEGER REFERENCES daily_files(id),
    rule_id VARCHAR(120) NOT NULL,
    rule_version VARCHAR(40) NOT NULL DEFAULT '1.0.0',
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(60) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    evidence JSON NOT NULL DEFAULT '[]',
    recommended_action TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    detected_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_quality_run_scope ON data_quality_runs(client_id, portfolio_id, started_at);
CREATE INDEX IF NOT EXISTS ix_quality_finding_scope ON data_quality_findings(client_id, portfolio_id, severity);
CREATE INDEX IF NOT EXISTS ix_quality_finding_run ON data_quality_findings(run_id);
