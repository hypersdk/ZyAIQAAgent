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

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class RequestContext:
    tenant_id: str
    access_levels: tuple[str, ...]
    product: str | None = None
    document_type: str | None = None


_context: ContextVar[RequestContext | None] = ContextVar("qa_request_context", default=None)


def current_context() -> RequestContext:
    value = _context.get()
    if value is None:
        raise RuntimeError("Request context is not configured")
    return value


@contextmanager
def request_context(context: RequestContext) -> Iterator[None]:
    token = _context.set(context)
    try:
        yield
    finally:
        _context.reset(token)
