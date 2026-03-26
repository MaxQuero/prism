# Prism — AI-powered energy forecasting

Prism is a real-time monitoring and forecasting platform for the French power grid. It bridges raw grid data (RTE API) and modern AI to deliver actionable energy insights.

This repository is maintained with **clear boundaries**, **automated quality checks**, and **modern tooling** so the codebase stays **maintainable, type-safe, and review-friendly** as it grows.

## Architecture & tech stack

The repo is a **monorepo** aligned with **Clean Architecture (hexagonal)** for maintainability, scalability, and testability.

| Component       | Technology            | Responsibility                                              |
|-----------------|-----------------------|-------------------------------------------------------------|
| ML Engine       | Python / FastAPI      | RTE ingestion, Chronos (zero-shot) inference              |
| API Gateway     | Node.js / Express     | Auth, proxy, user management                               |
| Database        | TimescaleDB (Postgres)| Time-series storage (hypertables)                          |
| Frontend        | React / Vite          | Interactive data visualization                             |
| Infrastructure  | Docker / Compose      | Multi-container orchestration                              |

## Key features

- **Real-time ingestion** — Sync with RTE (French TSO) via OAuth2 APIs.
- **AI-driven forecasts** — Time-series models (e.g. Amazon Chronos) for short-horizon load prediction.
- **Time-series storage** — TimescaleDB hypertables for scalable queries over large series.
- **Industrial practices** — DDD-style boundaries, hexagonal ports & adapters, Conventional Commits.

## Engineering & quality practices

- **Hexagonal / Clean Architecture** — Domain and application logic stay independent from HTTP, DB, and external APIs (adapters at the edges).
- **Explicit configuration** — Settings and secrets are loaded via typed configuration (e.g. Pydantic Settings), not scattered magic strings.
- **Structured logging** — Consistent, contextual logs for operations and debugging.
- **Small, reviewable changes** — Commit messages follow **Conventional Commits** (often with **gitmoji** for quick scanning) so history stays readable and tooling (changelog, semver) can plug in later.
- **Container-first** — Services ship as reproducible Docker images; local development matches production constraints as closely as practical.

## Tooling — ML Engine (Python)

The `services/ml-engine` service standardizes on a **modern Python** workflow:

| Tool | Role |
|------|------|
| **[uv](https://github.com/astral-sh/uv)** | Fast dependency resolution and lockfile (`uv.lock`); reproducible installs in dev and CI/Docker. |
| **[Ruff](https://github.com/astral-sh/ruff)** | Linter and formatter (replaces separate flake8/black/isort for speed). Configured in `pyproject.toml`. |
| **[Pyright](https://github.com/microsoft/pyright)** | Static type checking; **strict** mode is the baseline for new code. |
| **[pre-commit](https://pre-commit.com/)** | Runs Ruff, Pyright, and architecture/import checks before commits (see `.pre-commit-config.yaml`). |
| **Loguru** | Ergonomic logging with sensible defaults. |
| **FastAPI / Uvicorn / HTTPX / Pydantic Settings** | API layer, ASGI server, HTTP client, and typed settings. |

**Typical local setup (ML Engine):**

```bash
cd services/ml-engine
uv sync
uv run pre-commit install   # optional but recommended
```

Run checks manually when needed: `uv run ruff check .`, `uv run ruff format .`, `uv run pyright`.

## Tooling — Gateway & front (overview)

- **Gateway** (`services/gateway`) — Node **24** on **Debian Bookworm**-based images; multi-stage Docker builds; production installs use locked dependencies where applicable.
- **Dashboard** — React / Vite (see `apps/dashboard` as the stack evolves).

## Getting started

```bash
# 1. Clone the repository
git clone https://github.com/MaxQuero/prism.git
cd prism

# 2. Configure secrets (copy and edit values)
cp .env.example .env

# 3. Run the stack
docker compose -f docker-compose.yaml up --build
```

Prerequisites: **Docker** and **Docker Compose** (Compose V2: `docker compose`).

Use a project-level **`.env`** at the repository root so Compose can substitute `${VARIABLES}` in `docker-compose.yaml` and inject values into services.
