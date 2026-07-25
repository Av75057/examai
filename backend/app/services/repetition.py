from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ErrorLog

REVIEW_INTERVALS = [1, 3, 7, 14, 30]


class SpacedRepetitionScheduler:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def schedule_review(self, user_id: int, task_id: int, error_type: str):
        log = ErrorLog(
            user_id=user_id,
            task_id=task_id,
            error_type=error_type,
            review_stage=0,
            next_review_at=datetime.utcnow() + timedelta(days=REVIEW_INTERVALS[0]),
        )
        self.db.add(log)
        await self.db.commit()
        return log

    async def advance_stage(self, error_log_id: int, mastered: bool):
        result = await self.db.execute(
            __import__("sqlalchemy").select(ErrorLog).where(ErrorLog.id == error_log_id)
        )
        log = result.scalar_one_or_none()
        if not log:
            return None

        if mastered or log.review_stage >= len(REVIEW_INTERVALS) - 1:
            log.mastered = True
        else:
            log.review_stage += 1
            interval = REVIEW_INTERVALS[log.review_stage]
            log.next_review_at = datetime.utcnow() + timedelta(days=interval)

        await self.db.commit()
        return log

    async def get_due_reviews(self, user_id: int, limit: int = 3):
        result = await self.db.execute(
            __import__("sqlalchemy").select(ErrorLog)
            .where(
                ErrorLog.user_id == user_id,
                ErrorLog.mastered == False,
                ErrorLog.next_review_at <= datetime.utcnow(),
            )
            .order_by(ErrorLog.next_review_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
