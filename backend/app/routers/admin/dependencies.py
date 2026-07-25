from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.services.admin_auth import decode_token
from app.models.admin_models import AdminUser

security = HTTPBearer()


async def get_current_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminUser:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        admin_id = int(payload["sub"])
        result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
        admin = result.scalar_one_or_none()
        if not admin or not admin.is_active:
            raise HTTPException(status_code=401, detail="Admin not found or inactive")
        return admin
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(*roles: str):
    async def role_checker(admin: Annotated[AdminUser, Depends(get_current_admin)]):
        if admin.role.value not in roles:
            raise HTTPException(status_code=403, detail=f"Role {admin.role.value} not allowed")
        return admin
    return role_checker


def require_any_content():
    return require_role("super_admin", "content_manager")


def require_any_ai():
    return require_role("super_admin", "ai_moderator")


def require_any_user_mgmt():
    return require_role("super_admin", "support")


def require_any_billing():
    return require_role("super_admin")


def require_any_analyst():
    return require_role("super_admin", "analyst", "content_manager", "ai_moderator")


def log_admin_action(db: AsyncSession, admin_id: int, action: str, resource: str, **kwargs):
    from app.services.admin_auth import write_audit_log
    return write_audit_log(db, admin_id, action, resource, **kwargs)
