.PHONY: dev backend frontend db seed

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

db-up:
	docker compose up -d db redis

db-down:
	docker compose down

seed:
	cd backend && python seed.py

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev: db-up
	@echo "Starting backend and frontend..."
	@cd backend && uvicorn app.main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait
