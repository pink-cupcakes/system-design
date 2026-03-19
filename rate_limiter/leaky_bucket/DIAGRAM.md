# Queue worker demo – flow

Single FIFO queue (deque) and one worker that drains at a fixed rate. No cron; the worker loop + sleep is the predictable stream.

## Data flow

```mermaid
flowchart TB
    subgraph main["Main thread"]
        A[main]
    end

    subgraph queue["Queue"]
        Q[(deque FIFO)]
    end

    subgraph worker["Worker thread"]
        W[worker loop]
    end

    A -->|append| Q
    Q -->|popleft| W
    W -->|process then sleep 1/rate| W
```

- **Main** enqueues items with `queue.append(item)`.
- **deque** holds them in FIFO order; worker consumes from the left.
- **Worker** runs in a separate thread: if non-empty, `popleft()` → process → `sleep(1/rate)` → repeat. The sleep makes the drain rate predictable (e.g. 2 items/sec when `rate = 2.0`).

## Sequence (one item)

```mermaid
sequenceDiagram
    participant M as main
    participant Q as deque
    participant W as worker

    M->>Q: append
    W->>Q: popleft
    Q-->>W: item
    Note over W: process then sleep
    M->>Q: append
    W->>Q: popleft
    Q-->>W: item
```

Main and worker run concurrently; the worker’s rate limits how fast items leave the queue.
