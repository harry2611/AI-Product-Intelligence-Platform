# API Reference

Base URL: `/api/v1`

## Health

- `GET /health`

## Auth

- `POST /auth/register`
  - body: `{ "email", "full_name", "password" }`
- `POST /auth/login`
  - body: `{ "email", "password" }`
- `GET /auth/me`
  - bearer token required

## Feedback Ingestion

- `POST /feedback/manual`
  - body:
    ```json
    {
      "message": "Checkout is slow",
      "timestamp": "2026-03-07T12:00:00Z",
      "source": "manual",
      "user_id": "usr_123"
    }
    ```
- `POST /feedback/bulk`
  - body: `{ "items": [FeedbackCreate, ...] }`
- `POST /feedback/upload/csv`
  - multipart file upload
- `POST /feedback/upload/json`
  - multipart file upload
- `GET /feedback?limit=100&offset=0`
- `GET /feedback/{feedback_id}/analysis`

## Analytics

- `GET /analytics/summary?days=30`
- `GET /analytics/trends?days=30`
- `GET /analytics/feature-requests?days=30&limit=10`
- `GET /analytics/top-complaints?days=30&limit=10`

## AI Assistant (RAG)

- `POST /assistant/query`
  - body:
    ```json
    {
      "question": "What are users complaining about in payments?",
      "top_k": 8
    }
    ```

## Reports

- `GET /reports/weekly/latest`
- `POST /reports/weekly/generate`

## WebSocket

- `WS /ws/updates`
- Event samples:
  - `feedback_processed`
  - `feedback_failed`
  - `weekly_report_generated`
