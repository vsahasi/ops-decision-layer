"""
CRUD endpoints for decision records.
Annotation (confirm/correct) lives here too.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from src.schema.decision import Decision, DecisionCreate, DecisionPatch

router = APIRouter()

# In-memory store for now — swap for DB layer in Phase 2
_store: dict[UUID, Decision] = {}


@router.get("/", response_model=list[Decision])
async def list_decisions(
    domain: str | None = None,
    reviewed: bool | None = None,
    limit: int = 50,
):
    results = list(_store.values())
    if domain:
        results = [d for d in results if d.decision.domain.value == domain]
    if reviewed is not None:
        results = [d for d in results if d.annotation.reviewed == reviewed]
    return results[:limit]


@router.get("/{decision_id}", response_model=Decision)
async def get_decision(decision_id: UUID):
    decision = _store.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.post("/", response_model=Decision, status_code=201)
async def create_decision(payload: DecisionCreate):
    decision = Decision(**payload.model_dump())
    _store[decision.id] = decision
    return decision


@router.patch("/{decision_id}", response_model=Decision)
async def annotate_decision(decision_id: UUID, patch: DecisionPatch):
    """
    Used by the annotation UI. Decision-makers confirm or correct
    the AI's extracted fields here.
    """
    decision = _store.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    update_data = patch.model_dump(exclude_none=True)
    updated = decision.model_copy(update=update_data)
    updated.annotation.reviewed = True
    _store[decision_id] = updated
    return updated


@router.delete("/{decision_id}", status_code=204)
async def delete_decision(decision_id: UUID):
    if decision_id not in _store:
        raise HTTPException(status_code=404, detail="Decision not found")
    del _store[decision_id]
