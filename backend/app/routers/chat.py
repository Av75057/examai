from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.database import get_db
from app.core.config import get_settings
from app.routers.auth import current_user
from app.models.models import User, Task, ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


class ChatRequest(BaseModel):
    task_id: int | None = None
    message: str


class ChatResponse(BaseModel):
    reply: str


def get_ai_client():
    if settings.openai_api_key:
        return AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    return None


SYSTEM_PROMPT = """Ты — ИИ-репетитор по математике ЕГЭ. Помогаешь ученику разобраться в ошибках.
- Объясняй простыми словами
- Используй формулы LaTeX в $...$
- Будь дружелюбным
- Если ученик спрашивает не по теме — вежливо возвращай к математике
- Давай аналогичные примеры для закрепления"""


@router.post("/send", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Пустое сообщение")

    task_context = ""
    if data.task_id:
        task = await db.get(Task, data.task_id)
        if task:
            task_context = f"\nКонтекст задачи: {task.content.get('text', '')}\nПравильный ответ: {task.answer_pattern}"

    # Save user message
    user_msg = ChatMessage(
        user_id=user.id,
        task_id=data.task_id,
        role="user",
        content=data.message,
    )
    db.add(user_msg)

    # Get history
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    history = list(reversed(result.scalars().all()))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-8:]:
        if msg.id < user_msg.id:
            messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": data.message + task_context})

    client = get_ai_client()
    reply = "Извини, ИИ-репетитор сейчас недоступен. Попробуй позже."

    if client:
        try:
            resp = await client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content or reply
        except Exception:
            pass

    ai_msg = ChatMessage(
        user_id=user.id,
        task_id=data.task_id,
        role="assistant",
        content=reply,
    )
    db.add(ai_msg)
    await db.commit()

    return ChatResponse(reply=reply)


@router.get("/history", response_model=dict)
async def get_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
    task_id: int | None = None,
):
    query = select(ChatMessage).where(ChatMessage.user_id == user.id)
    if task_id:
        query = query.where(ChatMessage.task_id == task_id)
    query = query.order_by(ChatMessage.created_at.desc()).limit(20)

    result = await db.execute(query)
    messages = list(reversed(result.scalars().all()))

    return {
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "task_id": m.task_id,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]
    }
