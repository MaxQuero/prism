# ---- Builder ----
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

# ---- Runtime ----
FROM python:3.12-slim-bookworm

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd -r prism && useradd -r -g prism prism

COPY --from=builder --chown=prism:prism /app/.venv /app/.venv
COPY --chown=prism:prism . .

ENV PYTHONUNBUFFERED=1

USER prism
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
