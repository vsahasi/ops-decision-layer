from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    slack_thread = "slack_thread"
    jira_ticket = "jira_ticket"
    linear_issue = "linear_issue"
    email = "email"
    meeting_transcript = "meeting_transcript"


class UrgencyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class OutcomeStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    reversed = "reversed"


class Domain(str, Enum):
    devops = "devops"
    procurement = "procurement"
    finops = "finops"
    hiring = "hiring"
    product = "product"
    other = "other"


# --- Sub-objects ---

class DecisionSource(BaseModel):
    type: SourceType
    reference: str = Field(description="URL or external ID of the source artifact")
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionContext(BaseModel):
    situation: str = Field(description="What was known and at stake at decision time")
    constraints: list[str] = Field(default_factory=list)
    urgency: UrgencyLevel = UrgencyLevel.medium


class OptionConsidered(BaseModel):
    option: str
    rejected_because: str | None = None


class DecisionChoice(BaseModel):
    choice: str = Field(description="What was decided")
    reasoning: str = Field(description="Why this option over alternatives")
    made_by_role: str = Field(description="Job function of the decision-maker")
    domain: Domain = Domain.other


class DecisionOutcome(BaseModel):
    status: OutcomeStatus = OutcomeStatus.pending
    notes: str | None = None
    reviewed_at: datetime | None = None


class AnnotationRecord(BaseModel):
    reviewed: bool = False
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    corrections: list[dict[str, Any]] = Field(default_factory=list)


# --- Root decision object ---

class Decision(BaseModel):
    """
    Core data primitive. Every field maps to one of the six questions
    a decision record must answer (see MASTER_PLAN.md).
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    schema_version: str = "0.1"

    source: DecisionSource
    context: DecisionContext
    options_considered: list[OptionConsidered] = Field(default_factory=list)
    decision: DecisionChoice
    outcome: DecisionOutcome = Field(default_factory=DecisionOutcome)
    annotation: AnnotationRecord = Field(default_factory=AnnotationRecord)

    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionCreate(BaseModel):
    """Input model for manually creating a decision record."""
    source: DecisionSource
    context: DecisionContext
    options_considered: list[OptionConsidered] = []
    decision: DecisionChoice
    tags: list[str] = []


class DecisionPatch(BaseModel):
    """Partial update — used by the annotation UI."""
    context: DecisionContext | None = None
    options_considered: list[OptionConsidered] | None = None
    decision: DecisionChoice | None = None
    outcome: DecisionOutcome | None = None
    tags: list[str] | None = None
