import asyncio
import random
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.models.models import Base, Topic, Task, TaskTemplate, TopicGrade, ExamConfig

EXAM_CONFIGS = [
    {"grade": 9, "format_name": "ОГЭ", "total_tasks": 25, "duration_minutes": 235,
     "structure": {"part1": {"count": 19, "difficulty": [0.2, 0.6]}, "part2": {"count": 6, "difficulty": [0.6, 0.95]}}},
    {"grade": 11, "format_name": "ЕГЭ-профиль", "total_tasks": 18, "duration_minutes": 235,
     "structure": {"part1": {"count": 12, "difficulty": [0.3, 0.7]}, "part2": {"count": 6, "difficulty": [0.6, 0.95]}}},
]
from app.core.config import get_settings
from app.services.templates import TEMPLATES
from app.services.task_generator import TaskGenerator, simplify_fraction, sqrt_str, frac_str

settings = get_settings()

TOPICS = [
    ("linear_equations", "Линейные уравнения", 1.0),
    ("quadratic_equations", "Квадратные уравнения", 1.5),
    ("rational_equations", "Рациональные уравнения", 1.5),
    ("systems_equations", "Системы уравнений", 1.5),
    ("inequalities", "Неравенства", 2.0),
    ("exponents", "Степени и корни", 1.5),
    ("logarithms", "Логарифмы", 2.0),
    ("trigonometry", "Тригонометрия", 2.0),
    ("derivatives", "Производные", 1.5),
    ("integrals", "Первообразные и интегралы", 1.5),
    ("probability", "Теория вероятностей", 1.0),
    ("geometry_planimetry", "Планиметрия", 2.0),
    ("geometry_stereometry", "Стереометрия", 2.0),
    ("word_problems", "Текстовые задачи", 1.5),
    ("graphs", "Графики функций", 1.0),
    ("financial_math", "Финансовая математика", 1.5),
    ("optimization", "Оптимизация", 2.0),
    ("parameters", "Задачи с параметром", 3.0),
    ("number_theory", "Теория чисел", 3.0),
    ("sequences", "Последовательности", 1.5),
    ("vectors", "Векторы", 1.0),
    ("combinatorics", "Комбинаторика", 1.0),
    ("statistics", "Статистика", 1.0),
]

TOPIC_GRADE_MAP = {
    "linear_equations": [7, 8, 9, 10, 11],
    "quadratic_equations": [8, 9, 10, 11],
    "rational_equations": [8, 9, 10, 11],
    "systems_equations": [7, 8, 9, 10, 11],
    "inequalities": [8, 9, 10, 11],
    "exponents": [7, 8, 9, 10, 11],
    "logarithms": [10, 11],
    "trigonometry": [9, 10, 11],
    "derivatives": [10, 11],
    "integrals": [11],
    "probability": [8, 9, 10, 11],
    "geometry_planimetry": [7, 8, 9, 10, 11],
    "geometry_stereometry": [10, 11],
    "word_problems": [5, 6, 7, 8, 9, 10, 11],
    "graphs": [8, 9, 10, 11],
    "financial_math": [9, 10, 11],
    "optimization": [10, 11],
    "parameters": [10, 11],
    "number_theory": [10, 11],
    "sequences": [9, 10, 11],
    "vectors": [9, 10, 11],
    "combinatorics": [9, 10, 11],
    "statistics": [8, 9, 10, 11],
}

VARIATIONS_PER_TEMPLATE = 5


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    generator = TaskGenerator(TEMPLATES)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker(engine, class_=AsyncSession)() as session:
        for code, name, weight in TOPICS:
            result = await session.execute(select(Topic).where(Topic.code == code))
            existing = result.scalar_one_or_none()
            if not existing:
                topic = Topic(code=code, name=name, ege_weight=weight)
                session.add(topic)

        await session.commit()

        topic_map = {}
        result = await session.execute(select(Topic))
        for t in result.scalars():
            topic_map[t.code] = t.id

        for code, grades in TOPIC_GRADE_MAP.items():
            if code in topic_map:
                for g in grades:
                    tg = TopicGrade(topic_id=topic_map[code], grade=g, is_primary=True)
                    session.add(tg)

        for ec in EXAM_CONFIGS:
            cfg = ExamConfig(
                grade=ec["grade"],
                format_name=ec["format_name"],
                total_tasks=ec["total_tasks"],
                duration_minutes=ec["duration_minutes"],
                structure=ec["structure"],
            )
            session.add(cfg)

        await session.commit()

        template_map = {}
        total_tasks = 0

        for tmpl_data in TEMPLATES:
            topic_id = topic_map[tmpl_data["topic_code"]]

            template = TaskTemplate(
                topic_id=topic_id,
                content_template=tmpl_data["content_template"],
                solution_template=tmpl_data["solution_template"],
                param_ranges={"type": "dynamic"},
                difficulty_base=tmpl_data["difficulty_base"],
            )
            session.add(template)
            await session.flush()
            template_map[tmpl_data["id"]] = template.id

        await session.commit()

        for tmpl_data in TEMPLATES:
            template_id = template_map[tmpl_data["id"]]
            topic_id = topic_map[tmpl_data["topic_code"]]

            for v in range(VARIATIONS_PER_TEMPLATE):
                try:
                    gen_task = generator.generate(tmpl_data["id"], random.uniform(-0.08, 0.08))
                except Exception as e:
                    print(f"  [ERROR] template={tmpl_data['id']} variation={v}: {e}")
                    continue

                task = Task(
                    topic_id=topic_id,
                    template_id=template_id,
                    difficulty=gen_task.difficulty,
                    format=gen_task.format,
                    content=gen_task.content,
                    solution=gen_task.solution,
                    answer_pattern=gen_task.answer,
                )
                session.add(task)
                total_tasks += 1

        await session.commit()

    await engine.dispose()

    print(f"\nSeed completed:")
    print(f"  Topics: 24")
    print(f"  Templates: {len(TEMPLATES)}")
    print(f"  Tasks generated: {total_tasks}")
    print(f"  Topics with templates: {len(set(t['topic_code'] for t in TEMPLATES))}")


if __name__ == "__main__":
    asyncio.run(seed())
