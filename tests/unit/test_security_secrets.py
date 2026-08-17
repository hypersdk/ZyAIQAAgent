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

"""Unit tests for orchestrator.security.secrets: the secret-reference
guard/resolver used for durable schedules, queued jobs, and the
host_pentest/cloud_pentest credential path. Previously untested (67%,
only incidentally exercised via other modules that happen to call
through it)."""

from __future__ import annotations

import pytest

from orchestrator.security.secrets import (
    SecretReferenceError,
    assert_persistable,
    is_secret_ref,
    resolve_secret,
    resolve_secret_refs,
)


# -- is_secret_ref -----------------------------------------------------


def test_is_secret_ref_true_for_well_formed_ref():
    assert is_secret_ref({"$secret": "env:X"}) is True


def test_is_secret_ref_false_for_extra_keys():
    assert is_secret_ref({"$secret": "env:X", "other": 1}) is False


def test_is_secret_ref_false_for_non_string_value():
    assert is_secret_ref({"$secret": 123}) is False


def test_is_secret_ref_false_for_non_mapping():
    assert is_secret_ref("env:X") is False
    assert is_secret_ref(["$secret"]) is False


# -- assert_persistable --------------------------------------------------


def test_assert_persistable_rejects_excessive_nesting():
    with pytest.raises(SecretReferenceError, match="too deeply nested"):
        assert_persistable("x", depth=21)


def test_assert_persistable_rejects_raw_value_under_secret_key():
    with pytest.raises(SecretReferenceError, match="raw secret values cannot be persisted"):
        assert_persistable("raw-password-value", parent_key="password")


def test_assert_persistable_allows_valid_ref_under_secret_key():
    assert_persistable({"$secret": "env:API_KEY"}, parent_key="api_key")


def test_assert_persistable_rejects_malformed_ref_under_secret_key():
    with pytest.raises(SecretReferenceError, match="unsupported secret reference"):
        assert_persistable({"$secret": "vault:whatever"}, parent_key="token")


@pytest.mark.parametrize("empty_value", [None, "", [], {}])
def test_assert_persistable_allows_empty_values_under_secret_key(empty_value):
    assert_persistable(empty_value, parent_key="password")


def test_assert_persistable_rejects_secret_ref_shaped_value_regardless_of_key_name():
    # top-level: value itself looks like a $secret ref even though the key doesn't match
    assert_persistable({"$secret": "env:X"}, parent_key="not_sensitive")


def test_assert_persistable_recurses_into_nested_dict_and_finds_violation():
    payload = {"config": {"nested": {"password": "plaintext-oops"}}}
    with pytest.raises(SecretReferenceError, match="raw secret values cannot be persisted"):
        assert_persistable(payload)


def test_assert_persistable_recurses_into_nested_dict_when_clean():
    payload = {"config": {"nested": {"password": {"$secret": "env:X"}}, "name": "ok"}}
    assert_persistable(payload)


def test_assert_persistable_recurses_into_list_items():
    payload = [{"password": "plaintext-oops"}]
    with pytest.raises(SecretReferenceError, match="raw secret values cannot be persisted"):
        assert_persistable(payload)


def test_assert_persistable_does_not_iterate_strings_as_sequences():
    # a bare string must not be treated as a Sequence-of-characters
    assert_persistable("just a plain string")


def test_assert_persistable_does_not_iterate_bytes_as_sequences():
    assert_persistable(b"just some bytes")


# -- resolve_secret_refs ---------------------------------------------------


def test_resolve_secret_refs_rejects_excessive_nesting():
    with pytest.raises(SecretReferenceError, match="too deeply nested"):
        resolve_secret_refs("x", depth=21)


def test_resolve_secret_refs_resolves_bare_ref(monkeypatch):
    monkeypatch.setenv("MY_TOKEN", "sekrit")
    assert resolve_secret_refs({"$secret": "env:MY_TOKEN"}) == "sekrit"


def test_resolve_secret_refs_recurses_through_dict_list_and_tuple(monkeypatch):
    monkeypatch.setenv("MY_TOKEN", "sekrit")
    payload = {
        "creds": [{"$secret": "env:MY_TOKEN"}, "plain"],
        "pair": ({"$secret": "env:MY_TOKEN"}, 42),
        "unchanged": 7,
    }
    resolved = resolve_secret_refs(payload)
    assert resolved["creds"] == ["sekrit", "plain"]
    assert resolved["pair"] == ("sekrit", 42)
    assert resolved["unchanged"] == 7


def test_resolve_secret_refs_leaves_non_ref_values_unchanged():
    assert resolve_secret_refs(42) == 42
    assert resolve_secret_refs(None) is None


# -- resolve_secret ---------------------------------------------------------


def test_resolve_secret_env_ref_returns_value(monkeypatch):
    monkeypatch.setenv("MY_SECRET", "hunter2")
    assert resolve_secret("env:MY_SECRET") == "hunter2"


def test_resolve_secret_env_ref_missing_raises():
    with pytest.raises(SecretReferenceError, match="is not configured"):
        resolve_secret("env:DEFINITELY_NOT_SET_XYZ")


def test_resolve_secret_file_ref_returns_stripped_content(tmp_path):
    secret_file = tmp_path / "token"
    secret_file.write_text("file-secret-value\r\n", encoding="utf-8")
    assert resolve_secret(f"file:{secret_file}") == "file-secret-value"


def test_resolve_secret_file_ref_missing_raises(tmp_path):
    missing = tmp_path / "nope"
    with pytest.raises(SecretReferenceError, match="unavailable"):
        resolve_secret(f"file:{missing}")


def test_resolve_secret_file_ref_oversized_raises(tmp_path):
    big_file = tmp_path / "big"
    big_file.write_bytes(b"x" * (64 * 1024 + 1))
    with pytest.raises(SecretReferenceError, match="unexpectedly large"):
        resolve_secret(f"file:{big_file}")


def test_resolve_secret_unsupported_ref_raises():
    with pytest.raises(SecretReferenceError, match="unsupported secret reference"):
        resolve_secret("vault:whatever")


def test_resolve_secret_env_prefix_with_empty_name_raises():
    with pytest.raises(SecretReferenceError, match="unsupported secret reference"):
        resolve_secret("env:")
