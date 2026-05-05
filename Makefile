.PHONY: backend-install backend-dev backend-test frontend-install frontend-dev frontend-build check compose-up migrate bootstrap-slice slice-status

BACKEND_VENV := backend/.venv

backend-install:
	python3 -m venv $(BACKEND_VENV)
	$(BACKEND_VENV)/bin/pip install -e backend/.[dev]

backend-dev:
	$(BACKEND_VENV)/bin/python -m app.db.bootstrap
	$(BACKEND_VENV)/bin/uvicorn --app-dir backend app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	$(BACKEND_VENV)/bin/pytest backend/tests

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

migrate:
	cd backend && alembic upgrade head

# Bootstrap a roadmap slice: branch + worktree + workstream doc.
# Usage: make bootstrap-slice SLICE=A1
bootstrap-slice:
	@if [ -z "$(SLICE)" ]; then \
		echo "usage: make bootstrap-slice SLICE=A1"; \
		exit 2; \
	fi
	@scripts/bootstrap_slice.sh $(SLICE)

# Show in-flight slices (worktrees + branches) at a glance.
slice-status:
	@echo "=== worktrees ==="
	@git worktree list
	@echo
	@echo "=== open slice branches ==="
	@git branch --list 'track-*' --format='%(refname:short)  %(committerdate:relative)  %(subject)' || true
