FROM docker.io/library/python:3.12-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN apk add --no-cache curl

COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY src ./src

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data/uploads

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn excel_consumption_service.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
