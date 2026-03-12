FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md Makefile ./
COPY src ./src
COPY templates ./templates
COPY defaults ./defaults
COPY inventory ./inventory
COPY intent ./intent
COPY demo ./demo
COPY docs ./docs
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"
