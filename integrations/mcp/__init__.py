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

"""MCP server exposing Mission Control's job API to MCP clients (e.g. Hermes Agent).

Talks only to the existing `/api/v2` HTTP API over a Bearer service token — it
does not import `orchestrator.*` and has no access to Playwright/LangGraph
internals. See docs/mcp-server.md for setup and connection recipes.
"""
