import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    student = "student"
    tutor = "tutor"
    admin = "admin"


class SubscriptionTier(str, enum.Enum):
    free = "free"
    premium = "premium"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.student)
    subscription = Column(Enum(SubscriptionTier), default=SubscriptionTier.free)
    grade = Column(Integer, default=11)
    exam_goal = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=True)

    sessions = relationship("Session", back_populates="user")
    error_logs = relationship("ErrorLog", back_populates="user")
    mastery = relationship("Mastery", back_populates="user")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    ege_weight = Column(Float, default=1.0)

    tasks = relationship("Task", back_populates="topic")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("task_templates.id"))
    difficulty = Column(Float, default=0.5)
    format = Column(String(20), default="numeric")
    content = Column(JSON, nullable=False)
    solution = Column(JSON, nullable=False)
    answer_pattern = Column(String(500))

    topic = relationship("Topic", back_populates="tasks")
    template = relationship("TaskTemplate", back_populates="tasks")


class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    content_template = Column(JSON, nullable=False)
    solution_template = Column(JSON, nullable=False)
    param_ranges = Column(JSON, nullable=False)
    difficulty_base = Column(Float, default=0.5)

    tasks = relationship("Task", back_populates="template")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(20), default="daily")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    tasks_completed = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)

    user = relationship("User", back_populates="sessions")
    answers = relationship("Answer", back_populates="session")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_answer = Column(String(500))
    is_correct = Column(Boolean, default=False)
    time_spent_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="answers")


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    error_type = Column(String(50))
    error_pattern = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    next_review_at = Column(DateTime)
    review_stage = Column(Integer, default=0)
    mastered = Column(Boolean, default=False)

    user = relationship("User", back_populates="error_logs")


class Mastery(Base):
    __tablename__ = "mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Float, default=0.5)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mastery")


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    primary_score = Column(Integer, nullable=True)
    test_score = Column(Integer, nullable=True)
    answers_data = Column(JSON, default=dict)


class TopicGrade(Base):
    __tablename__ = "topic_grades"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    is_primary = Column(Boolean, default=True)

    topic = relationship("Topic")


class ExamConfig(Base):
    __tablename__ = "exam_configs"

    grade = Column(Integer, primary_key=True)
    format_name = Column(String(50), nullable=False)
    total_tasks = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    structure = Column(JSON, nullable=False)
