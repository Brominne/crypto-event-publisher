"""
Event listener interface.
Zero external dependencies.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from core.event import Event, EventFilter


class EventListener(ABC):
    """
    Base class for event listeners (notification handlers).

    Each listener registers for specific event types and handles them
    when they occur.
    """

    def __init__(self, event_types: Optional[List[str]] = None, filters: Optional[List[EventFilter]] = None):
        """
        Initialize listener.

        Args:
            event_types: List of event types to listen for. None means listen to all.
            filters: Optional list of filters to apply before handling
        """
        self.event_types = event_types or []
        self.filters = filters or []

    def can_handle(self, event: Event) -> bool:
        """
        Check if this listener should handle the event.

        Args:
            event: Event to check

        Returns:
            True if listener should handle this event
        """
        # Check if we listen to this event type (empty list means all events)
        if self.event_types and event.event_type not in self.event_types:
            return False

        # Apply all filters
        for event_filter in self.filters:
            if not event_filter.filter(event):
                return False

        return True

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """
        Handle the event. Implement notification logic here.

        Args:
            event: Event to handle
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the listener name for logging purposes."""
        pass
