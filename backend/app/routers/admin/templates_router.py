from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.models import Topic, Task, TaskTemplate
from app.models.admin_models import AdminUser, AuditLog
from app.routers.admin.dependencies import get_current_admin, require_any_content, log_admin_action
from app.services.task_generator import TaskGenerator
from app.services.templates import TEMPLATES
import random

router = APIRouter(prefix="/admin/tasks", tags=["admin-tasks"])


class TemplateCreate(BaseModel):
    topic_id: int
    title: str = ""
    content_template: dict
    solution_template: dict
    difficulty_base: float = Field(0.5, ge=0.1, le=1.0)
    format: str = "numeric"
    param_ranges: dict = {}
    answer_formula: str = ""


class TemplateUpdate(BaseModel):
    title: str | None = None
    content_template: dict | None = None
    solution_template: dict | None = None
    difficulty_base: float | None = None
    format: str | None = None
    param_ranges: dict | None = None
    status: str | None = None


@router.get("/templates", response_model=dict)
async def list_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
    page: int = Query(1, ge=1),
    per_page: int = Query(25, le=100),
    topic_id: int | None = None,
    difficulty_min: float | None = None,
    difficulty_max: float | None = None,
):
    query = select(TaskTemplate)
    if topic_id:
        query = query.where(TaskTemplate.topic_id == topic_id)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    result = await db.execute(
        query.offset((page - 1) * per_page).limit(per_page)
    )
    templates = result.scalars().all()

    items = []
    for tmpl in templates:
        task_count = await db.execute(
            select(func.count(Task.id)).where(Task.template_id == tmpl.id)
        )
        topic = await db.get(Topic, tmpl.topic_id)
        items.append({
            "id": tmpl.id,
            "topic_id": tmpl.topic_id,
            "topic_name": topic.name if topic else "",
            "content_template": tmpl.content_template,
            "solution_template": tmpl.solution_template,
            "difficulty_base": tmpl.difficulty_base,
            "task_count": task_count.scalar(),
        })

    return {"items": items, "total": total, "page": page, "per_page": per_page}


@router.post("/templates", response_model=dict)
async def create_template(
    data: TemplateCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    topic = await db.get(Topic, data.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    tmpl = TaskTemplate(
        topic_id=data.topic_id,
        content_template=data.content_template,
        solution_template=data.solution_template,
        param_ranges=data.param_ranges or {"type": "dynamic"},
        difficulty_base=data.difficulty_base,
    )
    db.add(tmpl)
    await db.commit()
    await db.refresh(tmpl)

    await log_admin_action(db, admin.id, "create", "task_template",
                           resource_id=str(tmpl.id),
                           new_value={"topic_id": data.topic_id})

    return {"id": tmpl.id, "topic_id": tmpl.topic_id, "difficulty_base": tmpl.difficulty_base}


@router.get("/templates/{template_id}", response_model=dict)
async def get_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    tmpl = await db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    topic = await db.get(Topic, tmpl.topic_id)
    return {
        "id": tmpl.id,
        "topic_id": tmpl.topic_id,
        "topic_name": topic.name if topic else "",
        "content_template": tmpl.content_template,
        "solution_template": tmpl.solution_template,
        "difficulty_base": tmpl.difficulty_base,
        "param_ranges": tmpl.param_ranges,
    }


@router.put("/templates/{template_id}", response_model=dict)
async def update_template(
    template_id: int,
    data: TemplateUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    tmpl = await db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    old_data = {"difficulty_base": tmpl.difficulty_base}
    if data.content_template is not None:
        tmpl.content_template = data.content_template
    if data.solution_template is not None:
        tmpl.solution_template = data.solution_template
    if data.difficulty_base is not None:
        tmpl.difficulty_base = data.difficulty_base
    if data.param_ranges is not None:
        tmpl.param_ranges = data.param_ranges

    await db.commit()
    await log_admin_action(db, admin.id, "update", "task_template",
                           resource_id=str(template_id),
                           old_value=old_data, new_value=data.model_dump(exclude_none=True))

    return {"id": tmpl.id, "status": "updated"}


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    tmpl = await db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    await db.delete(tmpl)
    await db.commit()
    await log_admin_action(db, admin.id, "delete", "task_template", resource_id=str(template_id))
    return {"status": "deleted"}


@router.post("/templates/{template_id}/generate", response_model=dict)
async def generate_variations(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
    count: int = Query(5, ge=1, le=20),
):
    tmpl = await db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    generator = TaskGenerator(TEMPLATES)
    previews = []
    for _ in range(count):
        try:
            gen = generator.generate_variations("quad_001", 1)[0]
            previews.append({
                "content": gen.content,
                "answer": gen.answer,
                "difficulty": gen.difficulty,
            })
        except Exception:
            pass

    return {"template_id": template_id, "previews": previews[:3]}


@router.post("/templates/{template_id}/add-variations")
async def add_variations_to_bank(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
    count: int = Query(5, ge=1, le=50),
):
    tmpl = await db.get(TaskTemplate, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    generator = TaskGenerator(TEMPLATES)
    added = 0
    for _ in range(count):
        try:
            gen = generator.generate_variations("quad_001", 1)[0]
            task = Task(
                topic_id=tmpl.topic_id,
                template_id=tmpl.id,
                difficulty=gen.difficulty,
                format=gen.format,
                content=gen.content,
                solution=gen.solution,
                answer_pattern=gen.answer,
            )
            db.add(task)
            added += 1
        except Exception:
            pass

    await db.commit()
    await log_admin_action(db, admin.id, "generate_tasks", "task_template",
                           resource_id=str(template_id),
                           new_value={"count": added})

    return {"template_id": template_id, "variations_added": added}


@router.get("/tasks", response_model=dict)
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
    page: int = Query(1, ge=1),
    per_page: int = Query(25, le=100),
    topic_id: int | None = None,
    template_id: int | None = None,
):
    query = select(Task)
    if topic_id:
        query = query.where(Task.topic_id == topic_id)
    if template_id:
        query = query.where(Task.template_id == template_id)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    result = await db.execute(
        query.order_by(Task.id).offset((page - 1) * per_page).limit(per_page)
    )
    tasks = result.scalars().all()

    return {
        "items": [
            {
                "id": t.id,
                "topic_id": t.topic_id,
                "template_id": t.template_id,
                "difficulty": t.difficulty,
                "format": t.format,
                "content": t.content,
                "answer_pattern": t.answer_pattern,
            }
            for t in tasks
        ],
        "total": total,
        "page": page,
    }
