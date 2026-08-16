# Tutorial 12 — Testing products, not just pages: API, Auth, Live-data & Web-quality

The earlier tutorials test **web pages** (crawl, audit, flow, route-sweep). But the products this agent tests are **API-first, auth-gated, and streaming-heavy** — a dashboard is only the tip. This tutorial covers four capability clusters that test the rest of the product:

1. **API contract** — validate REST endpoints against their OpenAPI schema, and run multi-step API workflows.
2. **Auth & session** — real login → reusable session → logout/expiry/negative-auth checks.
3. **Live data** — assert WebSocket / SSE streams are actually live, not just that the page loads.
4. **Web quality** — Core Web Vitals, device + network emulation, cross-browser.

All four are in the dashboard (their own cards), the CLI, and the ⌘K palette, and each writes an HTML/PDF/Markdown/CSV report.

---

## 1. API contract testing

Every product exposes an OpenAPI spec. Point the agent at it and it exercises each endpoint, checking the response **status** is declared and the body **validates against the response schema** (a self-contained JSON-Schema validator handles `type`/`required`/`properties`/`items`/`enum`/`nullable`/`$ref`/`oneOf`/`anyOf`/`allOf` — no extra deps).

```bash
# spec mode — validate GET endpoints (add --include-writes for POST/PUT/DELETE)
argus api test https://api.example.com --spec https://api.example.com/openapi.json
argus api test https://api.example.com --spec ./openapi.json --token "$JWT"
```

In the dashboard, the **🔌 API contract** card takes the base URL, a spec URL (or pasted inline JSON), and an optional bearer token. The result is a per-endpoint table with red rows for schema violations (e.g. `$.user.email: required property missing`).

### Multi-step API workflows

For async lifecycles (create → poll-until-Running → delete), pass a **workflow** file — an ordered list of steps with `{{variable}}` interpolation from earlier responses and a `poll` step:

```json
[
  { "name": "create VM", "method": "POST", "path": "/api/v1/vms",
    "body": { "name": "qa-vm", "template": "ubuntu-24" },
    "extract": { "vmid": "metadata.name" }, "expect": { "status": 201 } },
  { "name": "wait until Running", "method": "GET", "path": "/api/v1/vms/default/{{vmid}}",
    "poll": { "json_path": "status.phase", "equals": "Running", "timeout_ms": 60000 } },
  { "name": "delete", "method": "DELETE", "path": "/api/v1/vms/default/{{vmid}}",
    "expect": { "status": 200 } }
]
```

```bash
argus api test https://api.example.com --workflow vm-lifecycle.json --token "$JWT"
```

---

## 2. Auth & session testing

Login in these products lives in `sessionStorage` (JWT), cookies, or one-time tickets. The **🔐 Auth & session** action logs in — either by driving a **login page** in-browser or POSTing an **API login endpoint** — captures a full **storageState** (cookies + localStorage + sessionStorage), and asserts:

- authenticated access to a protected path works,
- **unauthenticated** access is gated (401/redirect) from a fresh context,
- a **tampered token** is rejected,
- **logout** clears the session.

For the Playwright *test suite* itself (smoke / generated specs), set `ENABLE_AUTH_SETUP=true` with `ENABLE_DASHBOARD_TESTS=true` and credentials. A setup project (`playwright/auth.setup.ts`) logs in once and writes `playwright/.auth/user.json`; dependent browser projects reuse that state (fixtures also reinject sessionStorage / token extras).

```bash
# API login (token → sessionStorage), then run the checks and save the session
argus api auth-test https://app.example.com --api-login /api/v1/auth/login \
  --username admin --password 'secret' --protected /dashboard --logout-url /api/v1/auth/logout

# or drive the login form in-browser
argus api auth-test https://app.example.com --login-url /login --username admin --password 'secret'
```

### Reuse the session everywhere

A passed auth-test saves the session as `reports/artifacts/auth/<host>.json`. Feed its name back into **flow** or **live-data** so they start already logged in — reliable "test behind login" instead of best-effort form-fill:

```bash
argus flow run https://app.example.com --steps checkout.flow --session app-example-com.json
argus flow realtime https://app.example.com --ws /api/v1/ws/flows --session app-example-com.json
```

In the dashboard, put the session filename in the 🎬 Flow card's "reuse session" field.

---

## 3. Live data — WebSocket & SSE

A dashboard that *loads* isn't the same as one whose live data *updates*. The **📡 Live data** action connects to a stream and asserts it's alive:

```bash
# WebSocket: connect, receive ≥N messages in the window, then survive a forced reconnect
argus flow realtime https://app.example.com --ws /api/v1/ws/flows --expect-messages 3

# JWT via subprotocol (packetwolf): Sec-WebSocket-Protocol: access_token,<jwt>
argus flow realtime https://app.example.com --ws /api/v1/ws/threats --token "$JWT" --subprotocol-jwt

# one-time ticket (veyron): issue a ticket, then connect with ?ticket=
argus flow realtime https://app.example.com --ws /api/v1/vms/default/vm1/vnc --ticket-url /api/v1/ws-ticket

# SSE job/log progress
argus flow realtime https://app.example.com --sse /api/v1/events --expect-messages 1
```

