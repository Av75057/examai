import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from passlib.hash import bcrypt
from datetime import datetime
import os

# Config
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://185.43.5.82:3001")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://examai:examai_secret@localhost:5432/examai")

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tg_id = str(user.id)

    keyboard = [
        [InlineKeyboardButton("📝 Регистрация", callback_data="register")],
        [InlineKeyboardButton("🚀 Открыть тренажёр", web_app=WebAppInfo(url=f"{WEBAPP_URL}/dashboard"))],
        [InlineKeyboardButton("⭐ Premium", web_app=WebAppInfo(url=f"{WEBAPP_URL}/premium"))],
        [InlineKeyboardButton("📊 Прогресс", web_app=WebAppInfo(url=f"{WEBAPP_URL}/profile"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я — бот ExamAI, адаптивного тренажёра по математике.\n\n"
        f"📚 24 темы ЕГЭ\n"
        f"🤖 ИИ-разбор ошибок\n"
        f"🎓 Пробные экзамены\n"
        f"🔥 Бесплатно: 5 задач/день\n\n"
        f"Что хочешь сделать?",
        reply_markup=reply_markup,
    )


async def handle_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    tg_id = str(user.id)
    email = f"tg_{tg_id}@examai.ru"
    password = f"tg{tg_id[:8]}"
    name = user.first_name or "Ученик"

    async with async_session() as session:
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email},
        )
        existing = result.scalar_one_or_none()

        if existing:
            await query.edit_message_text(
                f"✅ Ты уже зарегистрирован!\n\n"
                f"Логин: `{email}`\n"
                f"Пароль: `{password}`\n\n"
                f"Нажми кнопку ниже, чтобы начать:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Открыть тренажёр", web_app=WebAppInfo(url=f"{WEBAPP_URL}/dashboard"))],
                ]),
            )
        else:
            pw_hash = bcrypt.hash(password)
            await session.execute(
                text("INSERT INTO users (email, password_hash, name, grade) VALUES (:e, :p, :n, :g)"),
                {"e": email, "p": pw_hash, "n": name, "g": 11},
            )
            await session.commit()

            await query.edit_message_text(
                f"🎉 Регистрация прошла успешно!\n\n"
                f"Твои данные для входа:\n"
                f"Логин: `{email}`\n"
                f"Пароль: `{password}`\n\n"
                f"Сохрани их! Нажми кнопку для входа:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Начать тренировку", web_app=WebAppInfo(url=f"{WEBAPP_URL}/dashboard"))],
                ]),
            )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "/start":
        await start(update, context)
    elif text == "/register":
        fake_query = update
        await handle_register(fake_query, context)
    elif text == "/help":
        await update.message.reply_text(
            "📚 *ExamAI — тренажёр ЕГЭ по математике*\n\n"
            "/start — главное меню\n"
            "/register — регистрация\n"
            "/help — помощь\n\n"
            "🌐 Веб-версия: {WEBAPP_URL}",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "Используй кнопки меню или команду /start"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", handle_register))
    app.add_handler(CommandHandler("help", handle_message))
    app.add_handler(CallbackQueryHandler(handle_register, pattern="^register$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
