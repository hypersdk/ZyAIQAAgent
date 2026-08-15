//! Spawn `zyvor-qa serve` as a child process and track its readiness.
//!
//! Unlike hypercluster's `hypercluster.rs` (which spawns a fresh subprocess
//! per action and streams its output into custom UI panels), there's only
//! ever one long-lived child here: `zyvor-qa serve` runs once for the
//! app's lifetime, and the dashboard it serves handles every subsequent
//! action itself over HTTP — the Rust side's job is just "start it, know
//! when it's ready, kill it on quit."

use crate::paths;
use std::io::{BufRead, BufReader};
use std::net::{TcpListener, TcpStream};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;
use std::time::Duration;

const READY_TIMEOUT: Duration = Duration::from_secs(20);
const POLL_INTERVAL: Duration = Duration::from_millis(150);

pub enum ServerStatus {
    Ready(u16),
    Failed(String),
}

struct ServerHandle {
    child: Child,
}

impl Drop for ServerHandle {
    fn drop(&mut self) {
        // Best-effort: the app is quitting either way. A `zyvor-qa serve`
        // left running after the window closes would silently keep a port
        // bound and a stale dashboard reachable, so this is not optional.
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

#[derive(Default)]
pub struct ServerState {
    status: Mutex<Option<ServerStatus>>,
    handle: Mutex<Option<ServerHandle>>,
}

impl ServerState {
    fn set_status(&self, status: ServerStatus) {
        if let Ok(mut guard) = self.status.lock() {
            *guard = Some(status);
        }
    }
}

fn free_port() -> Result<u16, String> {
    let listener = TcpListener::bind(("127.0.0.1", 0)).map_err(|e| e.to_string())?;
    let port = listener
        .local_addr()
        .map_err(|e| e.to_string())?
        .port();
    drop(listener); // release it immediately so `zyvor-qa serve` can bind it
    Ok(port)
}

fn wait_for_port(port: u16, timeout: Duration) -> bool {
    let start = std::time::Instant::now();
    while start.elapsed() < timeout {
        if TcpStream::connect(("127.0.0.1", port)).is_ok() {
            return true;
        }
        thread::sleep(POLL_INTERVAL);
    }
    false
}

fn spawn_serve(bin_override: Option<&str>) -> Result<(Child, u16), String> {
    let bin = paths::resolve_zyvor_qa_bin(bin_override);
    let port = free_port()?;
    let working_dir = paths::working_dir();
    std::fs::create_dir_all(&working_dir).ok();

    // 127.0.0.1, not `serve`'s own CLI default of 0.0.0.0 — a desktop app
    // being opened shouldn't silently make the dashboard reachable from the
    // LAN. This is a spawn-argument choice here, not a change to `serve`'s
    // own default (other callers, e.g. Docker/K8s, still want 0.0.0.0).
    let mut cmd = Command::new(&bin);
    cmd.args(["serve", "--host", "127.0.0.1", "--port", &port.to_string()])
        // See paths::working_dir()'s doc comment — without this, relative
        // state paths (MissionControlStore's ZYVOR_STATE_DB default among
        // them) resolve against whatever CWD the app happened to launch
        // with, not the repo the wrapped `zyvor-qa` actually belongs to.
        .current_dir(&working_dir)
        // Tells the dashboard template it's running inside this desktop
        // shell, not a normal browser tab — it hides the Kubernetes
        // pods/workloads panel, which is always "cluster unavailable" here
        // (see orchestrator/dashboard/routes.py, templates/dashboard.html.j2).
        .env("ZYVOR_DESKTOP_MODE", "true")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let mut child = cmd.spawn().map_err(|e| {
        format!(
            "failed to launch {} ({e}) — is zyvor-qa installed? \
             Set a custom path in Settings if it's not on PATH.",
            bin.display()
        )
    })?;

    // Drain stdout/stderr on background threads so a full pipe buffer never
    // blocks the child; forwarded to this process's own stdout/stderr,
    // visible in `tauri dev`'s terminal.
    if let Some(stdout) = child.stdout.take() {
        thread::spawn(move || {
            for line in BufReader::new(stdout).lines().map_while(Result::ok) {
                println!("[zyvor-qa serve] {line}");
            }
        });
    }
    if let Some(stderr) = child.stderr.take() {
        thread::spawn(move || {
            for line in BufReader::new(stderr).lines().map_while(Result::ok) {
                eprintln!("[zyvor-qa serve] {line}");
            }
        });
    }

    Ok((child, port))
}

/// Start the server on a background thread; `status()` reports progress.
/// Called once from the app's `setup()` hook.
///
/// Takes an owned `AppHandle` (Send + Clone + 'static) rather than a
/// borrowed `State<ServerState>` — a `State` reference can't cross a
/// `thread::spawn` boundary, so the handle is captured instead and
/// `.state::<ServerState>()` is re-derived fresh once inside the thread.
pub fn start_in_background(app_handle: tauri::AppHandle, bin_override: Option<String>) {
    thread::spawn(move || {
        use tauri::Manager;
        let state = app_handle.state::<ServerState>();
        match spawn_serve(bin_override.as_deref()) {
            Ok((child, port)) => {
                if wait_for_port(port, READY_TIMEOUT) {
                    if let Ok(mut guard) = state.handle.lock() {
                        *guard = Some(ServerHandle { child });
                    }
                    state.set_status(ServerStatus::Ready(port));
                } else {
                    state.set_status(ServerStatus::Failed(format!(
                        "zyvor-qa serve did not become ready on port {port} within {}s",
                        READY_TIMEOUT.as_secs()
                    )));
                }
            }
            Err(e) => state.set_status(ServerStatus::Failed(e)),
        }
    });
}

/// Non-blocking status check for the frontend's poll loop:
/// `Ok(None)` = still starting, `Ok(Some(url))` = ready, `Err` = failed.
pub fn dashboard_url(state: &ServerState) -> Result<Option<String>, String> {
    match state.status.lock().map_err(|_| "server state poisoned")?.as_ref() {
        None => Ok(None),
        Some(ServerStatus::Ready(port)) => Ok(Some(format!("http://127.0.0.1:{port}/dashboard"))),
        Some(ServerStatus::Failed(e)) => Err(e.clone()),
    }
}

/// Kill the child, if running — called on window close.
pub fn shutdown(state: &ServerState) {
    if let Ok(mut guard) = state.handle.lock() {
        *guard = None; // drops ServerHandle -> kills the child
    }
}
