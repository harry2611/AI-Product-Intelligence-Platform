# Architecture Notes

## Backend Layers

- `api/`: HTTP + WS entrypoints
- `services/`: orchestration/business services
- `ai_agents/`: modular agent pipeline
- `rag/`: retrieval + answer generation
- `vector_db/`: Chroma abstraction
- `workers/`: async background processing + scheduling
- `models/` + `schemas/`: persistence + API contracts

## Data Stores

- PostgreSQL:
  - feedback
  - sentiment_results
  - topic_mentions
  - feature_requests
  - feedback_embeddings (metadata + vector id)
  - insight_reports
  - users
- ChromaDB:
  - semantic vectors for each feedback

## Real-Time Architecture

- Worker publishes processing events to Redis Pub/Sub channel.
- API app subscribes and pushes events to active WebSocket clients.
- Frontend listens on `/ws/updates` and updates dashboard state.

## RAG Pipeline

1. Query embedding generated via SentenceTransformers.
2. Top-K similar feedback retrieved from Chroma.
3. Context passed to LLM (or fallback summarizer).
4. Response returned with citations.

## Multi-Agent Pipeline

1. Sentiment Agent
2. Topic Extraction Agent
3. Feature Request Agent
4. Insight Agent

Output is persisted and used by analytics/reporting/RAG.
