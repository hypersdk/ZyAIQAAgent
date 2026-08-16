# Tutorial 3 — Natural-Language Tests

Generate and run a test from a single English sentence. This is the quickest way to add a one-off check.

**Prerequisites:** [Tutorial 1](01-getting-started.md), plus an **LLM key** — this is the one feature with no non-LLM fallback.

---

## 1. Configure an LLM

In `.env`:

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
```

(Any supported provider works — see [configuration.md](../configuration.md#llm-provider). For a local, free option: `LLM_PROVIDER=ollama` with an Ollama server running.)

## 2. Create a test

```bash
argus test create "Verify the homepage shows the Schedule Demo button and all product names"
```

What happens (`agents/nl_create/`):

1. The LLM converts your sentence into structured requirements (`prompts/nl_create.md`) — inferring the route, steps, and assertions.
2. The requirements are saved to `tests/fixtures/requirements.json`.
3. The generator writes the Playwright spec into `tests/generated/`, subject to the same quality gate as spec-driven generation.

```
Creating test from: Verify the homepage shows the Schedule Demo button and all product names
Generated 1 test file(s):
  /…/tests/generated/nl-001-….spec.ts
```

## 3. Create and run in one step

```bash
argus test create "Check that /vm page loads and mentions KubeVirt migration" --execute
```

`--execute` runs the generated test(s) immediately and exits non-zero on failure.

## 4. Writing good descriptions

The LLM has to infer the user journey, so give it anchors:

| Weak | Better |
|------|--------|
| "test the products" | "Verify `/products` lists HyperSDK, Zeus OS, and PacketWolf" |
| "check demo button" | "Check the homepage Schedule Demo button is visible and links somewhere" |
| "vm stuff works" | "Verify /vm page loads with a heading and mentions VMware migration" |

Rules of thumb:

- **Name the route** (`/products`, `/vm`) when you know it — otherwise the LLM guesses.
- **Name exact visible text** you expect — it becomes `getByText` assertions.
- One journey per `create` call; run it multiple times for multiple flows.

## 5. Where NL tests fit

NL-created tests land in `tests/generated/` like spec-driven ones — they're regenerated artifacts, not source of truth. For checks you want to keep permanently:

- promote the file to `tests/manual/` (it becomes hand-maintained), or
- turn the description into a markdown spec ([Tutorial 2](02-spec-to-test.md)) so it's versioned and reviewable.

**Next:** [Tutorial 4 — GitHub integration](04-github-integration.md): pull specs from your product repo and comment on PRs.
