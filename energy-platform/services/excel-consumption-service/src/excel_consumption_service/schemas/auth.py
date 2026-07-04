from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login input shared by the client and admin portals."""

    email: str
    password: str = Field(min_length=8)
    portal: str = Field(pattern="^(client|admin)$")


class AuthenticatedUser(BaseModel):
    """Role-aware user payload returned to the frontend."""

    id: str
    tenant_id: str | None
    email: str
    full_name: str
    role_codes: list[str]


class LoginResponse(BaseModel):
    """Auth response sent after successful login."""

    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser
