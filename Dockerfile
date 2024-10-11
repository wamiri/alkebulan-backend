FROM python:3.10-slim AS builder

RUN python -m pip install --upgrade pip && pip install poetry==1.8.3

# Environment variables
# PYTHONDONTWRITEBYTECODE=1 prevents Python from writing .pyc files
# PYTHONUNBUFFERED=1 ensures that Python outputs everything in real-time without buffering
# POETRY_NO_INTERACTION=1 disables Poetry interactive prompts (useful in CI/CD environments)
# POETRY_VIRTUALENVS_IN_PROJECT=1 ensures that virtual environments are created inside the project directory
# POETRY_VIRTUALENVS_CREATE=1 forces Poetry to create virtual environments
# POETRY_CACHE_DIR sets the location of the Poetry cache to a temporary directory
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY ./app .

FROM python:3.10-slim AS runner

WORKDIR /app
COPY --from=builder /app /app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
