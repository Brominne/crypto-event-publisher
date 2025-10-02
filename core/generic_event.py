"""
Generic event implementation.
All events use the same class - configured via JSON.
"""
from core.event import Event, EventPriority


class GenericEvent(Event):
    """
    Universal event class.

    All event logic is configured via constructor parameters.
    No need for separate event classes!

    Usage:
        event = GenericEvent(
            event_type="price_alert",
            data={"symbol": "BTC/USDT", "price": "$45,000", "change": "+5.3%"},
            priority="HIGH",
            notify_threshold=None  # Optional: custom notification logic
        )
    """

    def __init__(
        self,
        event_type: str,
        data: dict,
        priority: str = "MEDIUM",
        notify_threshold: dict = None
    ):
        """
        Create a generic event.

        Args:
            event_type: Event type identifier (e.g., "price_alert", "volume_spike")
            data: Event data dictionary (will be displayed in notifications)
            priority: Priority level - "LOW", "MEDIUM", "HIGH", or "CRITICAL"
            notify_threshold: Optional dict with notification rules
                Examples:
                - {"always": True} - always notify
                - {"never": True} - never notify
                - {"field": "value", "gt": 100} - notify if data["value"] > 100
                - {"field": "change_percent", "abs_gte": 2.0} - notify if abs(data["change_percent"]) >= 2.0
        """
        # Parse priority string to enum
        try:
            priority_enum = EventPriority[priority.upper()]
        except (KeyError, AttributeError):
            priority_enum = EventPriority.MEDIUM

        super().__init__(
            event_type=event_type,
            data=data,
            priority=priority_enum
        )

        self.notify_threshold = notify_threshold or {"always": True}

    def should_notify(self) -> bool:
        """
        Determine if notification should be sent based on threshold rules.
        """
        threshold = self.notify_threshold

        # Always notify
        if threshold.get("always"):
            return True

        # Never notify
        if threshold.get("never"):
            return False

        # Field-based rules
        if "field" in threshold:
            field = threshold["field"]
            if field not in self.data:
                return False

            value = self.data[field]

            # Try to convert to number for comparisons
            try:
                # Remove common formatting characters
                if isinstance(value, str):
                    value = value.replace("$", "").replace(",", "").replace("%", "").replace("+", "")
                value = float(value)
            except (ValueError, TypeError):
                return False

            # Greater than
            if "gt" in threshold:
                return value > threshold["gt"]

            # Greater than or equal
            if "gte" in threshold:
                return value >= threshold["gte"]

            # Less than
            if "lt" in threshold:
                return value < threshold["lt"]

            # Less than or equal
            if "lte" in threshold:
                return value <= threshold["lte"]

            # Absolute value greater than or equal
            if "abs_gte" in threshold:
                return abs(value) >= threshold["abs_gte"]

            # Absolute value greater than
            if "abs_gt" in threshold:
                return abs(value) > threshold["abs_gt"]

        # Default: notify
        return True
