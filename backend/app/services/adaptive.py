from dataclasses import dataclass
from typing import Optional
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.models import Task, Mastery, Answer, Topic, Session, ErrorLog, TopicGrade
from app.services.repetition import SpacedRepetitionScheduler

EGE_WEIGHTS: dict[str, float] = {}


@dataclass
class TaskSelection:
    task: Task
    priority: float


class AdaptiveEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_mastery(self, user_id: int, topic_id: int) -> Mastery:
        result = await self.db.execute(
            select(Mastery).where(
                Mastery.user_id == user_id,
                Mastery.topic_id == topic_id,
            )
        )
        mastery = result.scalar_one_or_none()
        if not mastery:
            mastery = Mastery(user_id=user_id, topic_id=topic_id)
            self.db.add(mastery)
            await self.db.commit()
            await self.db.refresh(mastery)
        return mastery

    async def last_n_answers(self, user_id: int, topic_id: int, n: int = 3):
        result = await self.db.execute(
            select(Answer)
            .join(Session, Answer.session_id == Session.id)
            .join(Task, Answer.task_id == Task.id)
            .where(
                and_(
                    Session.user_id == user_id,
                    Task.topic_id == topic_id,
                )
            )
            .order_by(Answer.created_at.desc())
            .limit(n)
        )
        return result.scalars().all()

    async def next_task(self, user_id: int, topic_id: int, exclude_ids: set[int] | None = None) -> Optional[Task]:
        mastery = await self.get_or_create_mastery(user_id, topic_id)
        score = mastery.score

        recent = await self.last_n_answers(user_id, topic_id, n=3)
        if recent and all(a.is_correct for a in recent):
            target_difficulty = min(score + 0.1, 1.0)
        elif recent and all(not a.is_correct for a in recent):
            target_difficulty = max(score - 0.15, 0.1)
        else:
            target_difficulty = score

        query = select(Task).where(
            Task.topic_id == topic_id,
            func.abs(Task.difficulty - target_difficulty) < 0.15,
        )
        if exclude_ids:
            query = query.where(Task.id.notin_(exclude_ids))
        query = query.order_by(func.abs(Task.difficulty - target_difficulty)).limit(3)

        result = await self.db.execute(query)
        candidates = result.scalars().all()
        if candidates:
            return random.choice(candidates)
        return None

    async def update_mastery(self, user_id: int, topic_id: int, is_correct: bool):
        mastery = await self.get_or_create_mastery(user_id, topic_id)
        mastery.total_attempts += 1
        if is_correct:
            mastery.correct_attempts += 1
        alpha = 0.1 if mastery.total_attempts < 10 else 0.05
        mastery.score = (1 - alpha) * mastery.score + alpha * (1.0 if is_correct else 0.0)
        await self.db.commit()

    async def get_topics_ranked(self, user_id: int, exclude_topics: set[int] | None = None, grade: int | None = None):
        query = select(Topic).where(
            Topic.id.in_(select(Task.topic_id).distinct())
        )
        if grade:
            query = query.where(
                Topic.id.in_(
                    select(TopicGrade.topic_id).where(TopicGrade.grade <= grade)
                )
            )
        result = await self.db.execute(query)
        ranked = []
        for topic in result.scalars().all():
            if exclude_topics and topic.id in exclude_topics:
                continue
            mastery = await self.get_or_create_mastery(user_id, topic.id)
            priority = (1 - mastery.score) * topic.ege_weight
            ranked.append((topic.id, priority))
        ranked.sort(key=lambda x: -x[1])
        return ranked

    async def select_next_topic(self, user_id: int, exclude_topics: set[int] | None = None) -> Optional[int]:
        ranked = await self.get_topics_ranked(user_id, exclude_topics)
        if not ranked:
            return None
        return ranked[0][0]

    async def generate_daily_session(self, user_id: int, task_count: int = 10, review_count: int = 3, grade: int | None = None):
        tasks = []
        exclude_task_ids: set[int] = set()

        scheduler = SpacedRepetitionScheduler(self.db)
        due_reviews = await scheduler.get_due_reviews(user_id, review_count)

        for review_log in due_reviews:
            if len(tasks) >= review_count:
                break
            task = await self.db.get(Task, review_log.task_id)
            if task and task.id not in exclude_task_ids:
                tasks.append(task)
                exclude_task_ids.add(task.id)

        remaining = task_count - len(tasks)

        ranked = await self.get_topics_ranked(user_id, grade=grade)

        while len(tasks) < task_count:
            started_with = len(tasks)
            for topic_id, _ in ranked:
                if len(tasks) >= task_count:
                    break
                task = await self.next_task(user_id, topic_id, exclude_ids=exclude_task_ids)
                if task:
                    tasks.append(task)
                    exclude_task_ids.add(task.id)
            if len(tasks) == started_with:
                break

        return tasks
