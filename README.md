# Crypto Trading Alert System - MVP

Modular trade alert system for detecting significant market moves and sending Discord notifications.

## Phase 1: Foundation ✓

Zero external dependencies - uses Python standard library only.

### Architecture

```
core/                    # Zero dependencies on other modules
├── event.py            # Event interface and base classes
├── event_bus.py        # Pub/sub event routing
└── listener.py         # Listener interface

notifications/          # Depends on: core only
└── discord_handler.py  # Discord webhook notifications (stdlib only)

market/                 # Depends on: core only
└── (Phase 2)

config/
└── settings.py         # Configuration management
```

### Features

- **Event System**: Abstract base class for extensible event types
- **Event Bus**: Async pub/sub pattern for decoupled event routing
- **Event Filters**: Pluggable filters (priority, custom logic)
- **Discord Notifications**: Webhook-based (no bot token needed)
- **HTTP API**: REST endpoints for event ingestion
- **Continuous Service**: Runs indefinitely, processing events in real-time
- **Test Publisher**: Standalone script to trigger test events
- **Zero External Dependencies**: Phase 1 uses only Python stdlib

## Quick Start

### 1. Setup

```bash
# Clone/navigate to project
cd crypto-trading-system

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Phase 1 requires no dependencies!
# (Phase 2 will add ccxt, websockets, aiohttp)
```

### 2. Configure Discord Webhook

#### Get your webhook URL:
1. Open Discord → Server Settings → Integrations → Webhooks
2. Create webhook → Copy URL
3. Configure:

**Option A: Environment variable**
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
```

**Option B: Config file**
```bash
cp config.example.json config.json
# Edit config.json and add your webhook URL
```

### 3. Run Service (Continuous Mode)

**Start the service:**
```bash
python run_service.py
# OR
python main.py
```

The service will:
- Run continuously, listening for events
- Start HTTP API on `http://localhost:8080`
- Process events and send notifications
- Run until you press Ctrl+C

**In a separate terminal, send test events:**
```bash
# Run automated test suite
python tests/test_publisher.py

# OR interactive mode
python tests/test_publisher.py --interactive
```

### 4. Using the Universal API

**ONE endpoint for ALL events:**

```bash
# Universal endpoint format:
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "EVENT_NAME",
    "params": { ... }
  }'

# Examples:
# Price alert
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "price_alert",
    "params": {
      "symbol": "BTC/USDT",
      "price": 45230.50,
      "change_percent": 5.3
    }
  }'

# RSI alert
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "rsi_alert",
    "params": {
      "symbol": "ETH/USDT",
      "rsi": 75
    }
  }'

# Whale transaction
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "whale_transaction",
    "params": {
      "symbol": "BTC/USDT",
      "amount": 5000000,
      "tx_hash": "0x123abc",
      "direction": "buy"
    }
  }'

# List available events
curl http://localhost:8080/events

# Health check
curl http://localhost:8080/health
```

## Creating New Event Types

**Step 1: Define event class in `main.py`**

```python
from core.event import Event, EventPriority
from core.event_registry import EventRegistry

@EventRegistry.register("support_break")  # <-- Register with decorator
class SupportBreakEvent(Event):
    def __init__(self, symbol: str, price: float, support_level: float):
        super().__init__(
            event_type="support_break",
            data={
                "symbol": symbol,
                "price": f"${price:,.2f}",
                "support": f"${support_level:,.2f}"
            },
            priority=EventPriority.HIGH
        )

    def should_notify(self) -> bool:
        return True  # Always notify on support breaks
```

**Step 2: Use it immediately!**

```bash
# No code changes needed - it's automatically available!
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "support_break",
    "params": {
      "symbol": "BTC/USDT",
      "price": 42000,
      "support_level": 43000
    }
  }'
```

**That's it!** The registry handles everything automatically.

## Creating Custom Listeners

```python
from core.listener import EventListener
from core.event import Event

class EmailListener(EventListener):
    def __init__(self, email_address: str):
        super().__init__(event_types=["price_alert", "volume_spike"])
        self.email = email_address

    def get_name(self) -> str:
        return "EmailListener"

    async def handle(self, event: Event) -> None:
        # Your email logic here
        print(f"Sending email to {self.email}: {event}")

# Register it
event_bus.register_listener(EmailListener("you@example.com"))
```

## Event Filters

```python
from core.event import PriorityFilter, EventPriority

# Only handle HIGH and CRITICAL events
high_priority_discord = DiscordWebhookHandler(
    webhook_url=webhook,
    filters=[PriorityFilter(EventPriority.HIGH)]
)
```

## Next Steps - Phase 2

Phase 2 will add:
1. Market data integration (ccxt)
2. Real-time WebSocket feeds
3. Price change detector
4. Volume spike detector
5. Configurable thresholds

## Test Publisher Script

The `test_publisher.py` script lets you trigger events on a running service:

**Automated test suite:**
```bash
python tests/test_publisher.py
```

Sends 6 test events demonstrating different scenarios.

**Interactive mode:**
```bash
python tests/test_publisher.py --interactive
```

Manually craft and send events.

**Custom API URL:**
```bash
python tests/test_publisher.py --url http://192.168.1.100:8080
```

## Project Structure

```
crypto-trading-system/
├── core/                   # Event system (no dependencies)
│   ├── event.py           # Event base classes
│   ├── event_bus.py       # Pub/sub routing
│   └── listener.py        # Listener interface
├── api/                    # HTTP API (depends on: core)
│   └── http_api.py        # Event ingestion endpoint
├── market/                 # Market data (depends on: core)
├── notifications/          # Notification handlers (depends on: core)
│   └── discord_handler.py # Discord webhook
├── config/                 # Configuration
│   └── settings.py        # Config management
├── tests/                  # Test utilities
│   └── test_publisher.py  # Event publisher script
├── main.py                 # Service entry point
├── run_service.py          # Production runner
├── requirements.txt        # Python dependencies
├── config.example.json     # Example config
└── .env.example           # Example environment variables
```

## Design Principles

1. **Minimal Dependencies**: Each module only imports from `core`
2. **Event-Driven**: Loose coupling via event bus
3. **Extensible**: Easy to add new event types and listeners
4. **Async First**: Built on asyncio for concurrent processing
5. **Type Safety**: Uses dataclasses and type hints
