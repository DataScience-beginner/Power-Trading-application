"""Typed authentication and conversational-assistant contracts."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=10, max_length=200)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    role: str
    client_id: int | None
    portfolio_ids: list[int] = Field(default_factory=list)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: datetime
    user: UserResponse


class BootstrapAdminRequest(LoginRequest):
    display_name: str = Field(..., min_length=2, max_length=255)


class UserCreateRequest(LoginRequest):
    display_name: str = Field(..., min_length=2, max_length=255)
    role: Literal["platform_admin", "client_user"]
    client_id: int | None = Field(None, gt=0)
    portfolio_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scope(self):
        if self.role == "client_user" and not self.client_id:
            raise ValueError("client_id is required for client users")
        if self.role == "platform_admin" and self.client_id is not None:
            raise ValueError("platform admins cannot be bound to one client")
        return self


class ConversationCreateRequest(BaseModel):
    client_id: int = Field(..., gt=0)
    portfolio_id: int | None = Field(None, gt=0)
    title: str = Field("New energy conversation", min_length=2, max_length=255)


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    intent: str | None
    provider: str | None
    model: str | None
    tool_calls: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    confidence: int | None
    limitations: list[str]
    safety_status: str
    token_usage: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    client_id: int
    portfolio_id: int | None
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = Field(default_factory=list)


class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    start_date: datetime | None = None
    end_date: datetime | None = None


class ChatQueryResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    suggested_questions: list[str]
