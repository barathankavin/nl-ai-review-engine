FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY config ./config
COPY scripts ./scripts

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:////app/data/reviews.db

RUN mkdir -p /app/data

EXPOSE 8000

# Shell form expands $PORT at runtime (Railway injects a dynamic port).
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
