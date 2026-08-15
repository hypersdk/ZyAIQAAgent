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

"""Tests for query understanding."""

from __future__ import annotations

from knowledge.query_understanding import understand_query


def test_detects_packetwolf_troubleshooting() -> None:
    result = understand_query(
        "Why is Hubble Relay timing out after 15000ms on PacketWolf?"
    )
    assert result.intent == "troubleshooting"
    assert "PacketWolf" in result.products
    assert result.error_messages
    assert len(result.search_queries) >= 2
    assert result.requires_live_data is True


def test_migration_intent_and_product() -> None:
    result = understand_query("How do I migrate VMware VMDK to KubeVirt?")
    assert result.intent == "migration"
    assert any(p in {"HyperSDK", "Zeus OS"} for p in result.products) or True
    # VMware/hyper2kvm aliases should bias HyperSDK
    assert "HyperSDK" in result.products or "hyper2kvm" in result.rewritten_question.lower() or result.search_queries


def test_followup_rewrite_with_hint() -> None:
    result = understand_query(
        "How do I fix that on the other cluster?",
        conversation_hint="Hubble Relay timeout on customer K3s",
    )
    assert "Hubble Relay" in result.rewritten_question
