# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    v4l-utils \
  && (apt-get install -y --no-install-recommends python3-picamera2 libcamera0 || true) \
  && rm -rf /var/lib/apt/lists/*

COPY services/gesture-service/pyproject.toml /app/pyproject.toml
COPY services/gesture-service/README.md /app/README.md
COPY services/gesture-service/src /app/src

RUN --mount=type=cache,target=/root/.cache/pip \
  pip install --upgrade pip \
  && pip install .

CMD ["python", "-m", "gesture_service.main"]
