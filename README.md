# Prism — AI-powered energy forecasting

Prism is a real-time monitoring and forecasting platform for the French power grid. It bridges raw grid data (RTE API) and modern AI to deliver actionable energy insights.

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

## Getting started

```bash
# 1. Clone the repository
git clone https://github.com/MaxQuero/prism.git
cd prism

# 2. Configure secrets (copy and edit values)
cp .env.example .env

# 3. Run the stack
docker compose up --build
```

Prerequisites: **Docker** and **Docker Compose** (Compose V2: `docker compose`).
