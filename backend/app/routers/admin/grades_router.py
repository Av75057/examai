from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import get_db
from app.models.models import Topic, TopicGrade, ExamConfig
from app.models.admin_models import AdminUser
from app.routers.admin.dependencies import get_current_admin, require_role, log_admin_action

router = APIRouter(prefix="/admin/grades", tags=["admin-grades"])

GRADES = [5, 6, 7, 8, 9, 10, 11]


@router.get("/topics", response_model=dict)
async def topics_with_grades(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    result = await db.execute(select(Topic).order_by(Topic.id))
    topics = result.scalars().all()

    grade_result = await db.execute(select(TopicGrade))
    grade_map: dict[int, list[int]] = {}
    for tg in grade_result.scalars():
        grade_map.setdefault(tg.topic_id, []).append(tg.grade)

    return {
        "items": [
            {
                "id": t.id,
                "code": t.code,
                "name": t.name,
                "grades": grade_map.get(t.id, []),
            }
            for t in topics
        ],
        "available_grades": GRADES,
    }


@router.put("/topics/{topic_id}/grades", response_model=dict)
async def update_topic_grades(
    topic_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_role("super_admin")),
):
    grades = data.get("grades", [])

    await db.execute(delete(TopicGrade).where(TopicGrade.topic_id == topic_id))

    for g in grades:
        tg = TopicGrade(topic_id=topic_id, grade=g, is_primary=True)
        db.add(tg)

    await db.commit()
    await log_admin_action(db, admin.id, "update", "topic_grades", resource_id=str(topic_id), new_value={"grades": grades})
    return {"status": "ok", "topic_id": topic_id, "grades": grades}


@router.get("/exam-configs", response_model=dict)
async def exam_configs(
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    result = await db.execute(select(ExamConfig))
    configs = result.scalars().all()
    return {
        "items": [
            {"grade": c.grade, "format_name": c.format_name, "total_tasks": c.total_tasks, "duration_minutes": c.duration_minutes}
            for c in configs
        ]
    }
