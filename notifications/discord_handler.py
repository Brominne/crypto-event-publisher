"""
Discord notification handler.
Uses webhook for minimal dependencies (no discord.py needed).
"""
import asyncio
import logging
import json
import requests
from typing import Optional
from urllib.error import HTTPError, URLError

from core.event import Event, EventPriority
from core.listener import EventListener


logger = logging.getLogger(__name__)


class DiscordWebhookHandler(EventListener):
    """
    Discord notification handler using webhooks.

    No external dependencies - uses only standard library urllib.
    Webhooks are simpler than bots for send-only notifications.
    """

    def __init__(
        self,
        webhook_url: str,
        event_types: Optional[list] = None,
        filters: Optional[list] = None,
        username: str = "Trade Alert Bot",
        max_retries: int = 3
    ):
        """
        Initialize Discord webhook handler.

        Args:
            webhook_url: Discord webhook URL
            event_types: Event types to listen for (None = all)
            filters: Event filters to apply
            username: Bot username for messages
            max_retries: Max retry attempts for failed sends
        """
        super().__init__(event_types=event_types, filters=filters)
        self.webhook_url = webhook_url
        self.username = username
        self.max_retries = max_retries

    def get_name(self) -> str:
        """Return listener name."""
        return "DiscordWebhookHandler"

    def _format_message(self, event: Event) -> dict:
        """
        Format event into Discord embed message.

        Args:
            event: Event to format

        Returns:
            Discord webhook payload
        """
        # Color coding based on priority
        color_map = {
            EventPriority.LOW: 0x808080,      # Gray
            EventPriority.MEDIUM: 0x3498db,   # Blue
            EventPriority.HIGH: 0xf39c12,     # Orange
            EventPriority.CRITICAL: 0xe74c3c  # Red
        }

        embed = {
            "title": f"🔔 {event.event_type}",
            "color": color_map.get(event.priority, 0x3498db),
            "timestamp": event.timestamp.isoformat(),
            "fields": []
        }

        # Add data fields
        for key, value in event.data.items():
            embed["fields"].append({
                "name": key.replace("_", " ").title(),
                "value": str(value),
                "inline": True
            })

        # Add priority
        embed["fields"].append({
            "name": "Priority",
            "value": event.priority.name,
            "inline": True
        })

        return {
            "username": self.username,
            "embeds": [embed]
        }

    async def _send_webhook(self, payload: dict) -> bool:
        """
        Send webhook message with retries.

        Args:
            payload: Discord webhook payload

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                # Run blocking HTTP request in executor to avoid blocking event loop
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._send_request,
                    payload
                )
                logger.info("Discord notification sent successfully")
                return True

            except HTTPError as e:
                if e.code == 429:  # Rate limited
                    retry_after = int(e.headers.get("Retry-After", 1))
                    logger.warning(f"Rate limited, retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                else:
                    logger.error(f"HTTP error sending Discord notification: {e.code} - {e.reason}")
                    if attempt == self.max_retries - 1:
                        return False

            except URLError as e:
                logger.error(f"Network error sending Discord notification: {e.reason}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"Unexpected error sending Discord notification: {e}", exc_info=True)
                return False

        return False

    def _send_request(self, payload: dict) -> None:
        """
        Send HTTP request (blocking, should be called in executor).

        Args:
            payload: Discord webhook payload
        """

        data = json.dumps(payload).encode("utf-8")

        request = requests.Request(
            url=self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        prepared = request.prepare()

        # with urlopen(request, timeout=10) as response:
        #     response.read()
        session = requests.Session()
        response = session.send(prepared, timeout=10)
        print("Status:", response.status_code)

    async def handle(self, event: Event) -> None:
        """
        Handle event by sending Discord notification.

        Args:
            event: Event to handle
        """
        if not event.should_notify():
            logger.debug(f"Event {event.event_type} should not notify, skipping")
            return

        logger.info(f"Handling event: {event.event_type}")
        payload = self._format_message(event)
        await self._send_webhook(payload)
