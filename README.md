<p align="center">
  <h1 align="center">🎓 ExamAI</h1>
</p>

<p align="center">
  <strong>Адаптивный тренажёр ЕГЭ/ОГЭ по математике с ИИ-разборами ошибок</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-16-000000?logo=next.js" alt="Next.js"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License"/>
</p>

---

> Готовься к ЕГЭ по математике: решай задачи, получай ИИ-разборы ошибок, отслеживай прогресс по шкале ФИПИ.

---

## 📸 Демо

<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="Главный экран тренажёра" width="80%"/>
  <!-- alt: Дашборд с прогрессом и кнопкой START -->
</p>

---

## 🚀 Возможности

### 👨‍🎓 Ученик

- 🔄 **Адаптивный тренажёр** — 24 темы, 460+ задач, подбор по уровню (IRT-lite)
- 🤖 **ИИ-разбор ошибок** — DeepSeek объясняет каждую ошибку и даёт задание на закрепление
- 🎓 **Пробный ЕГЭ** — 18 заданий, таймер 3ч55м, шкала ФИПИ (0–100 баллов)
- 🧪 **Диагностика** — 5 задач, определение уровня по темам
- 📝 **Дневник ошибок** — интервальное повторение (1→3→7→14→30 дней)
- 🔥 **Стрик и прогресс** — счётчик дней, mastery по темам
- 📱 **Telegram-бот** — регистрация, оплата Premium, уведомления

### 🛡️ Администратор

- 🏫 **Привязка классов** (5–11) — фильтрация задач по программе
- 👥 **Управление учениками** — просмотр, блокировка, удаление, аналитика
- 📊 **Дашборд** — DAU, конверсия, MRR, топ тем
- 🤖 **ИИ-модерация** — паттерны ошибок, очередь проверки, управление промптами
- 📝 **Управление контентом** — CRUD тем, шаблонов задач, генерация вариаций
- 🔐 **RBAC + 2FA + аудит** — 5 ролей, журнал действий
- 💳 **Free/Premium** — 5 задач/день бесплатно, безлимит за 990₽/мес

---

## 🛠 Стек технологий

| Слой | Технологии |
|------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Pydantic v2 |
| Frontend | Next.js 16, TypeScript, Tailwind CSS, KaTeX |
| БД / Кэш | PostgreSQL 16, Redis 7 |
| ИИ | DeepSeek V4 (Flash) |
| Бот | python-telegram-bot |
| Инфра | Docker Compose, Makefile |

---

## ⚡ Быстрый старт

### Требования

- Docker ≥ 24 + Docker Compose v2
- Make
- (или Python 3.12 + Node 20 для локальной разработки)

### Запуск

```bash
git clone https://github.com/Av75057/examai.git
cd examai
cp backend/.env.example backend/.env
make db-up
make seed
make dev
```

### Доступ после запуска

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| API (Swagger) | http://localhost:8000/docs |
| Админка | http://localhost:3000/admin/login |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### Первый вход

```
Админ: admin@examai.ru / admin
Ученик: регистрация на http://localhost:3000
```

---

## 📁 Структура проекта

```
examai/
├── backend/
│   ├── app/
│   │   ├── core/           # конфиг, БД
│   │   ├── models/         # SQLAlchemy-модели (11 таблиц)
│   │   ├── routers/        # API: auth, tasks, diagnostic, chat, admin
│   │   ├── schemas/        # Pydantic-схемы
│   │   └── services/       # adaptive, error_analyzer, repetition, task_generator
│   ├── bot.py              # Telegram-бот
│   ├── seed.py             # 24 темы, 111 шаблонов, 460+ задач
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── dashboard/      # главный экран
│       ├── solve/          # решение задач
│       ├── result/         # результат + ИИ-разбор + чат
│       ├── diagnostic/     # входная диагностика
│       ├── exam-sim/       # пробный ЕГЭ
│       ├── errors/         # дневник ошибок
│       ├── profile/        # профиль + прогресс
│       ├── premium/        # подписка
│       └── admin/          # админ-панель (11 разделов)
├── docker-compose.yml
├── Makefile
└── docs/
```

---

## 🔧 Переменные окружения

Скопируйте `backend/.env.example` → `backend/.env`:

| Переменная | Описание | По умолчанию | Обязательна |
|-----------|----------|-------------|:----------:|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql+asyncpg://...` | ✅ |
| `REDIS_URL` | Строка подключения к Redis | `redis://localhost:6379/0` | ✅ |
| `JWT_SECRET` | Секрет для JWT-токенов | `dev-secret-...` | ✅ |
| `OPENAI_API_KEY` | Ключ API DeepSeek | — | ⚠️ |
| `OPENAI_BASE_URL` | Базовый URL API | `https://api.deepseek.com` | ❌ |
| `OPENAI_MODEL` | Модель ИИ | `deepseek-v4-flash` | ❌ |
| `DEBUG` | Режим отладки | `true` | ❌ |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота | — | ⚠️ |

> ⚠️ — без ключа фича работает в локальном режиме

---

## 📋 Команды Makefile

| Команда | Действие |
|---------|----------|
| `make db-up` | Запуск PostgreSQL + Redis |
| `make db-down` | Остановка БД |
| `make seed` | Сидирование: темы, шаблоны, задачи, админ |
| `make install` | pip install + npm install |
| `make dev` | Запуск всего проекта |
| `make dev-backend` | Только бэкенд (uvicorn --reload) |
| `make dev-frontend` | Только фронтенд (next dev) |

---

## 🚢 Деплой на сервер

```bash
# 1. Клонирование
git clone https://github.com/Av75057/examai.git && cd examai

# 2. Настройка
cp backend/.env.example backend/.env
nano backend/.env   # JWT_SECRET, API ключи

# 3. Запуск БД
docker compose up -d db redis

# 4. Сидирование
cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py

# 5. Бэкенд
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 6. Фронтенд
cd ../frontend && npm install && npm run build && npx next start -p 3000 &

# 7. Nginx reverse proxy → :3000 и :8000
```

**Production checklist:**
- [ ] `JWT_SECRET` ≥ 64 символов (`openssl rand -hex 32`)
- [ ] `DEBUG=false`
- [ ] PostgreSQL: отдельный пользователь
- [ ] HTTPS через Let's Encrypt
- [ ] Redis с паролем
- [ ] Файрвол: открыты только 80/443

---

## 🗺 Roadmap

- [x] MVP: адаптивный тренажёр + ИИ-разборы
- [x] Пробный ЕГЭ с таймером и шкалой ФИПИ
- [x] Диагностика уровня + интервальное повторение
- [x] Админка: RBAC, 2FA, аудит, управление контентом
- [x] Привязка классов (5–11)
- [x] Free/Premium тарифы
- [x] Telegram-бот для регистрации
- [x] LaTeX-рендеринг (KaTeX)
- [ ] PWA / мобильное приложение
- [ ] ОГЭ (9 класс)
- [ ] Родительский дашборд
- [ ] Другие предметы (физика, информатика)
- [ ] Экспорт отчётов в PDF

---

## 👥 Contributing

1. Форкните репозиторий
2. Создайте ветку: `feature/xxx` или `fix/xxx`
3. Внесите изменения, проверьте `make lint && make test`
4. Откройте Pull Request в `master`
5. Code review → merge

---

## 📄 License

MIT License. Подробнее в [LICENSE](LICENSE).

---

<p align="center">
  <sub>Сделано с ❤️ для подготовки к ЕГЭ</sub>
</p>
