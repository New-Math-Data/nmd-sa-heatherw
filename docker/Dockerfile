FROM python:3.12-slim AS api

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    PYTHONPATH=/app:/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc g++ make clang libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY ./src /app/src

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -e .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
