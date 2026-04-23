.PHONY: backend-install backend-dev backend-test frontend-install frontend-dev frontend-build check compose-up

backend-install:
	python3 -m venv backend/.venv
	backend/.venv/bin/pip install -e backend/.[dev]

backend-dev:
	cd backend && ../.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	cd backend && ../.venv/bin/pytest

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

check:
	python3 -m compileall backend/app backend/tests
	node --check frontend/vite.config.js
	node --check frontend/src/lib/api.js

compose-up:
	docker compose up --build
