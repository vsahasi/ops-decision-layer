"""
Ingestion trigger endpoints.
Kick off extraction runs from connected sources.
"""

import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from src.ingestion.slack import SlackIngester
from src.extraction.extractor import DecisionExtractor
from src.schema.decision import SourceType
from src.api.routes.decisions import _store

router = APIRouter()


class SlackIngestRequest(BaseModel):
    channel_id: str
    limit: int = 100


@router.post("/slack")
async def ingest_slack(
    payload: SlackIngestRequest,
    background_tasks: BackgroundTasks,
):
    """
    Triggers a background ingestion run for a Slack channel.
    Extracted decisions are queued for annotation.
    """
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="SLACK_BOT_TOKEN not configured")

    background_tasks.add_task(
        _run_slack_ingestion,
        channel_id=payload.channel_id,
        token=token,
        limit=payload.limit,
    )
    return {"status": "ingestion queued", "channel_id": payload.channel_id}


def _run_slack_ingestion(channel_id: str, token: str, limit: int):
    ingester = SlackIngester(bot_token=token)
    extractor = DecisionExtractor()

    threads = ingester.fetch_channel_threads(channel_id, limit=limit)
    extracted = 0

    for thread in threads:
        decision = extractor.extract(
            raw_text=thread.text,
            source_type=SourceType.slack_thread,
            source_reference=thread.permalink,
        )
        if decision:
            _store[decision.id] = decision
            extracted += 1

    return extracted
