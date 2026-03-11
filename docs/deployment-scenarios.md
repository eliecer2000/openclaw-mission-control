# Deployment Scenarios

This guide covers the three supported deployment topologies for Mission Control and OpenClaw.
Each scenario includes the relevant environment variables with example values.

---

## Scenario 1: Local installation with SSH tunnel

Everything runs on a single remote machine. You access the UI and API through SSH port
forwarding.

```
┌─────────────────────────────────────────────────┐
│  Remote machine                                 │
│                                                 │
│   Frontend (:3000)  ◄──┐                        │
│   Backend  (:8000)  ◄──┼── SSH tunnel from      │
│   Gateway  (:18789)    │    your laptop          │
│   Agent(s)             │                        │
│                        │                        │
└────────────────────────┘                        │
                                                  │
┌──────────────┐                                  │
│  Your laptop │──── ssh -L 3000:localhost:3000 ──┘
│              │──── ssh -L 8000:localhost:8000
└──────────────┘
```

**Ports to tunnel:**

| Port  | Service  | Why                                      |
|-------|----------|------------------------------------------|
| 3000  | Frontend | Access the Mission Control UI             |
| 8000  | Backend  | API calls from the browser (auto mode)   |

The gateway and agents communicate over `localhost` on the remote machine, so no extra
tunneling is needed for them.

### Environment variables

**backend/.env**

```env
BASE_URL=http://localhost:8000
# INTERNAL_BASE_URL is not needed — everything is on the same host
CORS_ORIGINS=http://localhost:3000
```

**frontend/.env**

```env
NEXT_PUBLIC_API_URL=auto
```

When `NEXT_PUBLIC_API_URL=auto`, the frontend resolves the backend URL from the browser's
current host and port. Since you access the UI via `localhost:3000` through the SSH tunnel,
the API calls go to `localhost:8000` — also tunneled.

---

## Scenario 2: ALB / reverse proxy with multiple instances

Mission Control sits behind an Application Load Balancer (or any reverse proxy like nginx)
that terminates TLS. OpenClaw gateways and agents may run on separate hosts or containers.

```
┌──────────┐    HTTPS :443     ┌────────────┐
│  Browser  │─────────────────►│  ALB/Proxy  │
└──────────┘                   └─────┬──┬────┘
                                     │  │
                          ┌──────────┘  └──────────┐
                          ▼                         ▼
                   Frontend :3000            Backend :8000
                                                │
                          ┌─────────────────────┘
                          │  INTERNAL_BASE_URL
                          │  (callback to backend)
                          ▼
                      Gateway ◄──── Agent(s)
                                      │
                                      └── heartbeat via BASE_URL
                                          (public, through ALB)
```

The key distinction here is between **public** and **internal** URLs:

- `BASE_URL` — the public URL that agents use to reach the backend (goes through the ALB).
- `INTERNAL_BASE_URL` — the URL the gateway uses to call back to the backend over the
  internal network, bypassing the ALB.

### Environment variables

**backend/.env**

```env
BASE_URL=https://mc.example.com
INTERNAL_BASE_URL=http://backend:8000
CORS_ORIGINS=https://mc.example.com
```

**frontend/.env**

```env
NEXT_PUBLIC_API_URL=https://mc.example.com
```

**compose.yml** (or equivalent orchestrator config)

```yaml
frontend:
  environment:
    NEXT_PUBLIC_API_URL: https://mc.example.com
```

> **Tip:** When using `docker compose`, `INTERNAL_BASE_URL=http://backend:8000` works because
> Docker's internal DNS resolves the `backend` service name. If the gateway runs outside
> Docker, use the host's internal IP instead.

---

## Scenario 3: Mission Control on machine A, OpenClaw on machine B

Mission Control (frontend + backend) runs on machine **A**. The OpenClaw gateway and agents
run on a separate machine **B**. Machine A can reach B and vice versa over the network.

```
┌─────────────────────────┐         ┌─────────────────────────┐
│  Machine A (10.0.0.1)   │         │  Machine B (10.0.0.2)   │
│                         │         │                         │
│  Frontend :3000         │         │  Gateway :18789         │
│  Backend  :8000 ◄───────┼─────────┼── Agent heartbeats      │
│         │               │         │                         │
│         └───────────────┼────────►│  WS connection to       │
│           gateway RPC   │         │  gateway :18789         │
└─────────────────────────┘         └─────────────────────────┘
```

The backend needs to reach the gateway on machine B via WebSocket. The gateway (and agents
on B) need to reach the backend on machine A via HTTP for callbacks and heartbeats.

### Environment variables

**backend/.env (on machine A)**

```env
BASE_URL=http://10.0.0.1:8000
INTERNAL_BASE_URL=http://10.0.0.1:8000
CORS_ORIGINS=http://10.0.0.1:3000
```

**frontend/.env (on machine A)**

```env
NEXT_PUBLIC_API_URL=http://10.0.0.1:8000
```

**Gateway URL (configured in Mission Control UI)**

```
ws://10.0.0.2:18789
```

Here both `BASE_URL` and `INTERNAL_BASE_URL` point to machine A's IP so the gateway on
machine B can call back to the backend. If you access the UI from a different machine,
set `CORS_ORIGINS` to include that origin as well.

> **Note:** When the gateway URL points to `localhost` or `127.0.0.1`, Mission Control shows
> a warning in the UI — this is expected, since a local address would not be reachable from
> the backend when it runs on a different machine.

---

## Environment variable reference

| Variable | Where | Purpose |
|----------|-------|---------|
| `BASE_URL` | backend | Public URL of the backend. Used in agent-facing messages and heartbeat endpoints. Must be reachable by agents. |
| `INTERNAL_BASE_URL` | backend | Internal URL for gateway-to-backend callbacks. Falls back to `BASE_URL` when empty. |
| `CORS_ORIGINS` | backend | Comma-separated list of allowed origins for CORS. Should include the frontend URL. |
| `NEXT_PUBLIC_API_URL` | frontend | Backend URL for browser API calls. Set to `auto` to derive from the current page URL, or provide an explicit URL. |
| `NEXT_PUBLIC_ALLOWED_DEV_ORIGINS` | frontend | Comma-separated list of allowed dev origins for the Next.js dev server. Defaults to `localhost,127.0.0.1`. |
| `GATEWAY_RPC_TIMEOUT_SECONDS` | backend | Timeout for WebSocket RPC calls to the gateway. Default: `30`. |
| `AGENT_OFFLINE_CHECK_INTERVAL_SECONDS` | backend | How often the backend checks for agents that stopped sending heartbeats. Default: `60`. |
| `SSE_POLL_INTERVAL_SECONDS` | backend | Interval for the SSE event stream polling loop. Default: `2`. |
