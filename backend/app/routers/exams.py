from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.auth import current_user
from app.models.models import User, ExamAttempt

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post("/start")
async def start_exam(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    attempt = ExamAttempt(user_id=user.id)
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return {
        "attempt_id": attempt.id,
        "duration_minutes": 235,
        "total_tasks": 18,
    }


@router.get("/history")
async def exam_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    from sqlalchemy import select

    result = await db.execute(
        select(ExamAttempt)
        .where(ExamAttempt.user_id == user.id)
        .order_by(ExamAttempt.started_at.desc())
        .limit(10)
    )
    attempts = result.scalars().all()
    return [
        {
            "id": a.id,
            "started_at": a.started_at.isoformat(),
            "primary_score": a.primary_score,
            "test_score": a.test_score,
            "completed": a.completed_at is not None,
        }
        for a in attempts
    ]
