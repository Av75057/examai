import hashlib
import hmac
import base64
import time
import struct
from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.config import get_settings
from app.models.admin_models import AdminUser, AuditLog

settings = get_settings()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 30
ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_HOURS = 8


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    return bcrypt.verify(password, hash_)


def generate_totp_secret() -> str:
    return base64.b32encode(hashlib.sha256(str(time.time()).encode()).digest()).decode()[:32]


def generate_totp_code(secret: str, interval: int = 30) -> str:
    key = base64.b32decode(secret.upper() + "=" * ((8 - len(secret)) % 8))
    counter = int(time.time() // interval)
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = (struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF) % 1000000
    return str(code).zfill(6)


def verify_totp(secret: str, code: str) -> bool:
    return generate_totp_code(secret) == code


def create_access_token(admin_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(admin_id), "role": role, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(admin_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_HOURS)
    payload = {"sub": str(admin_id), "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


async def authenticate_admin(db: AsyncSession, email: str, password: str) -> AdminUser | None:
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        return None

    if admin.locked_until and admin.locked_until > datetime.utcnow():
        return None

    if not verify_password(password, admin.password_hash):
        admin.failed_login_attempts += 1
        if admin.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            admin.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
        await db.commit()
        return None

    admin.failed_login_attempts = 0
    admin.locked_until = None
    admin.last_login_at = datetime.utcnow()
    await db.commit()
    return admin


async def create_admin(
    db: AsyncSession,
    email: str,
    password: str,
    name: str,
    role: str,
) -> AdminUser:
    existing = await db.execute(select(AdminUser).where(AdminUser.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Администратор с таким email уже существует")

    admin = AdminUser(
        email=email,
        password_hash=hash_password(password),
        name=name,
        role=role,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


async def enable_totp(db: AsyncSession, admin_id: int) -> str:
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one()
    secret = generate_totp_secret()
    admin.totp_secret = secret
    admin.totp_enabled = False
    await db.commit()
    return secret


async def confirm_totp(db: AsyncSession, admin_id: int, code: str) -> bool:
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one()
    if not admin.totp_secret:
        return False
    if verify_totp(admin.totp_secret, code):
        admin.totp_enabled = True
        await db.commit()
        return True
    return False


async def write_audit_log(
    db: AsyncSession,
    admin_id: int,
    action: str,
    resource: str,
    resource_id: str | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    ip_address: str | None = None,
):
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()
