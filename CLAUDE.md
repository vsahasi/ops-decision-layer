# ops-decision-layer

A decision intelligence platform that captures the reasoning behind operational decisions as structured, retrievable data objects.

## What this project does

Ingests operational communications (Slack threads, Jira tickets, etc.), uses an LLM to extract structured decision records, and surfaces them in an annotation UI where decision-makers can confirm or correct the extraction. The resulting corpus becomes a training signal for enterprise agents.

## Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2
- **LLM:** Anthropic Claude (`claude-3-5-sonnet-20241022`) via `anthropic` SDK
- **Database:** PostgreSQL + pgvector (local via Docker)
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS
- **Local dev:** Docker Compose

## Repo layout

```
backend/
  src/
    schema/decision.py     # Core Decision object — the central data primitive
    extraction/extractor.py  # LLM extraction pipeline
    ingestion/slack.py     # Slack connector
    api/
      main.py              # FastAPI app
      routes/
        decisions.py       # CRUD + annotation endpoint (PATCH /decisions/{id})
        ingest.py          # Ingestion trigger (POST /ingest/slack)
        health.py
frontend/                  # Next.js annotation UI (in progress)
docs/ARCHITECTURE.md       # Stack decisions + data flow
MASTER_PLAN.md             # Internal strategy doc (gitignored — do not commit)
```

## Running locally

```bash
# Postgres
docker compose up db

# Backend
cd backend && source .venv/bin/activate
uvicorn src.api.main:app --reload
# API docs: http://localhost:8000/docs

# Frontend
cd frontend && npm run dev
# UI: http://localhost:3000
```

## Key conventions

- The **Decision object** (`backend/src/schema/decision.py`) is the core primitive. Every feature either populates one of its fields or queries them. Do not add fields without updating the schema version.
- The in-memory `_store` dict in `decisions.py` is a placeholder — the DB layer goes in `backend/src/db/` when the schema stabilizes.
- The **annotation endpoint** is `PATCH /decisions/{id}`. This is the contract between backend and frontend — confirm the field shape before changing it.
- `MASTER_PLAN.md` is gitignored. Never commit it.
- Raw source artifacts (Slack permalinks, Jira URLs) are stored in `decision.source.reference` and never modified. Re-extraction from the same source should always be possible.

## Environment variables

```
ANTHROPIC_API_KEY=       # Required for extraction pipeline
SLACK_BOT_TOKEN=         # Required for Slack ingestion
DATABASE_URL=            # postgresql+asyncpg://... (defaults to Docker Compose value)
```

Copy `backend/.env.example` to `backend/.env` and fill in.

## Current phase

Phase 1 — design partner sprint. Priority order:
1. Get extraction quality high enough that annotation feels like confirmation, not reconstruction
2. Ship annotation UI in the frontend
3. Wire up Postgres (replace in-memory store)
4. Add Jira ingestion connector alongside Slack

---

## Team & Work Split

Two engineers. Split by layer — do not cross into the other person's domain without coordinating.

| Owner | Domain | Key files |
|---|---|---|
| Engineer 1 | Backend — ingestion, extraction pipeline, API, DB | `backend/` |
| Engineer 2 | Frontend — annotation UI, decision repository, dashboards | `frontend/` |

**The interface between the two sides is the REST API.** The contract to never change unilaterally:
- `GET /decisions/` — list decisions (with filters)
- `GET /decisions/{id}` — fetch single decision
- `PATCH /decisions/{id}` — annotation UI writes corrections here
- `POST /ingest/slack` — trigger ingestion run

If you need to change a field shape on `PATCH /decisions/{id}`, coordinate with both sides first. Everything else is yours to own independently.

**Branch strategy:**
- `main` — always deployable
- Feature branches off main: `feat/<short-description>`
- No direct pushes to main — open a PR, get a review from the other engineer

---

## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First:** Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan:** Check in before starting implementation
3. **Track Progress:** Mark items complete as you go
4. **Explain Changes:** High-level summary at each step
5. **Document Results:** Add review section to `tasks/todo.md`
6. **Capture Lessons:** Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First:** Make every change as simple as possible. Impact minimal code.
- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact:** Changes should only touch what's necessary. Avoid introducing bugs.
