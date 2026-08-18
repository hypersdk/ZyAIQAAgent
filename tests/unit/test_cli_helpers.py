# Copyright 2026 ZyvorAI Labs Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for the pure/reusable helpers in orchestrator/cli.py.

The ~25 @app.command() functions themselves are thin Typer wrappers that
immediately delegate to real pipeline/subprocess execution (run_playwright,
graph.invoke, etc.) with no isolable validation logic of their own — Typer
handles their argument parsing/validation, so there's little unit-testable
surface there beyond what these helpers already cover.
"""

from __future__ import annotations

from pathlib import Path

from orchestrator import cli


# ── _initial_state ───────────────────────────────────────────────────


def test_initial_state_defaults():
    state = cli._initial_state()
    assert state["source"] == "local"
    assert state["spec_paths"] == []
    assert state["metadata"] == {"explicit_spec": False}
    assert state["expand_coverage"] is False
    assert state["pr_number"] is None


def test_initial_state_local_spec_resolved_to_absolute_path(tmp_path, monkeypatch):
    spec = tmp_path / "spec.md"
    spec.write_text("# spec")
    monkeypatch.chdir(tmp_path)
    state = cli._initial_state(source="local", spec="spec.md")
    assert state["spec_paths"] == [str(spec.resolve())]
    assert state["metadata"] == {"explicit_spec": True}


def test_initial_state_github_spec_normalized():
    state = cli._initial_state(source="github", spec="docs/spec.md")
    assert state["spec_paths"] == ["docs/spec.md"]


def test_initial_state_document_spec_resolved_to_absolute_path(tmp_path, monkeypatch):
    doc = tmp_path / "spec.pdf"
    doc.write_bytes(b"%PDF-1.4")
    monkeypatch.chdir(tmp_path)
    state = cli._initial_state(source="document", spec="spec.pdf")
    assert state["document_paths"] == [str(doc.resolve())]
    assert state["spec_paths"] == []  # document paths are separate from spec_paths


def test_initial_state_pr_number_passed_through():
    state = cli._initial_state(pr_number=42)
    assert state["pr_number"] == 42


def test_initial_state_expand_coverage_flag_or_env(monkeypatch):
    monkeypatch.delenv("ENABLE_COVERAGE_EXPANSION", raising=False)
    assert cli._initial_state(expand_coverage=True)["expand_coverage"] is True
    assert cli._initial_state(expand_coverage=False)["expand_coverage"] is False
    monkeypatch.setenv("ENABLE_COVERAGE_EXPANSION", "true")
    assert cli._initial_state(expand_coverage=False)["expand_coverage"] is True


def test_initial_state_repo_full_name_from_env(monkeypatch):
    monkeypatch.setenv("ZYVOR_PRODUCT_REPO", "owner/repo")
    assert cli._initial_state()["repo_full_name"] == "owner/repo"


# ── _load_env ─────────────────────────────────────────────────────────


def test_load_env_points_load_dotenv_at_the_repo_root_env_file(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "load_dotenv", lambda path: calls.append(path))

    cli._load_env()

    assert len(calls) == 1
    assert calls[0].name == ".env"
    # repo root = two parents up from orchestrator/cli.py
    assert calls[0].parent == Path(cli.__file__).resolve().parents[1]


def test_load_env_missing_file_does_not_raise():
    # No .env in the repo root shouldn't raise — load_dotenv() is silently
    # a no-op when the file doesn't exist. Uses the real repo (may or may
    # not have a .env, but either way this must not throw).
    cli._load_env()


# ── _ensure_tls_cert ──────────────────────────────────────────────────


def test_ensure_tls_cert_returns_explicit_paths_unchanged():
    cert, key = cli._ensure_tls_cert("/tmp/my.crt", "/tmp/my.key", "example.com")
    assert (cert, key) == ("/tmp/my.crt", "/tmp/my.key")


def test_ensure_tls_cert_reuses_existing_cert(tmp_path, monkeypatch):
    monkeypatch.setattr(cli.Path, "home", classmethod(lambda cls: tmp_path))
    cert_dir = tmp_path / ".zyvor-argus" / "tls"
    cert_dir.mkdir(parents=True)
    (cert_dir / "server.crt").write_text("fake-cert")
    (cert_dir / "server.key").write_text("fake-key")

    cert, key = cli._ensure_tls_cert(None, None, "localhost")

    assert cert == str(cert_dir / "server.crt")
    assert key == str(cert_dir / "server.key")


def test_ensure_tls_cert_generates_with_openssl_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(cli.Path, "home", classmethod(lambda cls: tmp_path))
    calls = []

    def fake_run(cmd, check, capture_output):
        calls.append(cmd)
        cert_path = Path(cmd[cmd.index("-out") + 1])
        key_path = Path(cmd[cmd.index("-keyout") + 1])
        cert_path.write_text("generated-cert")
        key_path.write_text("generated-key")

    # _ensure_tls_cert does `import subprocess` locally, so patch the real
    # module (sys.modules-cached) rather than a nonexistent cli.subprocess.
    import subprocess as real_subprocess

    monkeypatch.setattr(real_subprocess, "run", fake_run)

    cert, key = cli._ensure_tls_cert(None, None, "0.0.0.0")

    assert calls, "openssl should have been invoked"
    assert "/CN=localhost" in calls[0]  # 0.0.0.0 isn't a valid cert CN
    assert Path(cert).read_text() == "generated-cert"
    assert Path(key).read_text() == "generated-key"
