from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.models import Topic, Task, TaskTemplate
from app.models.admin_models import AdminUser
from app.routers.admin.dependencies import get_current_admin, require_any_content, log_admin_action
from app.services.task_generator import TaskGenerator
from app.services.templates import TEMPLATES

router = APIRouter(prefix="/admin/topics", tags=["admin-topics"])


class TopicCreate(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    ege_weight: float = Field(1.0, ge=0, le=10)
    parent_id: int | None = None
    order: int = 0
    is_active: bool = True


class TopicUpdate(BaseModel):
    name: str | None = None
    ege_weight: float | None = None
    parent_id: int | None = None
    order: int | None = None
    is_active: bool | None = None


class TemplateCreate(BaseModel):
    template_id: str
    topic_code: str
    content_text: str
    difficulty_base: float = 0.5
    format: str = "numeric"
    generate_params_code: str | None = None
    compute_answer_code: str | None = None


@router.get("/", response_model=list[dict])
async def list_topics(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    result = await db.execute(
        select(Topic).order_by(Topic.id)
    )
    topics = result.scalars().all()
    return [
        {
            "id": t.id,
            "code": t.code,
            "name": t.name,
            "ege_weight": t.ege_weight,
            "is_active": True,
        }
        for t in topics
    ]


@router.post("/", response_model=dict)
async def create_topic(
    data: TopicCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    existing = await db.execute(select(Topic).where(Topic.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Тема с таким кодом уже существует")

    topic = Topic(
        code=data.code,
        name=data.name,
        ege_weight=data.ege_weight,
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)

    await log_admin_action(db, admin.id, "create", "topic", resource_id=str(topic.id),
                           new_value={"code": topic.code, "name": topic.name})
    return {"id": topic.id, "code": topic.code, "name": topic.name, "ege_weight": topic.ege_weight}


@router.put("/{topic_id}", response_model=dict)
async def update_topic(
    topic_id: int,
    data: TopicUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    old_data = {"name": topic.name, "ege_weight": topic.ege_weight}
    if data.name is not None:
        topic.name = data.name
    if data.ege_weight is not None:
        topic.ege_weight = data.ege_weight

    await db.commit()

    await log_admin_action(db, admin.id, "update", "topic", resource_id=str(topic.id),
                           old_value=old_data, new_value=data.model_dump(exclude_none=True))
    return {"id": topic.id, "code": topic.code, "name": topic.name, "ege_weight": topic.ege_weight}


@router.delete("/{topic_id}")
async def archive_topic(
    topic_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    task_count = await db.execute(select(func.count(Task.id)).where(Task.topic_id == topic_id))
    if task_count.scalar() > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить тему, к которой привязаны задачи")

    await db.delete(topic)
    await db.commit()
    await log_admin_action(db, admin.id, "delete", "topic", resource_id=str(topic_id))
    return {"status": "deleted"}


@router.get("/{topic_id}/tasks", response_model=list[dict])
async def topic_tasks(
    topic_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    result = await db.execute(
        select(Task).where(Task.topic_id == topic_id).limit(50)
    )
    tasks = result.scalars().all()
    return [
        {"id": t.id, "content": t.content, "difficulty": t.difficulty, "format": t.format, "answer_pattern": t.answer_pattern}
        for t in tasks
    ]
