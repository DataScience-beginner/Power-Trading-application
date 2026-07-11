"""AI-1.5 persistence for users, scoped conversations, and auditable messages."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from database.config import Base


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class AppUser(Base):
    """Authenticated SaaS user with an admin or client-level role."""

    __tablename__ = "app_users"

    id = Column(String(36), primary_key=True, default=new_id)
    email = Column(String(320), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    password_hash = Column(String(500), nullable=False)
    role = Column(String(30), nullable=False, default="client_user", index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class UserPortfolioAccess(Base):
    """Optional portfolio restriction for a client user."""

    __tablename__ = "user_portfolio_access"
    __table_args__ = (UniqueConstraint("user_id", "portfolio_id", name="uq_user_portfolio_access"),)

    id = Column(String(36), primary_key=True, default=new_id)
    user_id = Column(String(36), ForeignKey("app_users.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class ChatConversation(Base):
    """Conversation whose tenant scope is fixed when it is created."""

    __tablename__ = "chat_conversations"
    __table_args__ = (Index("ix_chat_conversation_scope", "user_id", "client_id", "updated_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    user_id = Column(String(36), ForeignKey("app_users.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="New energy conversation")
    status = Column(String(30), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    """User/assistant message plus tool, evidence, model, and safety metadata."""

    __tablename__ = "chat_messages"
    __table_args__ = (Index("ix_chat_message_conversation", "conversation_id", "created_at"),)

    id = Column(String(36), primary_key=True, default=new_id)
    conversation_id = Column(String(36), ForeignKey("chat_conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(80), nullable=True)
    provider = Column(String(80), nullable=True)
    model = Column(String(160), nullable=True)
    prompt_version = Column(String(80), nullable=True)
    tool_calls = Column(JSON, nullable=False, default=list)
    evidence = Column(JSON, nullable=False, default=list)
    confidence = Column(Integer, nullable=True)
    limitations = Column(JSON, nullable=False, default=list)
    safety_status = Column(String(40), nullable=False, default="allowed")
    token_usage = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    conversation = relationship("ChatConversation", back_populates="messages")
