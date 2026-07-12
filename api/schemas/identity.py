"""Enterprise identity login and account-recovery contracts."""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


class RoleLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=10, max_length=200)
    portal: Literal["admin", "client"]
    mfa_code: str | None = Field(None, min_length=6, max_length=40)


class MfaEnrollmentResponse(BaseModel):
    factor_id: str
    secret: str
    provisioning_uri: str
    message: str = "Store the secret securely and verify one code before MFA becomes active."


class MfaVerifyRequest(BaseModel):
    code: str = Field(..., pattern=r"^[0-9]{6}$")


class MfaVerifyResponse(BaseModel):
    enabled: bool
    recovery_codes: list[str]
    message: str = "MFA enabled. Store recovery codes offline; they are shown only once."


class RecoveryRequest(BaseModel):
    identifier: str = Field(..., min_length=5, max_length=320)
    channel: Literal["email", "sms"]
    portal: Literal["admin", "client"]
    correlation_id: str = Field(..., min_length=8, max_length=100)


class RecoveryRequestResponse(BaseModel):
    accepted: bool = True
    message: str = "If the account and recovery channel are eligible, a recovery code will be sent."


class RecoveryConfirmRequest(BaseModel):
    identifier: str = Field(..., min_length=5, max_length=320)
    portal: Literal["admin", "client"]
    code: str = Field(..., pattern=r"^[0-9]{6}$")
    new_password: str = Field(..., min_length=15, max_length=200)
    correlation_id: str = Field(..., min_length=8, max_length=100)

    @model_validator(mode="after")
    def password_not_identifier(self):
        if self.identifier.lower() in self.new_password.lower():
            raise ValueError("Password must not contain the account identifier")
        return self


class RecoveryConfirmResponse(BaseModel):
    success: bool
    message: str


class OnboardingInviteRequest(BaseModel):
    """Admin-controlled invitation for a client-scoped user."""

    email: EmailStr
    display_name: str = Field(..., min_length=2, max_length=255)
    client_id: int = Field(..., gt=0)
    portfolio_ids: list[int] = Field(default_factory=list)
    phone_e164: str | None = Field(None, pattern=r"^\+[1-9][0-9]{7,14}$")


class OnboardingInviteResponse(BaseModel):
    user_id: str
    email: EmailStr
    email_delivery_status: str
    sms_delivery_status: str | None = None
    message: str = "Invitation created. Complete the required verification steps."


class OnboardingVerifyRequest(BaseModel):
    user_id: str = Field(..., min_length=10, max_length=50)
    channel: Literal["email", "sms"]
    code: str = Field(..., pattern=r"^[0-9]{6}$")
    new_password: str = Field(..., min_length=15, max_length=200)


class OnboardingVerifyResponse(BaseModel):
    user_id: str
    email_verified: bool
    phone_verified: bool
    active: bool
    message: str


class OnboardingStatusResponse(BaseModel):
    user_id: str
    email_verified: bool
    phone_verified: bool
    active: bool
    must_change_password: bool
