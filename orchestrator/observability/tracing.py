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

"""Optional OpenTelemetry distributed tracing.

Opt-in via ZYVOR_OTEL_ENABLED=true -- matching this codebase's existing
explicit-flag convention (ENABLE_AUTOFIX, ZYVOR_EXPLOIT_EXECUTION_ENABLED,
...) rather than auto-enabling just because the `otel` extra happens to be
installed. Without the extra installed, or with tracing disabled, start_span()
is a safe no-op context manager (yields None) -- callers never need to branch
on whether tracing is actually configured, the same "dependency-free by
default" posture as observability/metrics.py.

Exporter: OTLP/HTTP to OTEL_EXPORTER_OTLP_ENDPOINT if set, otherwise spans
print to stdout via OpenTelemetry's own ConsoleSpanExporter -- genuine SDK
behavior, not a stub, useful for local debugging without a collector.

Scope note (see ROADMAP.md): this instruments spans *within* a single
process (one span per claimed job in the worker loop, one span per LangGraph
pipeline node) but does not yet propagate trace context across the
enqueue -> claim boundary when those happen on different replicas (would
need a persisted `traceparent` column on the `jobs` table plus the same
change mirrored into PostgresStore) -- named as real follow-on work, not
silently skipped.
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Any, Iterator

_tracer: Any = None
_tracer_lock = threading.Lock()


def tracing_enabled() -> bool:
    return os.environ.get("ZYVOR_OTEL_ENABLED", "false").lower() == "true"


def _get_tracer() -> Any:
    """Returns an OTel tracer, or False (sentinel for "not available/enabled").
    Cached after first call -- mirrors observability/metrics.py's module-level
    state, and matches the once-per-process SDK/provider setup OTel expects."""
    global _tracer
    if _tracer is not None:
        return _tracer
    with _tracer_lock:
        if _tracer is not None:
            return _tracer
        if not tracing_enabled():
            _tracer = False
            return _tracer
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import (
                BatchSpanProcessor,
                ConsoleSpanExporter,
                SimpleSpanProcessor,
            )

            provider = TracerProvider(resource=Resource.create({"service.name": "zyvor-argus"}))
            endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
            if endpoint:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

                provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            else:
                provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
            trace.set_tracer_provider(provider)
            _tracer = trace.get_tracer("zyvor-argus")
        except ImportError:
            _tracer = False
        return _tracer


@contextmanager
def start_span(name: str, **attributes: Any) -> Iterator[Any]:
    """`with start_span("job.execute", job_id=..., job_kind=...) as span:` --
    `span` is None when tracing is disabled/unavailable; callers that want to
    set additional attributes conditionally should guard with `if span:`."""
    tracer = _get_tracer()
    if not tracer:
        yield None
        return
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(key, value)
        yield span


def set_span_error(span: Any, error: str) -> None:
    if span is None:
        return
    from opentelemetry.trace import Status, StatusCode

    span.set_status(Status(StatusCode.ERROR, str(error)[:500]))
    span.set_attribute("error", True)
