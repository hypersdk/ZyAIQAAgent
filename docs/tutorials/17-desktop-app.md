# Tutorial 17 — Desktop app (macOS)

A native window around Mission Control — `zyvor-qa serve`'s dashboard, without a browser tab.

**Prerequisites:** [Tutorial 1](01-getting-started.md), [Tutorial 10](10-mission-control-dashboard.md).

---

## 1. What this is (and isn't)

`desktop/` is a thin [Tauri 2](https://tauri.app) shell: it spawns
`zyvor-qa serve` as a child process and points a native window at
`http://127.0.0.1:<port>/dashboard`. It is **not** a reimplementation —
every dashboard action (triggering a run, viewing reports, managing
schedules) goes through the exact same FastAPI server, job queue, CSRF
protection, and rate limiting as `zyvor-qa serve` does normally. Closing
the window kills the spawned server; nothing is left running in the
background.

It also does **not** bundle a self-contained Python+Node+Playwright
runtime — it wraps your existing local install (the repo's own `.venv`, or
a `pip`-installed `zyvor-qa` on `PATH`). See `ROADMAP.md`'s "Desktop app
v2" entry for why that's a deliberate v1 boundary, not an oversight.

## 2. Requirements

- Node.js 20+, Rust (`rustup` or Homebrew), Xcode Command Line Tools
- A working `zyvor-qa` install — `make install` from the repo root gives
  you `.venv/bin/zyvor-qa`, auto-detected in dev
- Node/Playwright (also from `make install`) — only needed to actually
  *run* jobs from the dashboard, not to view it

## 3. Run it

```bash
npm install          # from the repo root — sets up the desktop/ workspace too
npm run desktop
# or
make desktop-dev
```

A window opens with a brief loading screen, then hands off to the real
dashboard once `zyvor-qa serve` is ready (usually under a second).

## 4. Build a standalone app

```bash
make desktop-build
```

Produces an **unsigned** `Zyvor QA Agent.app`/`.dmg` under
`desktop/src-tauri/target/release/bundle/macos/` — open it directly, no
`npm run desktop` needed. Unsigned means macOS Gatekeeper will warn on
first launch (right-click → Open); code signing/notarization isn't wired
up yet.

## 5. Pointing it at a different `zyvor-qa`

If you have multiple Python environments, or the auto-detected binary
isn't the one you want, override it in
`~/Library/Application Support/ZyvorQA/settings.json`:

```json
{ "zyvor_qa_bin": "/path/to/your/venv/bin/zyvor-qa" }
```

## 6. Security notes

- The spawned server binds to `127.0.0.1` only — opening the app never
  exposes the dashboard to your LAN, even though `zyvor-qa serve`'s own
  CLI default is `0.0.0.0`.
- A random free port is chosen per launch (not a fixed 8080), so a second
  instance or a port conflict doesn't just fail.
- `DASHBOARD_PASSWORD` is unset by default (matches `zyvor-qa serve`'s own
  default) — the desktop app assumes a single local user. Set it in your
  `.env` if you want the login/CSRF/rate-limiting path exercised even
  locally.

**See also:** [`desktop/README.md`](../../desktop/README.md) for the
Rust-side implementation notes, and [Tutorial 10](10-mission-control-dashboard.md)
for everything the dashboard itself can do.
