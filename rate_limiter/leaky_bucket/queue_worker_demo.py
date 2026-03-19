#!/usr/bin/env python3
"""
Leaky-bucket style: FIFO queue (deque) + a worker that drains at a fixed rate.
The worker loop is the predictable stream — not cron.
Run: python queue_worker_demo.py
"""

from collections import deque
import time
import threading

queue = deque()
rate = 2.0

def worker():
    while True:
        if not queue:
            time.sleep(0.1)
            continue
        item = queue.popleft()
        print(f"  Processed at {time.time():.1f}: {item}")
        time.sleep(rate)

def main():
    threading.Thread(target=worker, daemon=True).start()
    print(f"Worker draining at {rate} items/sec (sleep {1/rate}s between items)")
    print("-" * 50)

    for i in range(5):
        queue.append(f"req-{i}")
        print(f"Enqueued req-{i} (queue size {len(queue)})")
        time.sleep(0.2)

    print("-" * 50)
    print("Waiting for queue to drain...")
    while queue:
        time.sleep(0.1)
    time.sleep(0.5)
    print("Done.")


if __name__ == "__main__":
    main()