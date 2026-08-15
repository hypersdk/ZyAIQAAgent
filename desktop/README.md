# Zyvor QA Agent Desktop

A native macOS window around `zyvor-qa serve`'s Mission Control dashboard —
no browser tab needed. This is a thin shell, not a reimplementation: every
dashboard action (trigger a run, view reports, manage schedules) runs
through the exact same FastAPI server and job queue as `zyvor-qa serve`
does normally. See [the desktop plan](../ROADMAP.md) for the v1/v2 scope
boundary (v1 wraps an existing local install; it does not bundle a frozen
Python+Node+Playwright runtime).

## Requirements

- Node.js 20+
- Rust (for Tauri 2) — `rustup` or Homebrew
- macOS: Xcode Command Line Tools
- A working `zyvor-qa` install: the repo root's `.venv` (`make install` from
  the repo root) is auto-detected in dev; a `pip`-installed `zyvor-qa` on
  `PATH` also works
- Node/Playwright (`npm install && npx playwright install --with-deps
  chromium` from the repo root) — only needed to actually *run* jobs from
  the dashboard, not to view it

## Run (npm CLI — like `hypercluster-desktop`)

From the **repo root**:

```bash
npm install
npm run desktop
# or
npx zyvor-qa-desktop
```

Install globally:

```bash
npm install -g ./desktop
zyvor-qa-desktop
```

### Commands

| Command | Description |
|---------|--------------|
| `zyvor-qa-desktop` | Start Tauri dev (default) |
| `zyvor-qa-desktop dev` | Same as above |
| `zyvor-qa-desktop build` | Build the native `.app`/`.dmg` bundle |
| `zyvor-qa-desktop run` | Launch the built `.app` |
| `zyvor-qa-desktop help` | Show usage |

Legacy (still works):

```bash
cd desktop && npm install && npm run tauri dev
```

## How it works

1. On launch, the Rust shell (`src-tauri/src/server.rs`) resolves the
   `zyvor-qa` binary (`src-tauri/src/paths.rs`: explicit settings override →
   the repo's own `.venv` → `PATH`) and spawns
   `zyvor-qa serve --host 127.0.0.1 --port <free-port>` — **bound to
   localhost only**, not `serve`'s own CLI default of `0.0.0.0`, so opening
   the app never makes the dashboard reachable from the LAN.
2. `public/index.html` — the entire "frontend," no build step, no
   React/Vite — polls a `dashboard_url` Tauri command until the server is
   ready, then navigates the window straight to
   `http://127.0.0.1:<port>/dashboard`.
3. Closing the window kills the spawned `zyvor-qa serve` process (no
   orphaned server left running after the app quits).

## Settings

`~/Library/Application Support/ZyvorQA/settings.json` — currently just
`zyvor_qa_bin`, an explicit override for the resolved binary path if
auto-detection picks the wrong one (e.g. multiple Python environments).

## Icons

`src-tauri/icons/icon-source.png` is a **placeholder** (no real Zyvor
branding assets exist in this repo yet). Replace it with real artwork and
regenerate the platform set:

```bash
cd desktop && npx tauri icon src-tauri/icons/icon-source.png -o src-tauri/icons
```

## Building

```bash
zyvor-qa-desktop build
# or
make desktop-build   # from the repo root
```

Produces an **unsigned** `.app`/`.dmg` under
`desktop/src-tauri/target/release/bundle/macos/` — fine for local testing.
Code signing/notarization needs an Apple Developer account and isn't wired
up yet (see `ROADMAP.md`).

## Tech stack

- Tauri 2 (Rust) — process spawn/lifecycle only, no custom IPC surface
  beyond `dashboard_url`/`get_settings`/`set_settings`
- A single static HTML file as the frontend — the dashboard itself
  (`templates/dashboard.html.j2`) is server-rendered by the Python backend,
  so there's nothing here to build with React/Vite/Tailwind
