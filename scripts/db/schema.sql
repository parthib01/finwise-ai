-- ============================================================
-- FinWise AI - PostgreSQL Schema
-- Module 1: Core relational schema
-- Source of truth for database structure
-- ============================================================

-- Enable UUID generation (safe to re-run)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS: Stable identity
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ============================================================
-- SESSIONS: Authentication lifecycle (short-lived)
-- ============================================================
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- ============================================================
-- CONVERSATIONS: Logical chat threads (long-lived)
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ============================================================
-- MESSAGE ROLE ENUM (idempotent)
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'message_role'
    ) THEN
        CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
    END IF;
END$$;

-- ============================================================
-- MESSAGES: Immutable audit log (append-only)
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ============================================================
-- CONVERSATION SUMMARIES: Derived, replaceable memory
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_summaries (
    conversation_id UUID PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INDEXES: Performance-critical access paths
-- ============================================================

-- Fast retrieval of messages for a conversation in time order
CREATE INDEX IF NOT EXISTS idx_messages_conversation_time
ON messages (conversation_id, created_at);

-- Fast lookup of a user's recent conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_activity
ON conversations (user_id, last_active_at);

-- Fast validation & cleanup of user sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_expiry
ON sessions (user_id, expires_at);
