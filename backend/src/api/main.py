from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import decisions, ingest, health

app = FastAPI(
    title="Ops Decision Layer API",
    description="Decision intelligence platform — capture, structure, and query operational decisions.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
