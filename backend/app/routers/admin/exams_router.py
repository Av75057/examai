from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.models import Topic, Task, ExamAttempt
from app.models.admin_models import AdminUser
from app.routers.admin.dependencies import get_current_admin, require_any_content, log_admin_action

router = APIRouter(prefix="/admin/exams", tags=["admin-exams"])


class ExamCreate(BaseModel):
    title: str
    duration_min: int = 235
    structure: dict = Field(default_factory=lambda: {"part1": 12, "part2": 6})
    auto_select: bool = True
    difficulty_range: list[float] = [0.3, 0.95]


exams_store: list[dict] = []


@router.get("/", response_model=dict)
async def list_exams(
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    return {"items": exams_store, "total": len(exams_store)}


@router.post("/", response_model=dict)
async def create_exam(
    data: ExamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    exam = {
        "id": len(exams_store) + 1,
        "title": data.title,
        "duration_min": data.duration_min,
        "structure": data.structure,
        "status": "draft",
        "created_by": admin.name,
    }
    exams_store.append(exam)

    await log_admin_action(db, admin.id, "create", "exam",
                           resource_id=str(exam["id"]),
                           new_value=data.model_dump())
    return exam


@router.put("/{exam_id}", response_model=dict)
async def update_exam(
    exam_id: int,
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    for e in exams_store:
        if e["id"] == exam_id:
            e.update(data)
            await log_admin_action(db, admin.id, "update", "exam", resource_id=str(exam_id))
            return e
    raise HTTPException(status_code=404, detail="Экзамен не найден")


@router.post("/{exam_id}/publish", response_model=dict)
async def publish_exam(
    exam_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    for e in exams_store:
        if e["id"] == exam_id:
            e["status"] = "active"
            await log_admin_action(db, admin.id, "publish", "exam", resource_id=str(exam_id))
            return e
    raise HTTPException(status_code=404, detail="Экзамен не найден")


@router.get("/{exam_id}/results", response_model=dict)
async def exam_results(
    exam_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_content())],
):
    result = await db.execute(
        select(ExamAttempt).order_by(ExamAttempt.started_at.desc()).limit(100)
    )
    attempts = result.scalars().all()
    return {
        "exam_id": exam_id,
        "total_attempts": len(attempts),
        "items": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "test_score": a.test_score,
                "primary_score": a.primary_score,
                "completed": a.completed_at is not None,
            }
            for a in attempts
        ],
    }
