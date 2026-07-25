from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from app.core.database import get_db
from app.core.config import get_settings
from app.routers.auth import current_user
from app.models.models import User, Session, Answer, Task, Mastery, ErrorLog, Topic
from app.schemas.schemas import TaskOut, AnswerSubmit, AnswerResult
from app.services.adaptive import AdaptiveEngine
from app.services.error_analyzer import ErrorAnalyzer
from app.services.repetition import SpacedRepetitionScheduler

router = APIRouter(prefix="/tasks", tags=["tasks"])
settings = get_settings()

_analyzer = ErrorAnalyzer()


def normalize_answer(ans: str) -> str:
    """Normalize answer: comma→dot, strip spaces, lowercase"""
    return ans.strip().replace(",", ".").lower()


def answers_match(student: str, correct: str) -> bool:
    """Check if student answer matches correct answer, with numeric tolerance"""
    s = normalize_answer(student)
    c = normalize_answer(correct)
    if s == c:
        return True
    try:
        sn = float(s)
        cn = float(c)
        return abs(sn - cn) < 0.011
    except ValueError:
        return False


async def check_daily_limit(db: AsyncSession, user: User) -> int:
    if user.subscription and user.subscription.value == "premium":
        return 999
    today = datetime.utcnow().date()
    result = await db.execute(
        select(func.count(Answer.id))
        .join(Session, Answer.session_id == Session.id)
        .where(
            and_(
                Session.user_id == user.id,
                func.date(Answer.created_at) == today,
            )
        )
    )
    return settings.free_tasks_per_day - (result.scalar() or 0)


@router.get("/session", response_model=list[TaskOut])
async def start_session(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    remaining = await check_daily_limit(db, user)
    if remaining <= 0:
        raise HTTPException(
            status_code=402,
            detail=f"Лимит бесплатных задач исчерпан. Premium — безлимит. Сегодня осталось: 0"
        )

    count = min(10, max(1, remaining + 5))
    engine = AdaptiveEngine(db)
    tasks = await engine.generate_daily_session(user.id, task_count=count, grade=user.grade)

    user.last_activity_at = datetime.utcnow()
    session = Session(user_id=user.id, session_type="daily")
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return [
        TaskOut(
            id=t.id,
            topic_id=t.topic_id,
            content=t.content,
            format=t.format,
            difficulty=t.difficulty,
        )
        for t in tasks
    ]


@router.get("/limits", response_model=dict)
async def get_limits(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    remaining = await check_daily_limit(db, user)
    is_premium = user.subscription and user.subscription.value == "premium"
    return {
        "remaining": remaining if not is_premium else -1,
        "limit": settings.free_tasks_per_day if not is_premium else -1,
        "is_premium": is_premium,
        "premium_price": settings.premium_monthly_price,
    }


@router.get("/current-session", response_model=dict)
async def get_current_session(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user.id, Session.completed_at.is_(None))
        .order_by(Session.started_at.desc())
        .limit(1)
    )
    session = result.scalar_one_or_none()
    if not session:
        return {"session_id": None, "tasks_completed": 0}
    return {"session_id": session.id, "tasks_completed": session.tasks_completed}


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut(
        id=task.id,
        topic_id=task.topic_id,
        content=task.content,
        format=task.format,
        difficulty=task.difficulty,
    )


@router.post("/submit", response_model=AnswerResult)
async def submit_answer(
    data: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    task = await db.get(Task, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    topic = await db.get(Topic, task.topic_id)

    student_answer = data.answer.strip()
    correct_answer = (task.answer_pattern or "").strip()

    is_correct = answers_match(student_answer, correct_answer)

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user.id, Session.completed_at.is_(None))
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

    engine = AdaptiveEngine(db)
    await engine.update_mastery(user.id, task.topic_id, is_correct)

    scheduler = SpacedRepetitionScheduler(db)
    if is_correct:
        existing_review = await db.execute(
            select(ErrorLog).where(
                ErrorLog.user_id == user.id,
                ErrorLog.task_id == task.id,
                ErrorLog.mastered == False,
            ).order_by(ErrorLog.created_at.desc()).limit(1)
        )
        review = existing_review.scalar_one_or_none()
        if review:
            await scheduler.advance_stage(review.id, mastered=True)

    if session:
        session.tasks_completed = (session.tasks_completed or 0) + 1
        if is_correct:
            session.correct_count = (session.correct_count or 0) + 1

    await db.commit()

    explanation = None
    ai_explanation = None
    error_type = None
    micro_task = None

    if not is_correct:
        analysis = await _analyzer.full_analysis(
            topic_id=task.topic_id,
            topic_name=topic.name if topic else str(task.topic_id),
            task_content=str(task.content.get("text", "")),
            student_answer=student_answer,
            correct_answer=correct_answer,
        )
        explanation = analysis.explanation
        ai_explanation = analysis.ai_explanation
        error_type = analysis.error_type
        micro_task = analysis.micro_task

        scheduler = SpacedRepetitionScheduler(db)

        existing_review = await db.execute(
            select(ErrorLog).where(
                ErrorLog.user_id == user.id,
                ErrorLog.task_id == task.id,
                ErrorLog.mastered == False,
            ).order_by(ErrorLog.created_at.desc()).limit(1)
        )
        review = existing_review.scalar_one_or_none()
        if review:
            await scheduler.advance_stage(review.id, mastered=False)
        else:
            await scheduler.schedule_review(user.id, task.id, error_type)

    return AnswerResult(
        is_correct=is_correct,
        correct_answer=correct_answer,
        explanation=explanation,
        ai_explanation=ai_explanation,
        error_type=error_type,
    )


@router.get("/mastery", response_model=list[dict])
async def get_mastery(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(Mastery, Topic)
        .join(Topic, Mastery.topic_id == Topic.id)
        .where(Mastery.user_id == user.id)
    )
    rows = result.all()
    return [
        {
            "topic_code": topic.code,
            "topic_name": topic.name,
            "score": mastery.score,
        }
        for mastery, topic in rows
    ]
