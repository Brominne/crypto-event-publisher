"""
Core event definitions and interfaces.
Zero external dependencies.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event(ABC):
    """
    Base event class. All events must inherit from this.

    Attributes:
        event_type: Unique identifier for the event type
        timestamp: When the event occurred
        data: Event-specific payload
        priority: Event priority level
        metadata: Optional additional metadata
    """
    event_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def should_notify(self) -> bool:
        """
        Determine if this event should trigger a notification.
        Each event type implements its own logic.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "priority": self.priority.name,
            "metadata": self.metadata
        }

    def __str__(self) -> str:
        return f"{self.event_type} at {self.timestamp} - Priority: {self.priority.name}"


class EventFilter(ABC):
    """Base class for event filters."""

    @abstractmethod
    def filter(self, event: Event) -> bool:
        """
        Returns True if the event passes the filter.

        Args:
            event: Event to filter

        Returns:
            True if event should be processed, False otherwise
        """
        pass


class PriorityFilter(EventFilter):
    """Filter events by minimum priority level."""

    def __init__(self, min_priority: EventPriority):
        self.min_priority = min_priority

    def filter(self, event: Event) -> bool:
        return event.priority.value >= self.min_priority.value
