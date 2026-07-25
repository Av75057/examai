from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.admin_models import AdminUser
from app.routers.admin.dependencies import get_current_admin, require_role, log_admin_action

router = APIRouter(prefix="/admin/adaptive", tags=["admin-adaptive"])

ADAPTIVE_DEFAULTS = {
    "session_length": 12,
    "diagnostic_length": 20,
    "mastery_threshold": 0.85,
    "difficulty_step_up": 0.10,
    "difficulty_step_down": 0.15,
    "streak_for_level_up": 3,
    "streak_for_level_down": 2,
    "new_topic_ratio": 0.2,
    "review_ratio": 0.3,
    "max_session_time_min": 30,
    "irt_model": "1PL",
    "ability_update_rate": 0.3,
}

_current_settings = dict(ADAPTIVE_DEFAULTS)


@router.get("/settings", response_model=dict)
async def get_settings(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
):
    return {
        "settings": _current_settings,
        "defaults": ADAPTIVE_DEFAULTS,
    }


@router.put("/settings", response_model=dict)
async def update_settings(
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_role("super_admin"))],
):
    old = dict(_current_settings)
    for key, value in data.items():
        if key in ADAPTIVE_DEFAULTS:
            _current_settings[key] = value

    await log_admin_action(db, admin.id, "update", "adaptive_settings",
                           old_value=old, new_value=_current_settings)
    return {"status": "updated", "settings": _current_settings}


@router.get("/monitor", response_model=dict)
async def monitor(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
):
    return {
        "students_by_mastery": {"low": 10, "medium": 30, "high": 20},
        "avg_tasks_to_mastery": {"linear_equations": 12, "quadratic_equations": 18},
        "stuck_rate": 0.05,
        "anomalies": [],
    }
