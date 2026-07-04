from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from excel_consumption_service.models.base import Base, IdentifierMixin, TimestampMixin


class Role(IdentifierMixin, TimestampMixin, Base):
    """Reusable RBAC role definition."""

    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)

    assignments = relationship("UserRoleAssignment", back_populates="role")


class User(IdentifierMixin, TimestampMixin, Base):
    """Human account that authenticates into the platform."""

    __tablename__ = "users"

    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_assignments = relationship("UserRoleAssignment", back_populates="user")


class UserRoleAssignment(IdentifierMixin, TimestampMixin, Base):
    """Assign one role to one user, optionally within a tenant scope."""

    __tablename__ = "user_role_assignments"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), index=True)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.id"), index=True)

    user = relationship("User", back_populates="role_assignments")
    role = relationship("Role", back_populates="assignments")
