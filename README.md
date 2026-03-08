# AI Product Intelligence Platform

A production-style full-stack system for collecting product feedback, processing it with AI agents, indexing it in a vector database, and generating actionable product intelligence.

## What This Project Demonstrates

- Real-time feedback ingestion (`manual`, `CSV`, `JSON`, API)
- Asynchronous AI processing with Redis Queue workers
- Multi-agent analysis pipeline:
  - Sentiment Agent
  - Topic Extraction Agent
  - Feature Request Agent
  - Insight Agent
- Embedding pipeline using `SentenceTransformers`
- Vector search using `ChromaDB`
- RAG assistant for product-manager queries
- Live dashboard updates via WebSockets
- Weekly AI report generation via scheduler
- FastAPI + PostgreSQL + SQLAlchemy backend
- React + Tailwind + Recharts frontend
- Dockerized deployment for local run

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── ai_agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── vector_db/
│   │   └── workers/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── types/
│   ├── Dockerfile
│   └── nginx.conf
├── data/
│   ├── sample_feedback.csv
│   └── sample_feedback.json
├── docs/
│   ├── API.md
│   └── ARCHITECTURE.md
├── docker-compose.yml
└── .env.example
```

## Architecture Flow

1. Feedback hits ingestion API (`/api/v1/feedback/...`).
2. Feedback is persisted in PostgreSQL with status `pending`.
3. Job is pushed to Redis queue.
4. Worker consumes job and executes AI pipeline:
   - sentiment classification
   - topic extraction
   - feature request detection
   - single-feedback insight generation
5. Worker generates embedding and stores vectors in ChromaDB.
6. Worker writes analysis results to PostgreSQL and publishes real-time event to Redis Pub/Sub.
7. API service listens to events and broadcasts to connected dashboard clients via WebSocket.
8. Dashboard refreshes analytics and stream updates live.
9. Weekly scheduler queues weekly insight report generation.

## Environment Setup

Copy env file:

```bash
cp .env.example .env
```

Set your OpenAI key if you want LLM-backed analysis/RAG generation:

```bash
OPENAI_API_KEY=<your-key>
```

If `OPENAI_API_KEY` is not set, the platform still works using deterministic fallback logic.

## Run with Docker

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Chroma service: `http://localhost:8001`

## Quick Demo

1. Open dashboard at `http://localhost`.
2. Submit manual feedback or upload:
   - `data/sample_feedback.csv`
   - `data/sample_feedback.json`
3. Watch live processing events in the stream panel.
4. Ask assistant questions:
   - `What are the most common complaints?`
   - `What features are users requesting?`
   - `Summarize negative feedback about payments.`
5. Generate weekly report from dashboard or API.

## API Overview

See [docs/API.md](docs/API.md) for complete endpoint details.

Key endpoints:

- `POST /api/v1/feedback/manual`
- `POST /api/v1/feedback/upload/csv`
- `POST /api/v1/feedback/upload/json`
- `GET /api/v1/analytics/summary`
- `POST /api/v1/assistant/query`
- `GET /api/v1/reports/weekly/latest`
- `POST /api/v1/reports/weekly/generate`
- `WS /ws/updates`

## Local (Non-Docker) Run

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Worker

```bash
cd backend
python -m app.workers.worker
```

### Scheduler

```bash
cd backend
python -m app.workers.scheduler
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Production Considerations

- Replace default `SECRET_KEY`.
- Use managed Postgres/Redis/Chroma.
- Add Alembic migrations before production rollout.
- Add centralized logging and metrics (Prometheus/Grafana).
- Restrict CORS and enforce authentication on protected routes.
- Configure autoscaling for API and worker services.
