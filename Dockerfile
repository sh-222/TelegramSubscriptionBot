FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --compile-bytecode

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS migration-builder

WORKDIR /app
COPY . .
RUN uv sync --locked --compile-bytecode

FROM python:3.13-slim-bookworm

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]