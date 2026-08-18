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

"""Unit tests for orchestrator.paths.repo_root()."""

from __future__ import annotations

import sys

from orchestrator.paths import repo_root


def test_unfrozen_resolves_to_the_real_repo_root():
    root = repo_root()
    # A handful of directories that only exist at the real repo root --
    # confirms this isn't just "some parent directory."
    assert (root / "orchestrator").is_dir()
    assert (root / "agents").is_dir()
    assert (root / "pyproject.toml").is_file()


def test_frozen_onefile_uses_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert repo_root() == tmp_path


def test_frozen_onedir_without_meipass_uses_executable_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    fake_exe = tmp_path / "argus-enterprise-desktop"
    monkeypatch.setattr(sys, "executable", str(fake_exe))
    assert repo_root() == tmp_path
