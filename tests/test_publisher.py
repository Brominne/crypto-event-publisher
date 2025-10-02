#!/usr/bin/env python3
"""
Test event publisher - sends test events to running service.
Uses only standard library (no external dependencies).

UPDATED: Uses GenericEvent - send any event with simple JSON!
"""
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class EventPublisher:
    """Simple HTTP client to publish events to the API."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize publisher.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')

    def publish_event(
        self,
        event_type: str,
        data: dict,
        priority: str = "MEDIUM",
        notify_threshold: dict = None
    ) -> dict:
        """
        Publish an event using GenericEvent.

        Args:
            event_type: Type of event (any string - "price_alert", "custom", etc.)
            data: Event data dictionary (displayed in notifications)
            priority: Priority level - "LOW", "MEDIUM", "HIGH", or "CRITICAL"
            notify_threshold: Optional notification rules
                Examples:
                - {"always": True} - always notify (default)
                - {"never": True} - never notify
                - {"field": "change", "abs_gte": 2.0} - notify if abs(data["change"]) >= 2.0
                - {"field": "value", "gt": 100} - notify if data["value"] > 100

        Returns:
            API response
        """
        payload = {
            "event_type": event_type,
            "data": data,
            "priority": priority
        }

        if notify_threshold:
            payload["notify_threshold"] = notify_threshold

        url = f"{self.base_url}/event"
        json_data = json.dumps(payload).encode('utf-8')

        request = Request(
            url,
            data=json_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urlopen(request, timeout=10) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return response_data
        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                raise Exception(f"HTTP {e.code}: {error_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                raise Exception(f"HTTP {e.code}: {error_body}")
        except URLError as e:
            raise Exception(f"Network error: {e.reason}")

    def health_check(self) -> dict:
        """
        Check if API is healthy.

        Returns:
            Health status
        """
        request = Request(f"{self.base_url}/health")
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode('utf-8'))
        except (HTTPError, URLError) as e:
            raise Exception(f"Health check failed: {e}")


def print_response(response: dict, success: bool = True):
    """Print formatted response."""
    symbol = "✓" if success else "✗"
    msg = response.get('message', str(response))
    will_notify = response.get('will_notify', 'N/A')
    priority = response.get('priority', 'N/A')
    print(f"{symbol} {msg}")
    print(f"   Will notify: {will_notify}, Priority: {priority}")


def run_tests(api_url: str = "http://localhost:8080"):
    """
    Run test event publishing.

    Args:
        api_url: API base URL
    """
    publisher = EventPublisher(api_url)

    print(f"{'='*70}")
    print("Event Publisher - Test Suite (GenericEvent)")
    print(f"{'='*70}")
    print(f"Target: {api_url}\n")

    # Health check
    try:
        health = publisher.health_check()
        print(f"✓ Service is healthy: {health.get('status')}\n")
    except Exception as e:
        print(f"✗ Service unreachable: {e}")
        print("\nMake sure the service is running:")
        print("  python main.py")
        sys.exit(1)

    print("Sending test events...\n")

    # Test 1: Price alert with threshold
    try:
        print("1. Price Alert - BTC +5.3% (HIGH priority, with threshold)")
        response = publisher.publish_event(
            event_type="price_alert",
            data={
                "symbol": "BTC/USDT",
                "price": "$45,230.50",
                "change": "+5.3%"
            },
            priority="HIGH",
            notify_threshold={"field": "change", "abs_gte": 2.0}
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 2: Price alert - will notify
    try:
        print("\n2. Price Alert - ETH -3.2% (MEDIUM priority)")
        response = publisher.publish_event(
            event_type="price_alert",
            data={
                "symbol": "ETH/USDT",
                "price": "$2,850.75",
                "change": "-3.2%"
            },
            priority="MEDIUM",
            notify_threshold={"field": "change", "abs_gte": 2.0}
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 3: Small change - won't notify
    try:
        print("\n3. Price Alert - BNB +0.8% (won't notify, below threshold)")
        response = publisher.publish_event(
            event_type="price_alert",
            data={
                "symbol": "BNB/USDT",
                "price": "$305.20",
                "change": "+0.8%"
            },
            priority="LOW",
            notify_threshold={"field": "change", "abs_gte": 2.0}
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 4: Volume spike
    try:
        print("\n4. Volume Spike - SOL 3.5x average (HIGH priority)")
        response = publisher.publish_event(
            event_type="volume_spike",
            data={
                "symbol": "SOL/USDT",
                "volume": "15,000,000",
                "avg_volume": "4,300,000",
                "spike_ratio": "3.5x"
            },
            priority="HIGH",
            notify_threshold={"field": "spike_ratio", "gte": 2.0}
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 5: RSI Alert
    try:
        print("\n5. RSI Alert - BTC RSI 75 (overbought)")
        response = publisher.publish_event(
            event_type="rsi_alert",
            data={
                "symbol": "BTC/USDT",
                "rsi": "75",
                "condition": "overbought"
            },
            priority="HIGH",
            notify_threshold={"always": True}
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 6: Whale transaction
    try:
        print("\n6. Whale Transaction - $5M BTC buy (CRITICAL)")
        response = publisher.publish_event(
            event_type="whale_transaction",
            data={
                "symbol": "BTC/USDT",
                "amount": "$5,000,000",
                "tx_hash": "0x1234567890...",
                "direction": "buy"
            },
            priority="CRITICAL"
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 7: Custom event
    try:
        print("\n7. Custom Event - Market sentiment")
        response = publisher.publish_event(
            event_type="market_sentiment",
            data={
                "sentiment": "bullish",
                "fear_greed_index": "85",
                "change": "from neutral to greed"
            },
            priority="MEDIUM"
        )
        print_response(response)
    except Exception as e:
        print(f"✗ Failed: {e}")

    print(f"\n{'='*70}")
    print("Test suite completed!")
    print(f"{'='*70}\n")


def interactive_mode(api_url: str = "http://localhost:8080"):
    """
    Interactive mode for manual event publishing.

    Args:
        api_url: API base URL
    """
    publisher = EventPublisher(api_url)

    print(f"{'='*70}")
    print("Event Publisher - Interactive Mode")
    print(f"{'='*70}\n")

    print("Enter event details (or 'q' to quit):\n")

    while True:
        try:
            event_type = input("Event type: ").strip()
            if event_type == 'q':
                break

            print("Data (as JSON, e.g., {\"symbol\": \"BTC/USDT\", \"price\": \"$45000\"}):")
            data_str = input().strip()
            data = json.loads(data_str) if data_str else {}

            priority = input("Priority (LOW/MEDIUM/HIGH/CRITICAL) [MEDIUM]: ").strip().upper() or "MEDIUM"

            print("Notify threshold (optional, as JSON) [press Enter to skip]:")
            threshold_str = input().strip()
            threshold = json.loads(threshold_str) if threshold_str else None

            response = publisher.publish_event(
                event_type=event_type,
                data=data,
                priority=priority,
                notify_threshold=threshold
            )
            print_response(response)
            print()

        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Parse command line args
    api_url = "http://localhost:8080"
    mode = "test"

    if len(sys.argv) > 1:
        if sys.argv[1] in ["-i", "--interactive"]:
            mode = "interactive"
        elif sys.argv[1] in ["-h", "--help"]:
            print("Usage: python test_publisher.py [OPTIONS]")
            print("\nOptions:")
            print("  -i, --interactive    Interactive mode")
            print("  -u, --url URL       API URL (default: http://localhost:8080)")
            print("  -h, --help          Show this help")
            print("\nDefault: Run automated test suite")
            sys.exit(0)
        elif sys.argv[1] in ["-u", "--url"] and len(sys.argv) > 2:
            api_url = sys.argv[2]

    # Run appropriate mode
    if mode == "interactive":
        interactive_mode(api_url)
    else:
        run_tests(api_url)
