"""
Heartbeat monitor for service health checks.
Pings external monitoring service periodically.
"""
import asyncio
import logging
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    """
    Sends periodic heartbeat pings to external monitoring service.
    """

    def __init__(self, ping_url: str, interval_seconds: int = 30):
        """
        Initialize heartbeat monitor.

        Args:
            ping_url: URL to ping for health checks
            interval_seconds: Interval between pings (default: 30s)
        """
        self.ping_url = ping_url
        self.interval_seconds = interval_seconds
        self._running = False

    async def start(self) -> None:
        """
        Start the heartbeat monitor.
        Runs continuously sending pings at configured interval.
        """
        self._running = True
        logger.info(f"Heartbeat monitor started (pinging every {self.interval_seconds}s)")

        while self._running:
            try:
                # Send ping in executor to avoid blocking
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._send_ping
                )
                logger.debug(f"Heartbeat ping sent successfully")

            except Exception as e:
                logger.error(f"Failed to send heartbeat ping: {e}")

            # Wait for next interval
            await asyncio.sleep(self.interval_seconds)

        logger.info("Heartbeat monitor stopped")

    def _send_ping(self) -> None:
        """
        Send HTTP GET request to ping URL (blocking, runs in executor).

        Raises:
            Exception: If ping fails
        """
        try:
            with urlopen(self.ping_url, timeout=10) as response:
                response.read()
        except HTTPError as e:
            raise Exception(f"HTTP error: {e.code}")
        except URLError as e:
            raise Exception(f"Network error: {e.reason}")

    async def stop(self) -> None:
        """Stop the heartbeat monitor."""
        self._running = False
