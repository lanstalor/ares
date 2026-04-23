FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY backend/app /app/app
COPY world_bible.md /app/world_bible.md

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
