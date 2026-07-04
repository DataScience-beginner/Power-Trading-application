from sqlalchemy import select
from sqlalchemy.orm import Session

from excel_consumption_service.core.security import hash_password
from excel_consumption_service.models.auth import Role, User, UserRoleAssignment
from excel_consumption_service.models.tenant import Site, Tenant


def seed_reference_data(db: Session) -> None:
    """Seed a minimal but realistic tenant, site, role, and user setup for development."""

    tenant = db.scalar(select(Tenant).where(Tenant.code == "demo-tenant"))
    if tenant is None:
        tenant = Tenant(
            code="demo-tenant",
            name="Demo Tenant",
            deployment_mode="vendor-hosted",
        )
        db.add(tenant)
        db.flush()

    site = db.scalar(
        select(Site).where(Site.tenant_id == tenant.id, Site.code == "cuddalore-main")
    )
    if site is None:
        db.add(
            Site(
                tenant_id=tenant.id,
                code="cuddalore-main",
                name="Cuddalore Main Site",
                timezone="Asia/Kolkata",
            )
        )

    role_definitions = {
        "platform_admin": "Platform-level administrator with operational oversight.",
        "tenant_admin": "Tenant-level administrator with client management powers.",
        "client_viewer": "Client user who can upload and review tenant data.",
    }
    roles: dict[str, Role] = {}
    for code, description in role_definitions.items():
        role = db.scalar(select(Role).where(Role.code == code))
        if role is None:
            role = Role(code=code, name=code.replace("_", " ").title(), description=description)
            db.add(role)
            db.flush()
        roles[code] = role

    user_definitions = [
        {
            "email": "admin@demo.local",
            "full_name": "Platform Admin",
            "password": "Admin123!",
            "role_code": "platform_admin",
        },
        {
            "email": "tenantadmin@demo.local",
            "full_name": "Tenant Admin",
            "password": "Tenant123!",
            "role_code": "tenant_admin",
        },
        {
            "email": "client@demo.local",
            "full_name": "Client Viewer",
            "password": "Client123!",
            "role_code": "client_viewer",
        },
    ]

    for definition in user_definitions:
        user = db.scalar(select(User).where(User.email == definition["email"]))
        if user is None:
            user = User(
                tenant_id=tenant.id,
                email=definition["email"],
                full_name=definition["full_name"],
                password_hash=hash_password(definition["password"]),
                is_active=True,
            )
            db.add(user)
            db.flush()

        assignment = db.scalar(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == user.id,
                UserRoleAssignment.role_id == roles[definition["role_code"]].id,
            )
        )
        if assignment is None:
            db.add(
                UserRoleAssignment(
                    user_id=user.id,
                    role_id=roles[definition["role_code"]].id,
                    tenant_id=tenant.id,
                )
            )

    db.commit()
