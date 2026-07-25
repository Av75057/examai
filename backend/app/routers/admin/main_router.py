from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.core.database import get_db
from app.models.models import Topic, Task, TaskTemplate, User, Session, Answer, ExamAttempt
from app.models.admin_models import AdminUser, AuditLog
from app.routers.admin.dependencies import (
    get_current_admin, require_any_user_mgmt, require_any_analyst,
    require_role, log_admin_action,
)
from app.models.models import Answer, ErrorLog, Mastery, Session as StudentSession

router = APIRouter(prefix="/admin", tags=["admin-users", "admin-dashboard"])


@router.get("/dashboard", response_model=dict)
async def dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_analyst())],
):
    user_count = await db.execute(select(func.count(User.id)))
    total_users = user_count.scalar()

    tasks_count = await db.execute(select(func.count(Task.id)))
    total_tasks = tasks_count.scalar()

    today_tasks = await db.execute(
        select(func.count(Answer.id))
    )

    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "total_topics": 24,
        "conversion_rate": 0,
        "dau": total_users,
        "mrr": 0,
        "moderation_queue": 0,
    }


@router.get("/users/students", response_model=dict)
async def list_students(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_user_mgmt())],
    page: int = Query(1, ge=1),
    per_page: int = Query(25, le=100),
    search: str = Query(""),
    role: str = Query(""),
):
    query = select(User)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") | User.name.ilike(f"%{search}%")
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(
        query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    users = result.scalars().all()

    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "subscription": u.subscription.value if u.subscription else "free",
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_activity_at": u.last_activity_at.isoformat() if u.last_activity_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/users/students/{user_id}", response_model=dict)
async def student_card(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_user_mgmt())],
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    from app.models.models import Mastery

    mastery_result = await db.execute(
        select(Mastery, Topic)
        .join(Topic, Mastery.topic_id == Topic.id)
        .where(Mastery.user_id == user_id)
    )
    mastery_list = [
        {"topic_code": topic.code, "topic_name": topic.name, "score": mastery.score}
        for mastery, topic in mastery_result
    ]

    sessions_count = await db.execute(
        select(func.count(Session.id)).where(Session.user_id == user_id)
    )
    answers_count = await db.execute(
        select(func.count(Answer.id)).where(Answer.session.has(Session.user_id == user_id))
    )

    exam_result = await db.execute(
        select(ExamAttempt).where(ExamAttempt.user_id == user_id).order_by(ExamAttempt.started_at.desc()).limit(5)
    )

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "subscription": user.subscription.value if user.subscription else "free",
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "mastery": mastery_list,
        "total_sessions": sessions_count.scalar(),
        "total_answers": answers_count.scalar(),
        "exams": [
            {"id": e.id, "test_score": e.test_score, "started_at": e.started_at.isoformat() if e.started_at else None}
            for e in exam_result.scalars().all()
        ],
    }


@router.delete("/users/students/{user_id}")
async def delete_student(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_any_user_mgmt())],
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await db.execute(__import__("sqlalchemy").delete(Answer).where(
        Answer.session.has(id=__import__("sqlalchemy").select(StudentSession.id).where(StudentSession.user_id == user_id))
    ))
    await db.execute(__import__("sqlalchemy").delete(ErrorLog).where(ErrorLog.user_id == user_id))
    await db.execute(__import__("sqlalchemy").delete(Mastery).where(Mastery.user_id == user_id))
    await db.execute(__import__("sqlalchemy").delete(StudentSession).where(StudentSession.user_id == user_id))

    await db.delete(user)
    await db.commit()

    await log_admin_action(db, admin.id, "delete", "user", resource_id=str(user_id),
                           old_value={"email": user.email, "name": user.name})
    return {"status": "deleted", "user_id": user_id}


@router.get("/audit-log", response_model=dict)
async def audit_log(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[AdminUser, Depends(require_role("super_admin"))],
    page: int = Query(1, ge=1),
    per_page: int = Query(50, le=200),
):
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    logs = result.scalars().all()
    return {
        "items": [
            {
                "id": l.id,
                "admin_id": l.admin_id,
                "action": l.action,
                "resource": l.resource,
                "resource_id": l.resource_id,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ],
        "total": len(logs),
        "page": page,
    }
