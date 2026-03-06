"""
Slack ingestion connector.

Reads messages from a channel (or a thread) and yields raw text
blocks suitable for passing to the extraction pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


@dataclass
class RawThread:
    channel_id: str
    thread_ts: str
    permalink: str
    text: str  # full thread collapsed into a single string


class SlackIngester:
    def __init__(self, bot_token: str):
        self.client = WebClient(token=bot_token)

    def fetch_channel_threads(
        self,
        channel_id: str,
        limit: int = 100,
    ) -> list[RawThread]:
        """
        Fetches recent threads from a channel. Each thread is collapsed
        into a single text block (author + message per line).
        """
        threads: list[RawThread] = []

        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit,
            )
        except SlackApiError as e:
            logger.error("Failed to fetch channel history: %s", e.response["error"])
            return threads

        for message in response.get("messages", []):
            if message.get("reply_count", 0) == 0:
                # Single messages without replies — still worth extracting
                thread_text = self._format_message(message)
                permalink = self._get_permalink(channel_id, message["ts"])
                threads.append(
                    RawThread(
                        channel_id=channel_id,
                        thread_ts=message["ts"],
                        permalink=permalink,
                        text=thread_text,
                    )
                )
            else:
                thread = self._fetch_thread(channel_id, message["ts"])
                if thread:
                    threads.append(thread)

        return threads

    def _fetch_thread(self, channel_id: str, thread_ts: str) -> RawThread | None:
        try:
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
            )
        except SlackApiError as e:
            logger.error("Failed to fetch thread %s: %s", thread_ts, e.response["error"])
            return None

        messages = response.get("messages", [])
        if not messages:
            return None

        lines = [self._format_message(m) for m in messages]
        permalink = self._get_permalink(channel_id, thread_ts)

        return RawThread(
            channel_id=channel_id,
            thread_ts=thread_ts,
            permalink=permalink,
            text="\n".join(lines),
        )

    def _get_permalink(self, channel_id: str, message_ts: str) -> str:
        try:
            response = self.client.chat_getPermalink(
                channel=channel_id,
                message_ts=message_ts,
            )
            return response["permalink"]
        except SlackApiError:
            return f"slack://channel/{channel_id}/ts/{message_ts}"

    def _format_message(self, message: dict) -> str:
        user = message.get("user", "unknown")
        text = message.get("text", "")
        return f"[{user}]: {text}"
