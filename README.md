# Crypto Trading Alert System

Simple, modular alert system that sends Discord notifications for crypto market events.

## Features

- ✅ **Universal Event System** - No classes needed, just JSON
- ✅ **Discord Notifications** - Webhook-based (no bot required)
- ✅ **Configurable Priority** - LOW, MEDIUM, HIGH, CRITICAL
- ✅ **Notification Thresholds** - Control when alerts trigger
- ✅ **Heartbeat Monitoring** - Auto-ping healthchecks.io
- ✅ **Zero Dependencies** - Pure Python stdlib

## Quick Start

### 1. Setup Discord Webhook

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
```

Or create `config.json`:
```json
{
  "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
}
```

### 2. Start Service

```bash
python main.py
```

### 3. Send Events

**Option A: Using test script**
```bash
python tests/test_publisher.py
```

**Option B: Using curl**
```bash
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "price_alert",
    "data": {"symbol": "BTC/USDT", "price": "$45,000", "change": "+5.3%"},
    "priority": "HIGH",
    "notify_threshold": {"field": "change", "abs_gte": 2.0}
  }'
```

**Option C: Using Python**
```python
from tests.test_publisher import EventPublisher

publisher = EventPublisher()
publisher.publish_event(
    event_type="price_alert",
    data={"symbol": "BTC/USDT", "price": "$45,000", "change": "+5.3%"},
    priority="HIGH"
)
```

## Event Format

```json
{
  "event_type": "any_string",     // Required: event identifier
  "data": {                        // Optional: your data (shown in Discord)
    "any": "structure",
    "you": "want"
  },
  "priority": "HIGH",              // Optional: LOW/MEDIUM/HIGH/CRITICAL
  "notify_threshold": {            // Optional: notification rules
    "field": "change",
    "abs_gte": 2.0
  }
}
```

## Notification Thresholds

Control when to send notifications:

```json
{"always": true}                          // Always notify (default)
{"never": true}                           // Never notify
{"field": "value", "gt": 100}             // If value > 100
{"field": "change", "abs_gte": 2.0}       // If |change| >= 2.0
```

Available operators: `gt`, `gte`, `lt`, `lte`, `abs_gt`, `abs_gte`

## Configuration

Optional `config.json`:

```json
{
  "discord_webhook_url": "https://discord.com/api/webhooks/...",
  "log_level": "INFO",
  "api_host": "localhost",
  "api_port": 8080,
  "heartbeat_url": "https://hc-ping.com/YOUR_CHECK_ID",
  "heartbeat_interval": 30
}
```

Or use environment variables:
```bash
DISCORD_WEBHOOK_URL="..."
LOG_LEVEL="INFO"
```

## Project Structure

```
crypto-trading-system/
├── core/
│   ├── event.py           # Event base class
│   ├── event_bus.py       # Pub/sub routing
│   ├── generic_event.py   # Universal event implementation
│   ├── listener.py        # Listener interface
│   └── heartbeat.py       # Health monitoring
├── api/
│   └── http_api.py        # REST API endpoint
├── notifications/
│   └── discord_handler.py # Discord webhook integration
├── config/
│   └── settings.py        # Config management
├── tests/
│   └── test_publisher.py  # Event publisher utility
├── main.py                # Service entry point
└── run_service.py         # Production runner
```

## Examples

### Price Alert
```python
publisher.publish_event(
    event_type="price_alert",
    data={"symbol": "BTC/USDT", "price": "$45,000", "change": "+5.3%"},
    priority="HIGH",
    notify_threshold={"field": "change", "abs_gte": 2.0}
)
```

### Volume Spike
```python
publisher.publish_event(
    event_type="volume_spike",
    data={"symbol": "ETH/USDT", "volume": "15M", "spike": "3.5x"},
    priority="HIGH"
)
```

### Custom Event
```python
publisher.publish_event(
    event_type="anything",
    data={"any": "data"},
    priority="MEDIUM"
)
```

## Testing

```bash
# Run all tests
python tests/test_publisher.py

# Interactive mode
python tests/test_publisher.py --interactive

# Custom URL
python tests/test_publisher.py --url http://192.168.1.100:8080
```

## API Endpoints

- `POST /event` - Send an event (universal endpoint)
- `GET /health` - Health check
- `GET /` - API info

## Design Principles

1. **Simplicity** - JSON-only interface, no code changes needed
2. **Modularity** - Core has zero dependencies on other modules
3. **Extensibility** - Add new event types with JSON
4. **Async First** - Built on asyncio for concurrent processing

## License

MIT
