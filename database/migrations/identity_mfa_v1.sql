-- Additive encrypted TOTP MFA persistence.
CREATE TABLE IF NOT EXISTS mfa_factors (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES app_users(id),
    factor_type VARCHAR(20) NOT NULL DEFAULT 'totp',
    secret_ciphertext VARCHAR(1000) NOT NULL,
    recovery_code_hashes JSON NOT NULL DEFAULT '[]',
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_mfa_factor_user ON mfa_factors(user_id);
