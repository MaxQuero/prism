# ----  Builder ----
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*


COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
# Install project package locally to .venv
RUN uv sync --frozen --no-dev

# ---- Runtime ----
FROM python:3.10-slim

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# Security: create the 'prism' user
RUN groupadd -r prism && useradd -r -g prism prism

# Copy the entire virtual env from the builder
COPY --from=builder --chown=prism:prism /app/.venv /app/.venv
COPY --chown=prism:prism . .

ENV PYTHONUNBUFFERED=1


USER prism
EXPOSE 8000

# "uvicorn" will be found in /opt/venv/bin/uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]