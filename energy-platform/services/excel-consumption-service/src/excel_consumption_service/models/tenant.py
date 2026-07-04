from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from excel_consumption_service.models.base import Base, IdentifierMixin, TimestampMixin


class Tenant(IdentifierMixin, TimestampMixin, Base):
    """Client boundary used to isolate data and configuration."""

    __tablename__ = "tenants"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    deployment_mode: Mapped[str] = mapped_column(String(40), default="vendor-hosted")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sites = relationship("Site", back_populates="tenant")


class Site(IdentifierMixin, TimestampMixin, Base):
    """Physical or logical operating location under a tenant."""

    __tablename__ = "sites"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(160))
    timezone: Mapped[str] = mapped_column(String(80), default="UTC")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="sites")
