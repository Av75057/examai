from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.routers.auth import current_user
from app.models.models import User, Session, Answer, Task, Mastery, Topic
from app.schemas.schemas import TaskOut, AnswerSubmit, AnswerResult
from app.services.error_analyzer import ErrorAnalyzer
import random

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

DIAGNOSTIC_SIZE = 20

_analyzer = ErrorAnalyzer()


@router.get("/start", response_model=list[TaskOut])
async def start_diagnostic(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    all_topics = await db.execute(
        select(Topic).where(Topic.id.in_(select(Task.topic_id).distinct()))
    )
    topics = all_topics.scalars().all()

    if not topics:
        raise HTTPException(status_code=400, detail="Нет доступных тем")

    session = Session(user_id=user.id, session_type="diagnostic")
    db.add(session)
    await db.commit()

    tasks = []
    seen_ids = set()

    for topic in topics[:DIAGNOSTIC_SIZE]:
        result = await db.execute(
            select(Task)
            .where(Task.topic_id == topic.id)
            .order_by(func.random())
            .limit(1)
        )
        task = result.scalar_one_or_none()
        if task and task.id not in seen_ids:
            tasks.append(task)
            seen_ids.add(task.id)

    if len(tasks) < 5:
        result = await db.execute(
            select(Task).order_by(func.random()).limit(DIAGNOSTIC_SIZE)
        )
        tasks = result.scalars().all()

    random.shuffle(tasks)
    tasks = tasks[:DIAGNOSTIC_SIZE]

    return [
        TaskOut(id=t.id, topic_id=t.topic_id, content=t.content, format=t.format, difficulty=t.difficulty)
        for t in tasks
    ]


@router.post("/submit", response_model=AnswerResult)
async def submit_diagnostic_answer(
    data: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    task = await db.get(Task, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    topic = await db.get(Topic, task.topic_id)

    student_answer = data.answer.strip()
    correct_answer = (task.answer_pattern or "").strip()
    is_correct = student_answer.lower() == correct_answer.lower()

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user.id, Session.session_type == "diagnostic", Session.completed_at.is_(None))
        .order_by(Session.started_at.desc())
        .limit(1)
    )
    session = result.scalar_one_or_none()
    session_id = session.id if session else 1

    answer = Answer(
        session_id=session_id,
        task_id=data.task_id,
        student_answer=student_answer,
        is_correct=is_correct,
        time_spent_seconds=data.time_spent_seconds,
    )
    db.add(answer)
    await db.commit()

    explanation = None
    ai_explanation = None
    if not is_correct:
        analysis = await _analyzer.full_analysis(
            topic_id=task.topic_id,
            topic_name=topic.name if topic else "",
            task_content=str(task.content.get("text", "")),
            student_answer=student_answer,
            correct_answer=correct_answer,
        )
        explanation = analysis.explanation
        ai_explanation = analysis.ai_explanation

    return AnswerResult(
        is_correct=is_correct,
        correct_answer=correct_answer,
        explanation=explanation,
        ai_explanation=ai_explanation,
    )


@router.post("/complete", response_model=dict)
async def complete_diagnostic(
    results: list[dict],
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    if len(results) < 5:
        raise HTTPException(status_code=400, detail="Слишком мало ответов")

    topic_results: dict[int, list[bool]] = {}
    for r in results:
        task_id = r.get("task_id")
        is_correct = r.get("is_correct", False)
        task = await db.get(Task, task_id)
        if task:
            topic_results.setdefault(task.topic_id, []).append(is_correct)

    for topic_id, corrects in topic_results.items():
        accuracy = sum(corrects) / len(corrects) if corrects else 0.5
        existing = await db.execute(
            select(Mastery).where(
                Mastery.user_id == user.id,
                Mastery.topic_id == topic_id,
            )
        )
        mastery = existing.scalar_one_or_none()
        if mastery:
            mastery.score = 0.3 + 0.4 * accuracy
            mastery.total_attempts = len(corrects)
            mastery.correct_attempts = sum(corrects)
        else:
            mastery = Mastery(
                user_id=user.id,
                topic_id=topic_id,
                score=0.3 + 0.4 * accuracy,
                total_attempts=len(corrects),
                correct_attempts=sum(corrects),
            )
            db.add(mastery)

    await db.commit()

    return {
        "status": "completed",
        "topics_assessed": len(topic_results),
        "message": "Диагностика завершена. Ваш уровень определён.",
    }
