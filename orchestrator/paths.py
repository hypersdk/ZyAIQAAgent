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

"""Frozen-binary-aware repo-root resolution.

Every module that needs to locate `templates/`, `prompts/`, `tests/`,
`reports/`, etc. relative to the repo root should call `repo_root()` here
instead of hand-rolling `Path(__file__).resolve().parents[N]` locally --
that pattern assumes a real filesystem checkout and silently resolves to
the wrong directory (or one that doesn't exist at all) inside a
PyInstaller-frozen binary, since a frozen build's `__file__` points into a
one-off temp extraction directory, not the source tree.

See ROADMAP.md's "Desktop app v2" section -- this is the code-side half of
what a real single-binary freeze needs; Playwright's browser binaries not
being freezable is the other, unrelated half.
"""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller sets `sys.frozen = True` and, for a onefile build,
        # `sys._MEIPASS` to the temp dir bundled data was extracted into
        # (onedir builds don't set _MEIPASS; the executable's own directory
        # plays the same role there). Either way, that IS "repo root" for a
        # frozen build -- packaging is expected to bundle templates/prompts/
        # etc. at that same top level, mirroring docker/Dockerfile's layout.
        meipass = getattr(sys, "_MEIPASS", None)
        return Path(meipass) if meipass else Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]
