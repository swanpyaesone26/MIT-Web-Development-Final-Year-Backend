# Multi-stage build for production with Poetry
# Stage 1: Build dependencies
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no dev dependencies)
RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR

# Stage 2: Runtime
FROM python:3.12-slim as runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app/

# Don't run collectstatic during build (needs DB connection)
# Run it manually: docker-compose exec web python manage.py collectstatic --noinput

# Verify gunicorn is installed
RUN which gunicorn && gunicorn --version

# Run gunicorn with full path (exec form doesn't expand PATH)
CMD ["/app/.venv/bin/gunicorn", "app.config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
