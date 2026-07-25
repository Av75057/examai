# ExamAI Backend

## Запуск

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Поднять PostgreSQL и Redis
docker compose up -d db redis

# Запустить API
uvicorn app.main:app --reload
```
