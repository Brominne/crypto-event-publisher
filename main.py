"""
Main application entry point.
Runs continuously as a service, processing events via HTTP API.

All events now use GenericEvent - no custom classes needed!
"""
import asyncio
import signal

from core.event import Event
from core.event_bus import EventBus
from core.listener import EventListener
from notifications.discord_handler import DiscordWebhookHandler
from config.settings import Config, setup_logging
from api.http_api import EventAPIServer


# ============================================================================
# No event class definitions needed! All events use GenericEvent now.
# Just send JSON with event_type, data, priority, and optional notify_threshold.
# ============================================================================


# Console listener for testing
class ConsoleListener(EventListener):
    """Simple console output listener for testing."""

    def get_name(self) -> str:
        return "ConsoleListener"

    async def handle(self, event: Event) -> None:
        print(f"\n{'='*60}")
        print(f"[{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {event.event_type.upper()}")
        print(f"Priority: {event.priority.name}")
        print(f"Data: {event.data}")
        print(f"Should Notify: {event.should_notify()}")
        print(f"{'='*60}\n")


async def main():
    """Main application - runs continuously as a service."""
    # Load configuration
    config = Config(config_file="config.json")  # Falls back to env vars if file missing
    setup_logging(config.log_level)

    # Create event bus
    event_bus = EventBus()

    # Register listeners
    # Console listener (always active for testing)
    console_listener = ConsoleListener()
    event_bus.register_listener(console_listener)

    # Discord listener (only if webhook configured)
    try:
        discord_webhook = config.discord_webhook_url
        discord_listener = DiscordWebhookHandler(
            webhook_url=discord_webhook,
            username="Crypto Alert Bot"
        )
        event_bus.register_listener(discord_listener)
        print("✓ Discord notifications enabled")
    except ValueError:
        print("⚠ Discord webhook not configured, using console only")
        print("  Set DISCORD_WEBHOOK_URL environment variable or add to config.json")

    # Start event bus in background
    bus_task = asyncio.create_task(event_bus.start())

    # Start HTTP API server
    api_host = config.get("api_host", "localhost")
    api_port = config.get("api_port", 8080)
    api_server = EventAPIServer(
        host=api_host,
        port=api_port,
        event_publisher=event_bus.publish
    )
    api_task = asyncio.create_task(api_server.start())

    print(f"\n{'='*60}")
    print("Crypto Alert System - Service Mode")
    print(f"{'='*60}")
    print(f"Active listeners: {event_bus.get_listener_count()}")
    print(f"\nService running... Press Ctrl+C to stop")
    print(f"{'='*60}\n")

    # Setup graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler():
        print("\n\nShutdown signal received...")
        shutdown_event.set()

    # Register signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    # Wait for shutdown signal
    await shutdown_event.wait()

    # Graceful shutdown
    print("Stopping services...")
    await api_server.stop()
    await event_bus.stop()

    # Cancel tasks
    api_task.cancel()
    bus_task.cancel()

    try:
        await asyncio.gather(api_task, bus_task, return_exceptions=True)
    except asyncio.CancelledError:
        pass

    print("✓ Service stopped successfully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✓ Service stopped")
