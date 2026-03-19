#!/usr/bin/env python3
"""
Small demo: connect to Redis and call the Lua limiter with EVAL.
Run: python test_limiter.py  (Redis must be up, e.g. make redis)
"""

import os
import time
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
LIMIT = 10
WINDOW_SEC = 2
NUM_REQUESTS = 100
SERVICE_KEY = "auth_service_rate_limit"
SLEEP_SEC = 0.1

_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "limiter.lua")
with open(_SCRIPT_PATH) as _f:
    LIMITER_SCRIPT = _f.read()


def main():
    r = redis.from_url(REDIS_URL)
    print(f"{LIMIT} requests per {WINDOW_SEC}s window · {SERVICE_KEY}")
    print("-" * 50)

    for i in range(NUM_REQUESTS):
        now = int(time.time())
        allowed, count = r.eval(LIMITER_SCRIPT, 1, SERVICE_KEY, LIMIT, WINDOW_SEC, now)
        label = "ALLOWED " if allowed else "LIMITED "
        print(f"  {i + 1:3}: {label}  count={count}")
        if SLEEP_SEC:
            time.sleep(SLEEP_SEC)

    print("-" * 50)
    print("Done.")


if __name__ == "__main__":
    main()
