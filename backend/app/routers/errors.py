from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.auth import current_user
from app.models.models import User, ErrorLog
from app.services.repetition import SpacedRepetitionScheduler

router = APIRouter(prefix="/errors", tags=["errors"])


@router.get("/", response_model=list[dict])
async def list_errors(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    from sqlalchemy import select

    result = await db.execute(
        select(ErrorLog)
        .where(ErrorLog.user_id == user.id)
        .order_by(ErrorLog.created_at.desc())
        .limit(50)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "task_id": log.task_id,
            "error_type": log.error_type,
            "mastered": log.mastered,
            "review_stage": log.review_stage,
            "created_at": log.created_at.isoformat(),
            "next_review_at": log.next_review_at.isoformat() if log.next_review_at else None,
        }
        for log in logs
    ]


@router.post("/{error_log_id}/review")
async def review_error(
    error_log_id: int,
    mastered: bool = False,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    scheduler = SpacedRepetitionScheduler(db)
    log = await scheduler.advance_stage(error_log_id, mastered)
    if not log:
        raise HTTPException(status_code=404, detail="Error log not found")
    return {"status": "ok", "mastered": log.mastered, "stage": log.review_stage}
