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

"""Unit tests for the `github` and `local` branches of fetch_requirements
(the `document` branch is covered separately in test_fetch_document_source.py)."""

from __future__ import annotations

import orchestrator.nodes.fetch as fetch_module
from orchestrator.nodes.fetch import fetch_requirements


class _FakeGitHubClient:
    available = True
    download_files_result = None
    download_spec_result = None
    download_files_error = None
    download_spec_error = None
    pr_body = "some PR body"
    pr_body_error = None
    changed_files = ["a.py"]
    changed_files_error = None
    discovery_result = (["local/a.py"], ["a.py"])
    discovery_error = None

    def __init__(self):
        pass

    def download_files_to_local(self, repo, requested, output_dir):
        if self.download_files_error:
            raise self.download_files_error
        output_dir.mkdir(parents=True, exist_ok=True)  # real client ensures this exists too
        return self.download_files_result or ["/tmp/fetched-a.md"]

    def download_spec_to_local(self, repo, output_dir):
        if self.download_spec_error:
            raise self.download_spec_error
        output_dir.mkdir(parents=True, exist_ok=True)
        return self.download_spec_result or ["/tmp/fetched-b.md"]

    def fetch_pr_body(self, repo, pr_number):
        if self.pr_body_error:
            raise self.pr_body_error
        return self.pr_body

    def fetch_pr_changed_files(self, repo, pr_number):
        if self.changed_files_error:
            raise self.changed_files_error
        return self.changed_files

    def download_discovery_files_to_local(self, repo, code_dir, *, scope_paths=None):
        if self.discovery_error:
            raise self.discovery_error
        return self.discovery_result


def _patch_client(monkeypatch, client):
    monkeypatch.setattr("github_integration.client.GitHubClient", lambda: client)


# --- github: repo/token guards ------------------------------------------------
def test_github_requires_repo(monkeypatch):
    monkeypatch.delenv("ZYVOR_PRODUCT_REPO", raising=False)
    result = fetch_requirements({"source": "github"})
    assert "ZYVOR_PRODUCT_REPO is not set" in result["error"]


def test_github_requires_token(monkeypatch):
    client = _FakeGitHubClient()
    client.available = False
    _patch_client(monkeypatch, client)
    result = fetch_requirements({"source": "github", "repo_full_name": "org/repo"})
    assert "GitHub token required" in result["error"]


# --- github: happy paths -------------------------------------------------------
def test_github_downloads_requested_spec_paths(monkeypatch, tmp_path):
    client = _FakeGitHubClient()
    client.download_files_result = ["/tmp/fetched-requested.md"]
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "spec_paths": ["docs/spec.md"]}
    )
    assert result["spec_paths"] == ["/tmp/fetched-requested.md"]


def test_github_downloads_default_spec_when_no_paths_requested(monkeypatch):
    client = _FakeGitHubClient()
    _patch_client(monkeypatch, client)
    result = fetch_requirements({"source": "github", "repo_full_name": "org/repo"})
    assert result["spec_paths"] == ["/tmp/fetched-b.md"]


def test_github_download_failure_sets_error(monkeypatch):
    client = _FakeGitHubClient()
    client.download_spec_error = RuntimeError("network down")
    _patch_client(monkeypatch, client)
    result = fetch_requirements({"source": "github", "repo_full_name": "org/repo"})
    assert "Failed to fetch spec from GitHub" in result["error"]


# --- github: PR body / changed files -------------------------------------------
def test_github_pr_body_written_and_appended(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "pr_number": 42}
    )
    assert result["metadata"]["pr_body_fetched"] is True
    assert any("pr-42-body.md" in p for p in result["spec_paths"])
    written = (tmp_path / "tests" / "fixtures" / "fetched" / "pr-42-body.md").read_text()
    assert "some PR body" in written


def test_github_pr_body_fetch_failure_is_swallowed(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()
    client.pr_body_error = RuntimeError("no access")
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "pr_number": 42}
    )
    assert result.get("error") is None
    assert "pr_body_fetched" not in result["metadata"]


def test_github_changed_files_fetched_when_not_already_in_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "pr_number": 42}
    )
    assert result["metadata"]["changed_files"] == ["a.py"]


def test_github_changed_files_fetch_failure_defaults_to_empty_list(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()
    client.changed_files_error = RuntimeError("rate limited")
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "pr_number": 42}
    )
    assert result["metadata"]["changed_files"] == []


def test_github_changed_files_not_refetched_if_already_present(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()

    def should_not_be_called(*a, **k):
        raise AssertionError("fetch_pr_changed_files should not be called")

    client.fetch_pr_changed_files = should_not_be_called
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {
            "source": "github", "repo_full_name": "org/repo", "pr_number": 42,
            "metadata": {"changed_files": ["already-here.py"]},
        }
    )
    assert result["metadata"]["changed_files"] == ["already-here.py"]


# --- github: coverage-expansion discovery --------------------------------------
def test_github_discovery_runs_when_coverage_expansion_enabled(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "expand_coverage": True}
    )
    assert result["metadata"]["discovered_paths"] == ["a.py"]
    assert result["metadata"]["discovered_local_paths"] == ["local/a.py"]


def test_github_discovery_failure_recorded_in_metadata(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    client = _FakeGitHubClient()
    client.discovery_error = RuntimeError("crawl failed")
    _patch_client(monkeypatch, client)
    result = fetch_requirements(
        {"source": "github", "repo_full_name": "org/repo", "expand_coverage": True}
    )
    assert "crawl failed" in result["metadata"]["discovery_error"]


# --- local ----------------------------------------------------------------------
def test_local_reads_existing_spec_paths(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text("# real spec")
    result = fetch_requirements({"source": "local", "spec_paths": [str(spec)]})
    assert result["spec_contents"] == ["# real spec"]


def test_local_skips_nonexistent_spec_paths(tmp_path):
    result = fetch_requirements({"source": "local", "spec_paths": [str(tmp_path / "missing.md")]})
    assert result["spec_contents"] == []


def test_local_falls_back_to_default_spec_when_none_given():
    result = fetch_requirements({"source": "local"})
    # prompts/examples/vm-create.md is a real, checked-in file
    assert len(result["spec_paths"]) == 1
    assert "vm-create.md" in result["spec_paths"][0]
    assert result["spec_contents"]


def test_local_no_default_spec_available_leaves_everything_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_module, "_repo_root", lambda: tmp_path)
    result = fetch_requirements({"source": "local"})
    assert result["spec_paths"] == []
    assert result["spec_contents"] == []
