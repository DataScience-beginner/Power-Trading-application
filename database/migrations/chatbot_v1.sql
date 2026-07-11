-- AI-1.5 additive SaaS authentication and chatbot migration.
CREATE TABLE IF NOT EXISTS app_users (
 id VARCHAR(36) PRIMARY KEY, email VARCHAR(320) UNIQUE NOT NULL, display_name VARCHAR(255) NOT NULL,
 password_hash VARCHAR(500) NOT NULL, role VARCHAR(30) NOT NULL, client_id INTEGER REFERENCES clients(id),
 is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL, updated_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS user_portfolio_access (
 id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36) NOT NULL REFERENCES app_users(id),
 portfolio_id INTEGER NOT NULL REFERENCES portfolios(id), created_at TIMESTAMP NOT NULL,
 CONSTRAINT uq_user_portfolio_access UNIQUE(user_id, portfolio_id)
);
CREATE TABLE IF NOT EXISTS chat_conversations (
 id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36) NOT NULL REFERENCES app_users(id),
 client_id INTEGER NOT NULL REFERENCES clients(id), portfolio_id INTEGER REFERENCES portfolios(id),
 title VARCHAR(255) NOT NULL, status VARCHAR(30) NOT NULL, created_at TIMESTAMP NOT NULL, updated_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_messages (
 id VARCHAR(36) PRIMARY KEY, conversation_id VARCHAR(36) NOT NULL REFERENCES chat_conversations(id),
 role VARCHAR(20) NOT NULL, content TEXT NOT NULL, intent VARCHAR(80), provider VARCHAR(80), model VARCHAR(160),
 prompt_version VARCHAR(80), tool_calls JSON NOT NULL DEFAULT '[]', evidence JSON NOT NULL DEFAULT '[]',
 confidence INTEGER, limitations JSON NOT NULL DEFAULT '[]', safety_status VARCHAR(40) NOT NULL,
 token_usage JSON NOT NULL DEFAULT '{}', created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_chat_conversation_scope ON chat_conversations(user_id, client_id, updated_at);
CREATE INDEX IF NOT EXISTS ix_chat_message_conversation ON chat_messages(conversation_id, created_at);
