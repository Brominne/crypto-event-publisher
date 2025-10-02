# Quick Start Guide - GenericEvent (Maximum Simplicity!)

## How It Works Now (Ultra Simple!)

**No event classes needed!** Just send JSON with:
- `event_type` - any string you want
- `data` - your event data
- `priority` - LOW, MEDIUM, HIGH, or CRITICAL
- `notify_threshold` - optional notification rules

## Simple Example

```bash
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "price_alert",
    "data": {
      "symbol": "BTC/USDT",
      "price": "$45,230.50",
      "change": "+5.3%"
    },
    "priority": "HIGH",
    "notify_threshold": {
      "field": "change",
      "abs_gte": 2.0
    }
  }'
```

**That's it!** No class definitions, no registration, no extra code.

## All Fields Explained

```json
{
  "event_type": "price_alert",    // Any string - describes the event
  "data": {                         // Your event data (shown in Discord)
    "symbol": "BTC/USDT",
    "price": "$45,000",
    "change": "+5.3%"
  },
  "priority": "HIGH",               // LOW, MEDIUM, HIGH, or CRITICAL
  "notify_threshold": {             // Optional: when to send notification
    "field": "change",              // Which data field to check
    "abs_gte": 2.0                  // Notify if abs(change) >= 2.0
  }
}
```

## Notification Threshold Rules

Control when notifications are sent:

### Always notify
```json
"notify_threshold": {"always": true}
```

### Never notify
```json
"notify_threshold": {"never": true}
```

### Conditional (field-based)
```json
// Notify if data["value"] > 100
"notify_threshold": {"field": "value", "gt": 100}

// Notify if data["value"] >= 50
"notify_threshold": {"field": "value", "gte": 50}

// Notify if data["value"] < 10
"notify_threshold": {"field": "value", "lt": 10}

// Notify if abs(data["change"]) >= 2.0
"notify_threshold": {"field": "change", "abs_gte": 2.0}

// Notify if abs(data["change"]) > 5.0
"notify_threshold": {"field": "change", "abs_gt": 5.0}
```

## More Examples

### Volume Spike
```bash
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "volume_spike",
    "data": {
      "symbol": "SOL/USDT",
      "volume": "15,000,000",
      "spike_ratio": "3.5x"
    },
    "priority": "HIGH",
    "notify_threshold": {"field": "spike_ratio", "gte": 2.0}
  }'
```

### RSI Alert
```bash
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "rsi_alert",
    "data": {
      "symbol": "ETH/USDT",
      "rsi": "75",
      "condition": "overbought"
    },
    "priority": "HIGH",
    "notify_threshold": {"always": true}
  }'
```

### Whale Transaction
```bash
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "whale_transaction",
    "data": {
      "symbol": "BTC/USDT",
      "amount": "$5,000,000",
      "direction": "buy",
      "tx_hash": "0x1234..."
    },
    "priority": "CRITICAL"
  }'
```

### Custom Event (Anything You Want!)
```bash
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "my_custom_alert",
    "data": {
      "foo": "bar",
      "whatever": "you want",
      "any": "structure"
    },
    "priority": "MEDIUM"
  }'
```

## Python Client

```python
from tests.test_publisher import EventPublisher

publisher = EventPublisher("http://localhost:8080")

# Price alert
publisher.publish_event(
    event_type="price_alert",
    data={"symbol": "BTC/USDT", "price": "$45,000", "change": "+5.3%"},
    priority="HIGH",
    notify_threshold={"field": "change", "abs_gte": 2.0}
)

# Custom event
publisher.publish_event(
    event_type="anything_you_want",
    data={"any": "data", "structure": "works"},
    priority="MEDIUM"
)
```

## Running the System

**Terminal 1 - Start service:**
```bash
python main.py
```

**Terminal 2 - Send events:**
```bash
# Run test suite
python tests/test_publisher.py

# Interactive mode
python tests/test_publisher.py --interactive
```

## Priority Levels

- **LOW** - Informational, gray color in Discord
- **MEDIUM** - Normal events, blue color
- **HIGH** - Important events, orange color
- **CRITICAL** - Urgent events, red color

## Default Behavior

If you omit fields:
- `priority` defaults to `"MEDIUM"`
- `notify_threshold` defaults to `{"always": true}` (always notify)
- `data` defaults to empty `{}`

## Minimal Example

```bash
# This works! (event_type is the only required field)
curl -X POST http://localhost:8080/event \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test"}'
```

## No Code Changes Needed!

Want a new event type? **Just send it!** No need to:
- ❌ Define a class
- ❌ Register anything
- ❌ Restart the service

Everything is configured via JSON at runtime.
