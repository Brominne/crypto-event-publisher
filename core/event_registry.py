"""
Event registry for automatic event class discovery and instantiation.
Zero external dependencies.
"""
import logging
from typing import Dict, Type, Any, Optional
from core.event import Event


logger = logging.getLogger(__name__)


class EventRegistry:
    """
    Central registry for event types.

    Events self-register, so you just need to define the class
    and it's automatically available via the API.
    """

    _events: Dict[str, Type[Event]] = {}

    @classmethod
    def register(cls, event_type: str):
        """
        Decorator to register an event class.

        Usage:
            @EventRegistry.register("price_alert")
            class PriceAlertEvent(Event):
                ...
        """
        def decorator(event_class: Type[Event]):
            cls._events[event_type] = event_class
            logger.debug(f"Registered event type: {event_type} -> {event_class.__name__}")
            return event_class
        return decorator

    @classmethod
    def register_class(cls, event_type: str, event_class: Type[Event]) -> None:
        """
        Manually register an event class.

        Args:
            event_type: Event type identifier
            event_class: Event class
        """
        cls._events[event_type] = event_class
        logger.info(f"Registered event type: {event_type} -> {event_class.__name__}")

    @classmethod
    def create_event(cls, event_type: str, **kwargs) -> Optional[Event]:
        """
        Create an event instance from registered type.

        Args:
            event_type: Event type identifier
            **kwargs: Event constructor arguments

        Returns:
            Event instance or None if type not found

        Raises:
            ValueError: If event type not registered
            TypeError: If kwargs don't match event constructor
        """
        if event_type not in cls._events:
            raise ValueError(f"Unknown event type: {event_type}. Registered types: {list(cls._events.keys())}")

        event_class = cls._events[event_type]

        try:
            return event_class(**kwargs)
        except TypeError as e:
            raise TypeError(f"Invalid arguments for {event_type}: {e}")

    @classmethod
    def get_registered_types(cls) -> list:
        """Get list of all registered event types."""
        return list(cls._events.keys())

    @classmethod
    def is_registered(cls, event_type: str) -> bool:
        """Check if event type is registered."""
        return event_type in cls._events

    @classmethod
    def get_event_class(cls, event_type: str) -> Optional[Type[Event]]:
        """Get event class for a given type."""
        return cls._events.get(event_type)
