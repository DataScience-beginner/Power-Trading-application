-- Additive enterprise identity recovery, sessions, and security events.
CREATE TABLE IF NOT EXISTS identity_profiles (
    user_id VARCHAR(36) PRIMARY KEY REFERENCES app_users(id),
    phone_e164 VARCHAR(20) UNIQUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    phone_verified BOOLEAN NOT NULL DEFAULT FALSE,
    must_change_password BOOLEAN NOT NULL DEFAULT FALSE,
    password_changed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS recovery_challenges (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES app_users(id),
    identifier_hash VARCHAR(64) NOT NULL,
    role_scope VARCHAR(30) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    delivery_status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_recovery_lookup ON recovery_challenges(identifier_hash, created_at);
CREATE TABLE IF NOT EXISTS auth_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES app_users(id),
    role VARCHAR(30) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS security_events (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES app_users(id),
    event_type VARCHAR(80) NOT NULL,
    outcome VARCHAR(30) NOT NULL,
    actor_type VARCHAR(30) NOT NULL,
    actor_id VARCHAR(320),
    correlation_id VARCHAR(100) NOT NULL,
    event_metadata JSON NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_security_event_subject ON security_events(user_id, created_at);
