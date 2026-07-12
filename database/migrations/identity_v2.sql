-- Additive onboarding verification persistence.
CREATE TABLE IF NOT EXISTS onboarding_challenges (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES app_users(id),
    channel VARCHAR(20) NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    delivery_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_onboarding_lookup ON onboarding_challenges(user_id, channel, created_at);
