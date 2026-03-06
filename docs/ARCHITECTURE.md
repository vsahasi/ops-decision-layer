# Architecture

## Stack

| Layer | Technology | Why |
|---|---|---|
| Backend API | FastAPI (Python) | LLM ecosystem is Python-first. Pydantic for schema validation. Async-native. |
| Database | PostgreSQL + pgvector | Structured decision objects + semantic search over context/reasoning fields in one DB. |
| LLM | Anthropic Claude (claude-3-5-sonnet) | Best instruction-following for structured extraction tasks. Swap to OpenAI if needed. |
| Frontend | Next.js (TypeScript + Tailwind) | App Router, server components, fast iteration on the annotation UI. |
| Infrastructure | Docker Compose (local), TBD (prod) | Simple local dev setup. Prod infra TBD — Railway or Render for early stage. |

## Repository Structure

```
ops-decision-layer/
├── backend/
│   ├── src/
│   │   ├── schema/         # Core data models (Decision object + sub-types)
│   │   ├── extraction/     # LLM extraction pipeline
│   │   ├── ingestion/      # Source connectors (Slack, Jira, ...)
│   │   ├── api/
│   │   │   ├── main.py     # FastAPI app + middleware
│   │   │   └── routes/     # decisions, ingest, health
│   │   └── db/             # DB models + migrations (Phase 2)
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js app
├── docs/
│   └── ARCHITECTURE.md     # This file
├── docker-compose.yml
└── README.md
```

## Data Flow

```
Source (Slack / Jira)
       │
       ▼
  Ingestion layer
  (fetch raw text)
       │
       ▼
  Extraction pipeline
  (LLM → structured Decision object)
       │
       ▼
  Decision store
  (in-memory → Postgres + pgvector)
       │
       ├──► Annotation queue (frontend: confirm / correct)
       │
       └──► Repository UI (search, filter, dashboards)
```

## Key Design Decisions

**Why the Decision object is the core primitive, not the source artifact.**
We store raw source references (a Slack permalink, a Jira ticket ID) separately from the structured decision record. This means we can re-extract from the same source if the extraction model improves, without losing the human-annotated corrections.

**Why in-memory store first.**
The fastest way to validate extraction quality with design partners is to not have a DB in the critical path. The API routes use a simple dict now — swapping for async SQLAlchemy + Postgres is a clean one-file change when the schema stabilizes.

**Why pgvector over a standalone vector DB.**
Adding a second database (Pinecone, Weaviate, Qdrant) adds operational complexity with no benefit at this stage. pgvector gives semantic search within Postgres. If query performance becomes a problem at scale, migrating vector storage is straightforward.

**Annotation as a first-class flow, not an afterthought.**
The `PATCH /decisions/{id}` endpoint is the annotation endpoint. The frontend annotation UI writes to it. Every correction is stored in `annotation.corrections` so we can track what the model consistently gets wrong and use those pairs for fine-tuning.

## Local Dev Setup

See `README.md` for full instructions.

Short version:
```bash
# 1. Start Postgres
docker compose up db

# 2. Start backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
uvicorn src.api.main:app --reload

# 3. Start frontend
cd frontend
npm install
npm run dev
```

API docs available at http://localhost:8000/docs once the backend is running.
