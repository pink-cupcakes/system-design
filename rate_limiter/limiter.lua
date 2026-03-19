-- Redis Lua script: run inside Redis via EVAL for atomic rate limiting.
-- No classes, no require(), no Redis client — only redis.call().
--
-- Usage (redis-cli):
--   EVAL "$(cat limiter.lua)" 1 ratelimit:auth_service 10 60 1699123456
--
-- KEYS[1]: base key for this limit (e.g. "ratelimit:auth_service")
-- ARGV[1]: max requests allowed (limit)
-- ARGV[2]: window in seconds
-- ARGV[3]: current Unix time (from caller, so script is deterministic)

local base_key = KEYS[1]
local limit = tonumber(ARGV[1])
local window_sec = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = math.floor(now / window_sec)
local key = base_key .. ":" .. bucket

local count = redis.call("GET", key)
if count == false then
  count = 0
else
  count = tonumber(count)
end

if count >= limit then
  return {0, count}
end

redis.call("INCR", key)
if count == 0 then
  redis.call("PEXPIRE", key, window_sec * 1000)
end

return {1, count + 1}
