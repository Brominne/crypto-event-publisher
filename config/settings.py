"""
Configuration management.
Zero external dependencies - uses standard library only.
"""
import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class Config:
    """
    Simple configuration management.

    Loads from environment variables and optional config file.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Optional path to JSON config file
        """
        self._config: Dict[str, Any] = {}

        # Load from file if provided
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)

        # Environment variables override file config
        self._load_from_env()

    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                self._config = json.load(f)
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Discord
        if webhook := os.getenv("DISCORD_WEBHOOK_URL"):
            self._config["discord_webhook_url"] = webhook

        # Logging
        if log_level := os.getenv("LOG_LEVEL"):
            self._config["log_level"] = log_level

        # Market data
        if exchange := os.getenv("EXCHANGE"):
            self._config["exchange"] = exchange

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def get_required(self, key: str) -> Any:
        """
        Get required configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            ValueError: If key not found
        """
        if key not in self._config:
            raise ValueError(f"Required configuration '{key}' not found")
        return self._config[key]

    @property
    def discord_webhook_url(self) -> Optional[str]:
        """Get Discord webhook URL (optional)."""
        return self.get("discord_webhook_url")

    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.get("log_level", "INFO")

    @property
    def exchange(self) -> str:
        """Get exchange name."""
        return self.get("exchange", "binance")


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup logging configuration.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
