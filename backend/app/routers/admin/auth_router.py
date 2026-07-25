from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.admin_models import AdminUser, AdminRole
from app.routers.admin.dependencies import get_current_admin, require_role
from app.services.admin_auth import (
    authenticate_admin, create_admin, create_access_token,
    create_refresh_token, decode_token, enable_totp, confirm_totp,
)
from pydantic import BaseModel


router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    requires_2fa: bool = False
    admin: dict


class AdminCreateRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str


class TOTPVerifyRequest(BaseModel):
    code: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(data: AdminLoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    admin = await authenticate_admin(db, data.email, data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if admin.totp_enabled:
        return AdminLoginResponse(
            access_token="",
            refresh_token="",
            requires_2fa=True,
            admin={"id": admin.id, "email": admin.email, "name": admin.name},
        )
    access_token = create_access_token(admin.id, admin.role.value)
    refresh_token = create_refresh_token(admin.id)
    return AdminLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        admin={"id": admin.id, "email": admin.email, "name": admin.name, "role": admin.role.value},
    )


@router.post("/2fa/verify", response_model=dict)
async def verify_2fa(
    data: TOTPVerifyRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not admin.totp_secret:
        raise HTTPException(status_code=400, detail="2FA не настроен")
    ok = await confirm_totp(db, admin.id, data.code)
    if not ok:
        raise HTTPException(status_code=401, detail="Неверный код 2FA")
    return {"status": "ok"}


@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        admin_id = int(payload["sub"])
        access_token = create_access_token(admin_id, "")
        return {"access_token": access_token}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/me")
async def admin_me(admin: Annotated[AdminUser, Depends(get_current_admin)]):
    return {
        "id": admin.id,
        "email": admin.email,
        "name": admin.name,
        "role": admin.role.value,
        "totp_enabled": admin.totp_enabled,
    }


@router.post("/2fa/setup")
async def setup_2fa(admin: Annotated[AdminUser, Depends(get_current_admin)], db: Annotated[AsyncSession, Depends(get_db)]):
    secret = await enable_totp(db, admin.id)
    return {"secret": secret, "qr_url": f"otpauth://totp/ExamAI:{admin.email}?secret={secret}&issuer=ExamAI"}


@router.post("/2fa/confirm")
async def confirm_2fa_setup(
    data: TOTPVerifyRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ok = await confirm_totp(db, admin.id, data.code)
    if not ok:
        raise HTTPException(status_code=400, detail="Неверный код")
    return {"status": "2fa_enabled"}
