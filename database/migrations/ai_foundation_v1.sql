-- AI Phase 0 additive migration.
-- Existing V0 tables and data are intentionally unchanged.
-- Production rollout: back up, apply in staging, validate, then apply in production.

CREATE TABLE IF NOT EXISTS canonical_entities (
    id VARCHAR(36) PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    parent_entity_id VARCHAR(36) REFERENCES canonical_entities(id),
    entity_type VARCHAR(80) NOT NULL,
    external_key VARCHAR(180) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    schema_version VARCHAR(40) NOT NULL DEFAULT 'canonical-v1',
    version INTEGER NOT NULL DEFAULT 1,
    attributes JSON NOT NULL DEFAULT '{}',
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_canonical_entity_version UNIQUE (entity_type, external_key, version)
);

CREATE TABLE IF NOT EXISTS source_artifacts (
    id VARCHAR(36) PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    canonical_entity_id VARCHAR(36) REFERENCES canonical_entities(id),
    supersedes_artifact_id VARCHAR(36) REFERENCES source_artifacts(id),
    source_type VARCHAR(80) NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    content_checksum VARCHAR(128) NOT NULL,
    storage_uri VARCHAR(1000),
    source_schema_version VARCHAR(80) NOT NULL DEFAULT 'unknown',
    parser_name VARCHAR(120),
    parser_version VARCHAR(40),
    artifact_version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(30) NOT NULL DEFAULT 'registered',
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    artifact_metadata JSON NOT NULL DEFAULT '{}',
    observed_at TIMESTAMP,
    registered_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_source_artifact_version UNIQUE (client_id, content_checksum, artifact_version)
);

CREATE TABLE IF NOT EXISTS processing_runs (
    id VARCHAR(36) PRIMARY KEY,
    correlation_id VARCHAR(100) NOT NULL,
    source_artifact_id VARCHAR(36) NOT NULL REFERENCES source_artifacts(id),
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    run_type VARCHAR(80) NOT NULL,
    executor_type VARCHAR(30) NOT NULL,
    executor_id VARCHAR(120) NOT NULL,
    executor_version VARCHAR(40) NOT NULL,
    contract_version VARCHAR(40) NOT NULL,
    status VARCHAR(30) NOT NULL,
    input_summary JSON NOT NULL DEFAULT '{}',
    output_summary JSON NOT NULL DEFAULT '{}',
    error_details JSON NOT NULL DEFAULT '{}',
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS business_rule_versions (
    id VARCHAR(36) PRIMARY KEY,
    rule_key VARCHAR(160) NOT NULL,
    rule_type VARCHAR(80) NOT NULL,
    scope_type VARCHAR(40) NOT NULL,
    scope_key VARCHAR(160) NOT NULL,
    jurisdiction VARCHAR(80),
    version INTEGER NOT NULL,
    schema_version VARCHAR(40) NOT NULL,
    configuration JSON NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    status VARCHAR(30) NOT NULL,
    approved_by VARCHAR(120),
    approval_note TEXT,
    created_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_business_rule_version UNIQUE (rule_key, scope_type, scope_key, version)
);

CREATE TABLE IF NOT EXISTS ai_execution_audits (
    id VARCHAR(36) PRIMARY KEY,
    correlation_id VARCHAR(100) NOT NULL,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    actor_type VARCHAR(30) NOT NULL,
    actor_id VARCHAR(120) NOT NULL,
    agent_id VARCHAR(120),
    agent_version VARCHAR(40),
    capability VARCHAR(120) NOT NULL,
    contract_version VARCHAR(40) NOT NULL,
    model_provider VARCHAR(80),
    model_name VARCHAR(120),
    model_version VARCHAR(80),
    prompt_version VARCHAR(80),
    input_references JSON NOT NULL DEFAULT '[]',
    tool_calls JSON NOT NULL DEFAULT '[]',
    output_payload JSON NOT NULL DEFAULT '{}',
    confidence DOUBLE PRECISION,
    status VARCHAR(30) NOT NULL,
    limitations JSON NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_records (
    id VARCHAR(36) PRIMARY KEY,
    audit_event_id VARCHAR(36) REFERENCES ai_execution_audits(id),
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    decision_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    rationale JSON NOT NULL DEFAULT '[]',
    evidence JSON NOT NULL DEFAULT '[]',
    alternatives JSON NOT NULL DEFAULT '[]',
    limitations JSON NOT NULL DEFAULT '[]',
    confidence DOUBLE PRECISION,
    status VARCHAR(30) NOT NULL,
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE,
    reviewed_by VARCHAR(120),
    reviewed_at TIMESTAMP,
    review_note TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_canonical_entity_scope ON canonical_entities(client_id, portfolio_id, entity_type);
CREATE INDEX IF NOT EXISTS ix_source_artifact_scope ON source_artifacts(client_id, portfolio_id, source_type);
CREATE INDEX IF NOT EXISTS ix_processing_run_scope ON processing_runs(client_id, portfolio_id, run_type);
CREATE INDEX IF NOT EXISTS ix_business_rule_effective ON business_rule_versions(rule_key, status, valid_from, valid_to);
CREATE INDEX IF NOT EXISTS ix_ai_audit_scope ON ai_execution_audits(client_id, portfolio_id, capability);
CREATE INDEX IF NOT EXISTS ix_decision_scope ON decision_records(client_id, portfolio_id, decision_type);
