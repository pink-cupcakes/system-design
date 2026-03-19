#!/usr/bin/env python3
"""
Test the Redis + Lua rate limiter. Your app can be in any language (Python, Go, etc.);
this script is the "caller" that sends the Lua script to Redis via EVAL.

Run: pip install redis && python test_limiter.py
Requires: Redis running locally (redis-server) on default port 6379.
"""

import os
import time
import redis

# Config (could come from ENV)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
LIMIT = 10
WINDOW_SEC = 20
SERVICE_KEY = "auth_service_rate_limit"

# Load Lua script once at import; reused for every EVAL
_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "limiter.lua")
with open(_SCRIPT_PATH) as _f:
    LIMITER_SCRIPT = _f.read()

def main():
    r = redis.from_url(REDIS_URL)

    print(f"Rate limit: {LIMIT} requests per {WINDOW_SEC}s window")
    print(f"Key: {SERVICE_KEY}")
    print("-" * 50)

    # Simulate 15 requests
    for i in range(10000):
        now = int(time.time())
        # EVAL script numkeys key [arg1 arg2 arg3 ...]
        result = r.eval(LIMITER_SCRIPT, 1, SERVICE_KEY, LIMIT, WINDOW_SEC, now)
        allowed, count = result
        status = "ALLOWED " if allowed else "LIMITED "
        print(f"  Request {i+1:2}: {status} -> count = {count}")
        time.sleep(0.5)  # tiny delay so they're in same second/window

    print("-" * 50)
    print("First 10 allowed (1), next 5 limited (0). Server can be Python, Go, Node, Lambda — not Lua.")

if __name__ == "__main__":
    main()
