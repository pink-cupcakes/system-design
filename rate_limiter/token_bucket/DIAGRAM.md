# Rate limiter – flow and architecture

## Request flow (sequence)

```mermaid
sequenceDiagram
    participant App as App (Python/Go/Node)
    participant Redis as Redis
    participant Lua as Lua script

    App->>Redis: EVAL limiter.lua 1 <key> <limit> <window_sec> <now>
    Redis->>Lua: run script (atomic)
    Lua->>Redis: GET key (bucket counter)
    Redis-->>Lua: count
    Lua->>Lua: count < limit?
    alt allowed
        Lua->>Redis: INCR key
        Lua->>Redis: PEXPIRE key (if new)
        Lua-->>Redis: [1, count+1]
    else limited
        Lua-->>Redis: [0, count]
    end
    Redis-->>App: [allowed, count]
    App->>App: allow request or 429
```

## Fixed-window buckets (how keys work)

```mermaid
flowchart LR
    subgraph Time
        T1["t=0..59s\nbucket 0"]
        T2["t=60..119s\nbucket 1"]
        T3["t=120..179s\nbucket 2"]
    end

    subgraph Redis keys
        K1["ratelimit:auth_service:0\n→ count"]
        K2["ratelimit:auth_service:1\n→ count"]
        K3["ratelimit:auth_service:2\n→ count"]
    end

    T1 --> K1
    T2 --> K2
    T3 --> K3
```

- **Bucket** = `floor(now / window_sec)` → one key per time window.
- **Key** = `{base_key}:{bucket}`; value = request count in that window.
- After the window, the key expires (`PEXPIRE`) or a new bucket is used.

## Components

```mermaid
flowchart TB
    subgraph Your app
        API["API / Worker"]
        Client["Redis client"]
        API --> Client
    end

    subgraph Redis
        EVAL["EVAL"]
        Script["limiter.lua\n(GET → check → INCR → EXPIRE)"]
        Store[("Keys: base_key:bucket\nValues: count")]
        EVAL --> Script
        Script --> Store
    end

    Client -->|"script + key + limit, window, now"| EVAL
    EVAL -->|"[allowed, count]"| Client
```

- **App**: loads `limiter.lua` once, calls `EVAL` per request with key and ARGV.
- **Redis**: runs the script atomically; no other command runs in between.
- **Storage**: one string key per (base_key, time bucket); value = count.
