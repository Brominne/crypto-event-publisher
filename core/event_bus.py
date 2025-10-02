"""
Event bus implementation with pub/sub pattern.
Zero external dependencies - uses only Python standard library.
"""
import asyncio
import logging
from typing import List, Optional
from core.event import Event
from core.listener import EventListener


logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for decoupled event handling.

    Events are published to the bus, which routes them to registered listeners.
    Listeners process events asynchronously.
    """

    def __init__(self):
        """Initialize the event bus."""
        self._listeners: List[EventListener] = []
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    def register_listener(self, listener: EventListener) -> None:
        """
        Register an event listener.

        Args:
            listener: EventListener instance to register
        """
        self._listeners.append(listener)
        logger.info(f"Registered listener: {listener.get_name()}")

    def unregister_listener(self, listener: EventListener) -> None:
        """
        Unregister an event listener.

        Args:
            listener: EventListener instance to unregister
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
            logger.info(f"Unregistered listener: {listener.get_name()}")

    async def publish(self, event: Event) -> None:
        """
        Publish an event to the bus.

        Args:
            event: Event to publish
        """
        logger.debug(f"Publishing event: {event}")
        await self._event_queue.put(event)

    async def _process_event(self, event: Event) -> None:
        """
        Process a single event by routing to appropriate listeners.

        Args:
            event: Event to process
        """
        tasks = []

        for listener in self._listeners:
            if listener.can_handle(event):
                logger.debug(f"Routing event {event.event_type} to {listener.get_name()}")
                tasks.append(listener.handle(event))

        if tasks:
            # Run all listener handlers concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log any exceptions that occurred
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Error in listener {self._listeners[i].get_name()}: {result}",
                        exc_info=result
                    )
        else:
            logger.warning(f"No listeners handled event: {event.event_type}")

    async def start(self) -> None:
        """
        Start the event bus processing loop.
        This should be run as an async task.
        """
        self._running = True
        logger.info("Event bus started")

        while self._running:
            try:
                # Wait for events with timeout to allow graceful shutdown
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
                self._event_queue.task_done()
            except asyncio.TimeoutError:
                # No events received, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)

        logger.info("Event bus stopped")

    async def stop(self) -> None:
        """Stop the event bus gracefully."""
        self._running = False

        # Wait for remaining events to be processed
        await self._event_queue.join()
        logger.info("All pending events processed")

    def get_listener_count(self) -> int:
        """Get the number of registered listeners."""
        return len(self._listeners)

    def get_pending_events_count(self) -> int:
        """Get the number of pending events in the queue."""
        return self._event_queue.qsize()
