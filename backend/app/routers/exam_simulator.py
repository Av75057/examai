from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.core.database import get_db
from app.routers.auth import current_user
from app.models.models import User, Task, Topic, ExamAttempt
from app.schemas.schemas import TaskOut, AnswerSubmit, AnswerResult
from app.services.error_analyzer import ErrorAnalyzer
import random

router = APIRouter(prefix="/exam-sim", tags=["exam-simulator"])

EXAM_DURATION = 235
PART1_COUNT = 12
PART2_COUNT = 6

SCORE_TABLE = {
    0: 0, 1: 5, 2: 9, 3: 14, 4: 18, 5: 23, 6: 27, 7: 31, 8: 34,
    9: 37, 10: 39, 11: 41, 12: 43, 13: 45, 14: 47, 15: 49, 16: 51,
    17: 53, 18: 55, 19: 57, 20: 59, 21: 61, 22: 63, 23: 65,
    24: 67, 25: 69, 26: 71, 27: 73, 28: 75, 29: 77, 30: 79,
    31: 82, 32: 86,
}

_analyzer = ErrorAnalyzer()


@router.get("/start", response_model=dict)
async def start_exam(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    topics_result = await db.execute(
        select(Topic).where(Topic.id.in_(select(Task.topic_id).distinct()))
    )
    topics = topics_result.scalars().all()

    if len(topics) < 3:
        raise HTTPException(status_code=400, detail="Недостаточно тем в банке задач")

    all_tasks: list[Task] = []
    seen_ids = set()

    for topic in topics:
        result = await db.execute(
            select(Task)
            .where(Task.topic_id == topic.id)
            .order_by(Task.difficulty)
            .limit(3)
        )
        for t in result.scalars():
            if t.id not in seen_ids:
                all_tasks.append(t)
                seen_ids.add(t.id)

    random.shuffle(all_tasks)

    part1 = [t for t in all_tasks if t.difficulty < 0.7][:PART1_COUNT]
    part2_candidates = [t for t in all_tasks if t.difficulty >= 0.5 and t.id not in {t.id for t in part1}]
    part2 = part2_candidates[:PART2_COUNT]

    if len(part1) < PART1_COUNT:
        remaining = [t for t in all_tasks if t.id not in {tt.id for tt in part1}]
        part1.extend(remaining[:PART1_COUNT - len(part1)])

    if len(part2) < PART2_COUNT:
        remaining = [t for t in all_tasks if t.id not in {tt.id for tt in part1} and t.id not in {tt.id for tt in part2}]
        part2.extend(remaining[:PART2_COUNT - len(part2)])

    exam_tasks = part1[:PART1_COUNT] + part2[:PART2_COUNT]

    attempt = ExamAttempt(user_id=user.id)
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "duration_minutes": EXAM_DURATION,
        "tasks": [
            TaskOut(id=t.id, topic_id=t.topic_id, content=t.content, format=t.format, difficulty=t.difficulty).model_dump()
            for t in exam_tasks
        ],
    }


@router.get("/{attempt_id}", response_model=dict)
async def get_exam_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    attempt = await db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Попытка не найдена")

    return {
        "id": attempt.id,
        "started_at": attempt.started_at.isoformat(),
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "test_score": attempt.test_score,
        "primary_score": attempt.primary_score,
    }


@router.post("/{attempt_id}/submit", response_model=AnswerResult)
async def submit_exam_answer(
    attempt_id: int,
    data: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    task = await db.get(Task, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    topic = await db.get(Topic, task.topic_id)
    is_correct = data.answer.strip().lower() == (task.answer_pattern or "").strip().lower()

    explanation = None
    ai_explanation = None
    if not is_correct:
        analysis = await _analyzer.full_analysis(
            topic_id=task.topic_id,
            topic_name=topic.name if topic else "",
            task_content=str(task.content.get("text", "")),
            student_answer=data.answer.strip(),
            correct_answer=task.answer_pattern or "",
        )
        explanation = analysis.explanation
        ai_explanation = analysis.ai_explanation

    return AnswerResult(
        is_correct=is_correct,
        correct_answer=task.answer_pattern or "",
        explanation=explanation,
        ai_explanation=ai_explanation,
    )


@router.post("/{attempt_id}/finish", response_model=dict)
async def finish_exam(
    attempt_id: int,
    answers: list[dict],
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    attempt = await db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Попытка не найдена")

    primary = sum(1 for a in answers if a.get("is_correct", False))

    attempt.primary_score = primary
    attempt.test_score = SCORE_TABLE.get(primary, 0)
    attempt.answers_data = answers
    attempt.completed_at = func.now()
    db.add(attempt)
    await db.commit()

    return {
        "attempt_id": attempt_id,
        "primary_score": primary,
        "test_score": attempt.test_score,
        "max_primary": 32,
        "total_tasks": len(answers),
        "correct": primary,
    }


def primary_to_test(primary: int) -> int:
    return SCORE_TABLE.get(primary, 0)
