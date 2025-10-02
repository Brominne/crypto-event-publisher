#!/usr/bin/env python3
"""
Service runner - Production entry point.
Starts the alert system with proper configuration and logging.
"""
import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main


def check_environment():
    """Check environment and configuration."""
    issues = []

    # Check if Discord webhook is configured
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    config_file = "config.json"

    if not webhook and not os.path.exists(config_file):
        issues.append("⚠ Discord webhook not configured")
        issues.append("  Set DISCORD_WEBHOOK_URL env var or create config.json")

    return issues


def print_banner():
    """Print startup banner."""
    banner = """
╔════════════════════════════════════════════════════════════╗
║           Crypto Trading Alert System - v1.0              ║
║                      Service Mode                          ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


if __name__ == "__main__":
    print_banner()

    # Check environment
    issues = check_environment()
    if issues:
        for issue in issues:
            print(issue)
        print()

    # Start service
    try:
        print("Starting service...\n")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Service stopped gracefully")
    except Exception as e:
        print(f"\n✗ Service crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
