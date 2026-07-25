from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models.models import Base
from app.routers import auth, tasks, errors, exams, diagnostic, exam_simulator, progress, chat
from app.routers.admin import auth_router, topics_router, main_router, templates_router, adaptive_router, ai_router, exams_router, grades_router
from app.models.admin_models import Base as AdminBase


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(AdminBase.metadata.create_all)
    yield


app = FastAPI(
    title="ExamAI",
    description="Адаптивный тренажёр по математике (профиль ЕГЭ)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(errors.router)
app.include_router(exams.router)
app.include_router(diagnostic.router)
app.include_router(exam_simulator.router)
app.include_router(progress.router)
app.include_router(chat.router)
app.include_router(auth_router.router)
app.include_router(topics_router.router)
app.include_router(main_router.router)
app.include_router(templates_router.router)
app.include_router(adaptive_router.router)
app.include_router(ai_router.router)
app.include_router(exams_router.router)
app.include_router(grades_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
