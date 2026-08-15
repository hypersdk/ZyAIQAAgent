//! Resolve the `zyvor-qa` binary and the app's data directory.
//!
//! v1 deliberately wraps an *existing* local install rather than bundling a
//! frozen Python+Node+Playwright runtime (see the desktop plan's Context
//! section) — this cascade is the whole story for "where does the wrapped
//! tool live," mirroring hypercluster's `resolve_hypercluster_bin()`.

use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

#[cfg(target_os = "windows")]
const PATH_SEP: char = ';';
#[cfg(not(target_os = "windows"))]
const PATH_SEP: char = ':';

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AppSettings {
    /// Explicit override for the `zyvor-qa` binary path. Empty/absent means
    /// "use the resolve_zyvor_qa_bin() cascade."
    #[serde(default)]
    pub zyvor_qa_bin: Option<String>,
}

pub fn app_data_dir() -> PathBuf {
    if cfg!(target_os = "macos") {
        dirs::home_dir()
            .map(|h| h.join("Library/Application Support/ZyvorQA"))
            .unwrap_or_else(|| PathBuf::from(".zyvor-qa-desktop"))
    } else {
        dirs::data_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join("ZyvorQA")
    }
}

pub fn settings_path() -> PathBuf {
    app_data_dir().join("settings.json")
}

pub fn load_settings() -> AppSettings {
    fs::read_to_string(settings_path())
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

pub fn save_settings(settings: &AppSettings) -> Result<(), String> {
    let dir = app_data_dir();
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let json = serde_json::to_string_pretty(settings).map_err(|e| e.to_string())?;
    fs::write(settings_path(), json).map_err(|e| e.to_string())
}

/// The ZyAIQAAgent repo root, resolved from *this crate's own source
/// location* at compile time (`CARGO_MANIFEST_DIR`) rather than the
/// process's runtime working directory or executable path — both of those
/// vary depending on how `cargo`/`tauri dev` was invoked, while
/// `CARGO_MANIFEST_DIR` is a fixed, reliable absolute path baked in at
/// build time for whoever compiled this checkout. Returns `None` if this
/// binary wasn't built from within a real ZyAIQAAgent checkout (`.venv`
/// missing) — e.g. a release build copied elsewhere.
pub fn dev_checkout_root() -> Option<PathBuf> {
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")); // .../ZyAIQAAgent/desktop/src-tauri
    let repo_root = manifest_dir.parent()?.parent()?.to_path_buf(); // .../ZyAIQAAgent
    repo_root.join(".venv").is_dir().then_some(repo_root)
}

fn dev_checkout_bin() -> Option<PathBuf> {
    let repo_root = dev_checkout_root()?;
    let venv_name = if cfg!(target_os = "windows") {
        "Scripts/zyvor-qa.exe"
    } else {
        "bin/zyvor-qa"
    };
    let candidate = repo_root.join(".venv").join(venv_name);
    candidate.is_file().then_some(candidate)
}

fn path_lookup_bin() -> Option<PathBuf> {
    let name = if cfg!(target_os = "windows") {
        "zyvor-qa.exe"
    } else {
        "zyvor-qa"
    };
    for seg in env::var("PATH").unwrap_or_default().split(PATH_SEP) {
        if seg.is_empty() {
            continue;
        }
        let candidate = Path::new(seg).join(name);
        if candidate.is_file() {
            return Some(candidate);
        }
    }
    None
}

/// Working directory to launch `zyvor-qa serve` from. `MissionControlStore`
/// (`orchestrator/persistence/store.py`) defaults `ZYVOR_STATE_DB` to the
/// *relative* path `reports/mission-control.db` — unlike the rest of
/// ZyAIQAAgent's path handling (`_repo_root()`-based, CWD-independent),
/// that one default resolves relative to the process's working directory.
/// Left unset, the spawned child inherits whatever CWD `cargo`/the app
/// bundle happened to launch with (confirmed while testing this: it landed
/// state in `desktop/src-tauri/reports/` instead of the repo root). Pin it
/// explicitly: the real repo root in dev (matching a normal `zyvor-qa
/// serve` invocation exactly, so state lands in the same place), or the
/// app's own data dir otherwise (stable and app-owned, rather than
/// whatever ambient CWD Finder/launchd happened to provide).
pub fn working_dir() -> PathBuf {
    dev_checkout_root().unwrap_or_else(app_data_dir)
}

/// Resolution order: explicit settings override -> dev checkout's `.venv`
/// -> `zyvor-qa` on PATH -> bare `"zyvor-qa"` (last resort; spawning it will
/// fail with a clear "not found" error the UI can surface).
pub fn resolve_zyvor_qa_bin(settings_override: Option<&str>) -> PathBuf {
    if let Some(b) = settings_override {
        if !b.is_empty() && Path::new(b).is_file() {
            return PathBuf::from(b);
        }
    }
    if let Some(b) = dev_checkout_bin() {
        return b;
    }
    if let Some(b) = path_lookup_bin() {
        return b;
    }
    PathBuf::from(if cfg!(target_os = "windows") {
        "zyvor-qa.exe"
    } else {
        "zyvor-qa"
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dev_checkout_bin_finds_the_real_venv_when_present() {
        // This test runs from within the actual ZyAIQAAgent checkout, so if
        // `.venv` was set up (`make install`), the cascade's second tier
        // should find it without needing PATH or a settings override.
        if let Some(bin) = dev_checkout_bin() {
            assert!(bin.ends_with("zyvor-qa") || bin.ends_with("zyvor-qa.exe"));
        }
    }

    #[test]
    fn resolve_prefers_explicit_override_when_it_exists() {
        let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let this_file = manifest_dir.join("Cargo.toml");
        let resolved = resolve_zyvor_qa_bin(Some(this_file.to_str().unwrap()));
        assert_eq!(resolved, this_file);
    }

    #[test]
    fn resolve_ignores_a_nonexistent_override() {
        let resolved = resolve_zyvor_qa_bin(Some("/definitely/not/a/real/path/zyvor-qa"));
        // Falls through to the next tier rather than returning the bogus path.
        assert_ne!(resolved, PathBuf::from("/definitely/not/a/real/path/zyvor-qa"));
    }
}
