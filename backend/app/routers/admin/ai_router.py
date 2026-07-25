from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.admin_models import AdminUser
from app.routers.admin.dependencies import get_current_admin, require_role, require_any_content, log_admin_action

router = APIRouter(prefix="/admin/ai", tags=["admin-ai"])

ERROR_PATTERNS_STORE: list[dict] = [
    {
        "id": 1,
        "topic_id": 2,
        "name": "Забыл разделить на 2a",
        "detection_rule": {"type": "regex", "pattern": "(-b.*sqrt)"},
        "explanation_template": "Вы нашли корни, но забыли разделить на 2a",
        "is_active": True,
        "hit_count": 142,
    },
    {
        "id": 2,
        "topic_id": 1,
        "name": "Ошибка в знаке",
        "detection_rule": {"type": "condition", "field": "sign_mismatch"},
        "explanation_template": "Ошибка в знаке при переносе слагаемого",
        "is_active": True,
        "hit_count": 98,
    },
    {
        "id": 3,
        "topic_id": 7,
        "name": "Свойство логарифма",
        "detection_rule": {"type": "condition", "field": "log_property_wrong"},
        "explanation_template": "Проверьте свойство: log(a*b) = log(a) + log(b)",
        "is_active": True,
        "hit_count": 67,
    },
]

MODERATION_QUEUE: list[dict] = []


class ErrorPatternCreate(BaseModel):
    topic_id: int
    name: str
    detection_rule: dict
    explanation_template: str
    is_active: bool = True


class ModerationAction(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|edit)$")
    edited_text: str | None = None


@router.get("/error-patterns", response_model=dict)
async def list_error_patterns(
    admin: Annotated[AdminUser, Depends(require_any_content())],
    topic_id: int | None = None,
):
    items = ERROR_PATTERNS_STORE
    if topic_id:
        items = [p for p in items if p["topic_id"] == topic_id]
    return {"items": items, "total": len(items)}


@router.post("/error-patterns", response_model=dict)
async def create_error_pattern(
    data: ErrorPatternCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    new_id = max((p["id"] for p in ERROR_PATTERNS_STORE), default=0) + 1
    pattern = {
        "id": new_id,
        "topic_id": data.topic_id,
        "name": data.name,
        "detection_rule": data.detection_rule,
        "explanation_template": data.explanation_template,
        "is_active": data.is_active,
        "hit_count": 0,
    }
    ERROR_PATTERNS_STORE.append(pattern)
    await log_admin_action(db, admin.id, "create", "error_pattern",
                           resource_id=str(new_id), new_value=data.model_dump())
    return pattern


@router.put("/error-patterns/{pattern_id}", response_model=dict)
async def update_error_pattern(
    pattern_id: int,
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    for p in ERROR_PATTERNS_STORE:
        if p["id"] == pattern_id:
            p.update(data)
            await log_admin_action(db, admin.id, "update", "error_pattern", resource_id=str(pattern_id))
            return p
    raise HTTPException(status_code=404, detail="Паттерн не найден")


@router.get("/moderation/queue", response_model=dict)
async def moderation_queue(
    admin: Annotated[AdminUser, Depends(require_role("super_admin", "ai_moderator"))],
    page: int = Query(1),
    per_page: int = Query(20),
):
    return {
        "items": MODERATION_QUEUE,
        "total": len(MODERATION_QUEUE),
        "stats": {"pending": 0, "today_approved": 0, "today_rejected": 0},
    }


@router.post("/moderation/{item_id}/action", response_model=dict)
async def moderate_item(
    item_id: int,
    data: ModerationAction,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_role("super_admin", "ai_moderator"))],
):
    await log_admin_action(
        db, admin.id, f"moderation_{data.action}", "ai_response",
        resource_id=str(item_id),
        new_value={"action": data.action},
    )
    return {"id": item_id, "status": data.action}


@router.get("/prompts", response_model=dict)
async def list_prompts(
    admin: Annotated[AdminUser, Depends(require_role("super_admin", "ai_moderator"))],
):
    return {
        "items": [
            {
                "id": 1,
                "name": "Разбор ошибки по алгебре",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500,
                "is_active": True,
                "version": 1,
            }
        ]
    }
