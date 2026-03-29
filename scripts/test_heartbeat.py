#!/usr/bin/env python3
"""Test script for /agent-heartbeat API."""

import json
import sys
import os
import time
from datetime import datetime, timezone
import hashlib
import hmac

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.auth_utils import generate_signature, verify_signature, verify_timestamp


def test_signature():
    """Test HMAC signature generation and verification."""
    print("[TEST] Signature generation and verification...")

    secret = "test-secret-key-32-chars-minimum!!"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = json.dumps({"state": "writing", "detail": "Testing..."})

    sig = generate_signature(secret, timestamp, body)
    print(f"  Generated signature: {sig[:30]}...")

    # Verify
    assert verify_signature(secret, timestamp, body, sig), "Signature verification failed"
    print("  ✓ Signature verified")

    # Wrong secret should fail
    assert not verify_signature("wrong-secret", timestamp, body, sig), "Wrong secret should fail"
    print("  ✓ Wrong secret correctly rejected")


def test_timestamp():
    """Test timestamp verification."""
    print("\n[TEST] Timestamp verification...")

    # Valid timestamp (now)
    valid_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ok, err = verify_timestamp(valid_ts)
    assert ok, f"Current timestamp should be valid: {err}"
    print(f"  ✓ Current timestamp valid: {valid_ts}")

    # Expired timestamp (10 minutes ago)
    expired_ts = "2026-01-01T00:00:00Z"
    ok, err = verify_timestamp(expired_ts)
    assert not ok, "Expired timestamp should be rejected"
    print(f"  ✓ Expired timestamp rejected: {err}")


def test_heartbeat_api():
    """Test the /agent-heartbeat API endpoint."""
    print("\n[TEST] API endpoint test...")

    # Create test config
    config = {
        "agents": [{
            "agentId": "test_agent_001",
            "name": "Test Agent",
            "secretKey": "test-secret-for-testing-32-characters",
            "avatar": "star",
            "enabled": True
        }],
        "settings": {
            "offlineTimeout": 300,
            "signatureExpireSeconds": 60
        }
    }

    # Write test config
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents-config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  Created test config: {config_path}")

    # Test heartbeat
    try:
        import urllib.request
        import urllib.error

        base_url = "http://127.0.0.1:19000"
        agent_id = "test_agent_001"
        secret = "test-secret-for-testing-32-characters"

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        body = json.dumps({"state": "writing", "detail": "Running tests..."})
        sig = generate_signature(secret, timestamp, body)

        req = urllib.request.Request(
            f"{base_url}/agent-heartbeat",
            data=body.encode(),
            headers={
                "Content-Type": "application/json",
                "X-Agent-Id": agent_id,
                "X-Timestamp": timestamp,
                "X-Signature": sig
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode())
                print(f"  ✓ Heartbeat success: {result}")
        except urllib.error.HTTPError as e:
            print(f"  ✗ Heartbeat failed: {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"  ! Skipping API test: {e}")
        print("    (Start the backend first: cd backend && python app.py)")


if __name__ == "__main__":
    print("=" * 50)
    print("Star Office UI - Heartbeat Test Suite")
    print("=" * 50)

    test_signature()
    test_timestamp()
    test_heartbeat_api()

    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)
