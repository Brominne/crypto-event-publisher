#!/usr/bin/env python3
"""Quick test to verify the fix works."""
import subprocess
import time
import sys
import json
from urllib.request import Request, urlopen

def test_api():
    """Test the API with a simple request."""
    print("Testing API endpoint...")

    try:
        # Send a price alert
        url = "http://localhost:8080/events/price_alert"
        data = json.dumps({
            "symbol": "BTC/USDT",
            "price": 45230.50,
            "change_percent": 5.3
        }).encode('utf-8')

        request = Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Success: {result['message']}")
            return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Make sure the service is running in another terminal:")
    print("  python main.py")
    print()
    input("Press Enter when ready...")
    print()

    if test_api():
        print("\n✓ Test passed! Check the service terminal for event output.")
    else:
        print("\n✗ Test failed. Check if the service is running.")
        sys.exit(1)
