"""
HTTP API for event ingestion.
Zero external dependencies - uses Python standard library only.

Universal endpoint: POST /event
All event types use the same GenericEvent class!
"""
import asyncio
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional

from core.generic_event import GenericEvent


logger = logging.getLogger(__name__)


class EventAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for event API."""

    # Class variables
    event_publisher: Optional[Callable] = None
    event_loop: Optional[asyncio.AbstractEventLoop] = None

    def log_message(self, format, *args):
        """Override to use Python logging instead of printing to stderr."""
        logger.info("%s - %s" % (self.address_string(), format % args))

    def _send_json_response(self, status_code: int, data: dict) -> None:
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error_response(self, status_code: int, message: str) -> None:
        """Send error response."""
        self._send_json_response(status_code, {"error": message})

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self._send_json_response(200, {
                "status": "healthy",
                "service": "crypto-alert-system"
            })
        elif self.path == '/':
            self._send_json_response(200, {
                "service": "Crypto Alert System API",
                "version": "3.0",
                "usage": "POST /event with JSON body: {\"event_type\": \"...\", \"data\": {...}, \"priority\": \"HIGH\"}",
                "endpoints": {
                    "POST /event": "Universal endpoint - all events use GenericEvent",
                    "GET /health": "Health check"
                },
                "example": {
                    "event_type": "price_alert",
                    "data": {"symbol": "BTC/USDT", "price": "$45,000", "change": "+5.3%"},
                    "priority": "HIGH",
                    "notify_threshold": {"field": "change", "abs_gte": 2.0}
                }
            })
        else:
            self._send_error_response(404, "Endpoint not found")

    def do_POST(self):
        """Handle POST requests - Universal event endpoint."""
        if not self.event_publisher:
            self._send_error_response(500, "Event publisher not configured")
            return

        # Only one endpoint needed!
        if self.path != '/event':
            self._send_error_response(404, f"Endpoint not found. Use POST /event")
            return

        # Parse request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_error_response(400, "Empty request body")
            return

        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_error_response(400, "Invalid JSON")
            return

        # Handle the event
        self._handle_universal_event(data)

    def _handle_universal_event(self, data: dict) -> None:
        """
        Universal event handler - uses GenericEvent for everything!

        Expected JSON format:
        {
            "event_type": "price_alert",
            "data": {
                "symbol": "BTC/USDT",
                "price": "$45,230.50",
                "change": "+5.3%"
            },
            "priority": "HIGH",  // Optional: LOW, MEDIUM, HIGH, CRITICAL
            "notify_threshold": {  // Optional: notification rules
                "field": "change",
                "abs_gte": 2.0
            }
        }
        """
        try:
            event_type = data.get('event_type')
            event_data = data.get('data', {})
            priority = data.get('priority', 'MEDIUM')
            notify_threshold = data.get('notify_threshold')

            if not event_type:
                self._send_error_response(400, "Missing 'event_type' field")
                return

            # Create generic event
            try:
                event = GenericEvent(
                    event_type=event_type,
                    data=event_data,
                    priority=priority,
                    notify_threshold=notify_threshold
                )
            except Exception as e:
                self._send_error_response(400, f"Error creating event: {str(e)}")
                return

            # Publish to event bus
            # Use run_coroutine_threadsafe to schedule in the main event loop
            if self.event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.event_publisher(event),
                    self.event_loop
                )
            else:
                raise RuntimeError("Event loop not configured")

            # Success response
            self._send_json_response(200, {
                "status": "success",
                "message": f"Event '{event_type}' published successfully",
                "event_type": event_type,
                "will_notify": event.should_notify(),
                "priority": event.priority.name
            })

        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
            self._send_error_response(500, f"Internal error: {str(e)}")


class EventAPIServer:
    """HTTP server for event API."""

    def __init__(self, host: str = 'localhost', port: int = 8080, event_publisher: Optional[Callable] = None):
        """
        Initialize API server.

        Args:
            host: Server host
            port: Server port
            event_publisher: Async function to publish events to event bus
        """
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self._running = False

        # Set the event publisher and event loop on the handler class
        EventAPIHandler.event_publisher = event_publisher
        EventAPIHandler.event_loop = None  # Will be set in start()

    async def start(self) -> None:
        """Start the HTTP server."""
        self.server = HTTPServer((self.host, self.port), EventAPIHandler)
        self._running = True

        # Store the event loop so HTTP handlers can schedule tasks on it
        EventAPIHandler.event_loop = asyncio.get_running_loop()

        logger.info(f"Event API server started on http://{self.host}:{self.port}")
        print(f"✓ Event API listening on http://{self.host}:{self.port}")
        print(f"  POST http://{self.host}:{self.port}/event")
        print(f"  GET  http://{self.host}:{self.port}/health")
        print(f"\n  All events use GenericEvent - no registration needed!\n")

        # Run server in executor to avoid blocking event loop
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._serve_forever)

    def _serve_forever(self) -> None:
        """Serve requests until stopped."""
        while self._running:
            self.server.handle_request()

    async def stop(self) -> None:
        """Stop the server."""
        self._running = False
        if self.server:
            self.server.server_close()
            logger.info("Event API server stopped")
