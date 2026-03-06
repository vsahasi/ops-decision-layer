"""
LLM-powered extraction pipeline.

Takes raw text (Slack thread, Jira ticket body, etc.) and attempts to
extract a structured Decision object. Returns None if no decision is found.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from anthropic import Anthropic
from pydantic import ValidationError

from src.schema.decision import (
    Decision,
    DecisionChoice,
    DecisionContext,
    DecisionOutcome,
    DecisionSource,
    Domain,
    OptionConsidered,
    SourceType,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a decision extraction engine. Given a block of text from an operational communication (Slack thread, Jira ticket, email, etc.), your job is to:

1. Determine whether a meaningful operational decision was made in this text.
2. If yes, extract the decision into a structured JSON object.
3. If no clear decision was made (it's a status update, idle discussion, or question without resolution), return null.

A "decision" means: someone chose a specific course of action over alternatives, with some reasoning behind it.

Return ONLY valid JSON — no explanation, no markdown fences.

If a decision exists, return:
{
  "situation": "<what was known / at stake>",
  "constraints": ["<constraint>", ...],
  "urgency": "low|medium|high|critical",
  "options_considered": [
    {"option": "<description>", "rejected_because": "<reason or null>"}
  ],
  "choice": "<what was decided>",
  "reasoning": "<why this option>",
  "made_by_role": "<job function, or 'unknown'>",
  "domain": "devops|procurement|finops|hiring|product|other"
}

If no decision exists, return:
null"""


class DecisionExtractor:
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.client = Anthropic()
        self.model = model

    def extract(
        self,
        raw_text: str,
        source_type: SourceType,
        source_reference: str,
    ) -> Decision | None:
        """
        Extract a Decision from raw text. Returns None if no decision found.
        Raises on LLM or validation errors after retries are exhausted.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_text}],
        )

        raw_output = response.content[0].text.strip()

        try:
            parsed: dict[str, Any] | None = json.loads(raw_output)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON output: %s", raw_output[:200])
            return None

        if parsed is None:
            return None

        try:
            return Decision(
                source=DecisionSource(
                    type=source_type,
                    reference=source_reference,
                ),
                context=DecisionContext(
                    situation=parsed["situation"],
                    constraints=parsed.get("constraints", []),
                    urgency=UrgencyLevel(parsed.get("urgency", "medium")),
                ),
                options_considered=[
                    OptionConsidered(**o) for o in parsed.get("options_considered", [])
                ],
                decision=DecisionChoice(
                    choice=parsed["choice"],
                    reasoning=parsed["reasoning"],
                    made_by_role=parsed.get("made_by_role", "unknown"),
                    domain=Domain(parsed.get("domain", "other")),
                ),
                outcome=DecisionOutcome(),
            )
        except (KeyError, ValueError, ValidationError) as e:
            logger.error("Failed to build Decision from LLM output: %s", e)
            return None
