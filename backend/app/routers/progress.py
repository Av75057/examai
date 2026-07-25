from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from app.core.database import get_db
from app.routers.auth import current_user
from app.models.models import User, Session, Answer, Mastery, Topic

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/streak", response_model=dict)
async def get_streak(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(func.date(Session.started_at))
        .where(Session.user_id == user.id)
        .distinct()
        .order_by(func.date(Session.started_at).desc())
    )
    active_dates = {row[0] for row in result.all()}

    today = datetime.utcnow().date()
    streak = 0
    for i in range(365):
        day = today - timedelta(days=i)
        if day in active_dates:
            streak += 1
        else:
            break

    return {"streak": streak, "active_dates": sorted(active_dates, reverse=True)[:30]}


@router.get("/overview", response_model=dict)
async def progress_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    total_answers = await db.execute(
        select(func.count(Answer.id)).where(
            Answer.session.has(id=select(Session.id).where(Session.user_id == user.id))
        )
    )

    correct_answers = await db.execute(
        select(func.count(Answer.id)).where(
            Answer.is_correct == True,
            Answer.session.has(id=select(Session.id).where(Session.user_id == user.id))
        )
    )

    total_sessions = await db.execute(
        select(func.count(Session.id)).where(Session.user_id == user.id)
    )

    result = await db.execute(
        select(Mastery.score).where(Mastery.user_id == user.id)
    )
    scores = [r[0] for r in result.all()]
    avg_mastery = sum(scores) / len(scores) if scores else 0

    topics_done = await db.execute(
        select(func.count(Mastery.id)).where(
            Mastery.user_id == user.id,
            Mastery.score >= 0.7,
        )
    )

    return {
        "total_answers": total_answers.scalar() or 0,
        "correct_answers": correct_answers.scalar() or 0,
        "accuracy": round(
            (correct_answers.scalar() or 0) / max((total_answers.scalar() or 1), 1) * 100, 1
        ),
        "total_sessions": total_sessions.scalar() or 0,
        "avg_mastery": round(avg_mastery * 100, 1),
        "topics_mastered": topics_done.scalar() or 0,
        "total_topics": 24,
    }
