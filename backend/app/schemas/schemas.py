from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    grade: int = 11


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    email: str
    name: str
    subscription: str
    grade: int = 11
    streak_days: int = 0

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    topic_id: int
    content: dict
    format: str
    difficulty: float

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    task_id: int
    answer: str
    time_spent_seconds: float


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    ai_explanation: Optional[str] = None
    error_type: Optional[str] = None
    micro_task: Optional[str] = None


class SessionCreate(BaseModel):
    session_type: str = "daily"


class SessionProgress(BaseModel):
    session_id: int
    tasks_completed: int
    correct_count: int
    accuracy: float


class MasteryOut(BaseModel):
    topic_code: str
    topic_name: str
    score: float

    class Config:
        from_attributes = True
