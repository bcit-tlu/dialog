# Step 6 — Redis in-cluster

**Size:** Small · **Depends on:** Step 4 · **Blocks:** Step 9 (worker queue)

## Goal

Provide a Redis instance for the async job queue that the API enqueues to and the worker
dequeues from.

## Why

The pipeline is asynchronous: `POST /jobs` enqueues work in Redis; the worker consumes it.
Without Redis the worker has nothing to pull from. In compose this is the `redis` service;
in K8s it needs a Deployment/StatefulSet + Service (or a managed Redis).

## Tasks

1. Add a Redis workload (gated by `redis.enabled`):
   - Option A (simple): `Deployment` + `Service` using `redis:7-alpine` (matches compose).
   - Option B: depend on the Bitnami Redis subchart for persistence/HA.
2. Expose it as a Service (e.g. `dialog-redis:6379`) and inject `REDIS_URL` into api + worker
   pods (Step 9).
3. Decide on persistence:
   - Job queue is transient — an ephemeral Redis is acceptable for now (document the
     trade-off: in-flight jobs lost on Redis restart).
   - Add a small PVC if durability is desired later.
4. `values.yaml` additions under `redis:` — `enabled`, `url` (for external Redis fallback),
   `image`, `persistence`.

## Files created

- `charts/backend/templates/redis-deployment.yaml` (+ service), or a subchart dependency

## Files touched

- `charts/backend/values.yaml`

## Acceptance criteria

- With `redis.enabled=true`, a Redis pod is `Ready` and reachable at `dialog-redis:6379`.
- `REDIS_URL` resolves from within an api/worker pod (`redis-cli -u $REDIS_URL ping` → PONG).
- Setting `redis.enabled=false` + `redis.url=<external>` skips the in-cluster Redis.
