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

from orchestrator.security.redaction import REDACTED, redact, redact_text


def test_recursive_secret_redaction():
    raw = {
        "auth": {
            "token": "abc",
            "headers": {"Authorization": "Bearer top-secret"},
        },
        "items": [{"client_secret": "x"}, {"safe": "ok"}],
    }
    clean = redact(raw)
    assert clean["auth"]["token"] == REDACTED
    assert clean["auth"]["headers"]["Authorization"] == REDACTED
    assert clean["items"][0]["client_secret"] == REDACTED
    assert clean["items"][1]["safe"] == "ok"


def test_text_token_redaction():
    text = redact_text("Authorization: Bearer abcdefghijklmnop token=hello-world")
    assert "abcdefghijklmnop" not in text
    assert "hello-world" not in text


def test_redact_stops_at_max_depth():
    nested: dict = {"leaf": "value"}
    for _ in range(5):
        nested = {"child": nested}
    assert redact(nested, max_depth=2) == {"child": {"child": {"child": "<max-depth>"}}}


def test_redact_handles_tuples():
    clean = redact(({"token": "abc"}, "safe"))
    assert clean == ({"token": REDACTED}, "safe")


def test_redact_handles_sets():
    clean = redact({"safe-one", "safe-two"})
    assert clean == {"safe-one", "safe-two"}


def test_redact_leaves_unknown_types_unchanged():
    assert redact(42) == 42
    assert redact(None) is None
    assert redact(3.14) == 3.14