It also does a **browser live-view** check: give a `--live-selector` and it loads the dashboard, counts WebSocket frames via `page.on('websocket')`, and asserts a live region's text actually changed. Crucially it uses **`domcontentloaded` + a per-request latency budget** instead of `networkidle` (always-live dashboards never idle) and classifies the page `ok | crash | api-5xx | slow` — a hung `/api/` call is reported as **slow**, not a false pass.

---

## 4. Web quality

### Core Web Vitals

```bash
argus watch vitals https://app.example.com                 # LCP / CLS / INP / FCP / TTFB, graded
argus watch vitals https://app.example.com --throttle 3g   # under a throttled connection
argus watch vitals https://app.example.com --device "iPhone 14"
```

Each metric is graded good / needs-improvement / poor against Google's thresholds. The **📊 Web Vitals** card has device and throttle dropdowns.

### Device, network & cross-browser (on flow)

The **🎬 Flow** action gained three dropdowns (and CLI flags) so a journey can run under real conditions:

```bash
argus flow run https://app.example.com --steps signup.flow --browser firefox
argus flow run https://app.example.com --steps signup.flow --device "Pixel 7"
argus flow run https://app.example.com --steps signup.flow --throttle offline   # graceful-degradation
```

- **`--browser`** chromium / firefox / webkit — catches Safari/Firefox-specific breakage (Chromium was the only engine before). The deploy script installs all three; if firefox/webkit aren't present it falls back to chromium.
- **`--device`** uses Playwright's real device profiles (touch, UA, viewport).
- **`--throttle`** 3g / offline via CDP — run the same journey and assert the app degrades gracefully.

---

## 8. 🤖 AI test — describe a goal, the agent drives the app itself

The autonomous tester. Type a plain-English goal and the agent drives a real browser to accomplish it — no pre-written steps. It works as a **ReAct loop**: each turn it *observes* the page (the visible interactive elements), a decider *chooses* the next action, and the browser *executes* it — repeating until the goal is met. The whole journey is recorded as video + Playwright trace.

```bash
# needs a saved session for anything behind login (see §2)
argus api ai-test https://app.example.com/vms/new \
  --goal "create a ubuntu vm with 1 vcpu and 2gb ram" \
  --session app-example-com.json --insecure
```

In the dashboard, the **🤖 AI test** card takes a URL, the goal, an optional session, and a max-steps cap. The result is the agent's action transcript (what it clicked/filled and why), the embedded journey video, the trace, and per-step screenshots. If the goal isn't achieved it records a **finding**.

**Two brains:**
- **LLM decider** (primary) — uses the configured model (`LLM_PROVIDER` + key, or a local `ollama` model) via `prompts/ai_flow.md`. Best for bespoke UIs: it reasons about the page, navigates wizards, maps "1 vcpu / 2gb" to the right fields, and knows when it's done.
- **Heuristic decider** (fallback, no LLM) — rule-based: opens a create wizard, fills name/OS/CPU/RAM from the goal keywords, advances `Next`, and submits. Handles standard forms; bespoke UIs need the LLM.

The agent dismisses onboarding overlays, waits for async modals to settle, references elements by a stable index (no brittle selectors), and reuses a saved session (cookies + localStorage + the raw token injected under every common key, so token-in-storage apps authenticate).

## When to use which

| Surface | Action |
|---------|--------|
| REST API correctness | `api-test` (spec or workflow) |
| Login / session / RBAC | `auth-test` (+ reuse the session elsewhere) |
| Live tables, metrics, consoles, job progress | `realtime` |
| Performance, mobile, Safari/Firefox, offline | `vitals` + flow `--browser/--device/--throttle` |
| A page renders / looks right | crawl, audit, route-sweep, flow (Tutorials 10–11) |

## Wiring a product as a test target (example: Forge)

Products can be wired to the agent with a small target script. `scripts/wire-forge.sh` stands up **Forge** locally (its FastAPI API gateway + Vite web UI) and runs the agent's suite against it:

```bash
scripts/wire-forge.sh                 # start Forge + run api-contract, vitals, ai-test
scripts/wire-forge.sh --suite-only    # Forge already running → just run the agent
scripts/wire-forge.sh --no-ui         # gateway only (API contract)
```

It authenticates with a bearer dev key (`FORGE_API_KEY`), starts the gateway with a throwaway kubeconfig so it runs without a full cluster, and points `argus api test` at Forge's 366-endpoint OpenAPI. Note: with no reachable K8s cluster, Forge's cluster-backed endpoints return an **undocumented HTTP 500** — the api-contract flags this ("status 500 not declared"), a real contract-robustness finding (endpoints should declare a 503 for backend-unavailable). Any product with an OpenAPI spec + bearer/token auth can be wired the same way.

## Configuration

| Variable | Effect |
|----------|--------|
| `ZYVOR_BROWSER` | flow engine: chromium / firefox / webkit (set by `--browser`) |
| `ZYVOR_DEVICE` | Playwright device profile (set by `--device`) |
| `ZYVOR_THROTTLE` | 3g / offline network emulation (set by `--throttle`) |
| `ZYVOR_SLOW_MS` | live-data per-request latency budget before a page is flagged `slow` (default 12000) |
| `ZYVOR_IGNORE_HTTPS_ERRORS` | accept self-signed certs (set by `--insecure`) |

A target-site login password is redacted (`***`) from the job-status API and history — see Tutorial 11.
