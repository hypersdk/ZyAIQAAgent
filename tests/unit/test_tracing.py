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

"""Unit tests for the optional OpenTelemetry tracing wrapper."""

from __future__ import annotations

import pytest

import orchestrator.observability.tracing as tracing_module
from orchestrator.observability.tracing import set_span_error, start_span, tracing_enabled


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ZYVOR_OTEL_ENABLED", raising=False)
    assert tracing_enabled() is False


def test_enabled_via_explicit_flag(monkeypatch):
    monkeypatch.setenv("ZYVOR_OTEL_ENABLED", "true")
    assert tracing_enabled() is True


def test_start_span_is_a_safe_noop_when_disabled(monkeypatch):
    monkeypatch.setenv("ZYVOR_OTEL_ENABLED", "false")
    monkeypatch.setattr(tracing_module, "_tracer", None)

    with start_span("noop.test", foo="bar") as span:
        assert span is None
    # set_span_error on a None span must not raise
    set_span_error(None, "irrelevant")


def test_start_span_emits_a_real_span_when_enabled(monkeypatch):
    pytest.importorskip("opentelemetry")
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    monkeypatch.setenv("ZYVOR_OTEL_ENABLED", "true")
    monkeypatch.setattr(tracing_module, "_tracer", trace.get_tracer("test", tracer_provider=provider))

    with start_span("job.execute", job_id="abc", job_kind="ping") as span:
        assert span is not None
        span.set_attribute("job.status", "succeeded")

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "job.execute"
    assert spans[0].attributes["job_id"] == "abc"
    assert spans[0].attributes["job.status"] == "succeeded"


def test_set_span_error_marks_status_and_attribute(monkeypatch):
    pytest.importorskip("opentelemetry")
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.trace import StatusCode

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    monkeypatch.setenv("ZYVOR_OTEL_ENABLED", "true")
    monkeypatch.setattr(tracing_module, "_tracer", trace.get_tracer("test", tracer_provider=provider))

    with start_span("pipeline.fetch") as span:
        set_span_error(span, "boom")

    finished = exporter.get_finished_spans()[0]
    assert finished.status.status_code == StatusCode.ERROR
    assert finished.attributes["error"] is True
