# Tutorial 2 — From Spec to Test

Write a markdown requirement spec, generate Playwright tests from it, and run them. You'll do it first without an LLM (rule-based parsing), then see what changes when an LLM key is present.

**Prerequisites:** [Tutorial 1](01-getting-started.md) completed.

---

## 1. The spec format

The parser understands user-story markdown with an **Acceptance Criteria** section. Create `my-specs/products-page.md`:

```markdown
# Products page shows the full suite

**As a** visitor
**I want to** browse the product catalog
**So that** I can evaluate the platform

## Acceptance Criteria

1. Page loads at `/products`
2. Heading `Products` is visible
3. Content shows `HyperSDK`
4. Content shows `Zeus OS`

## Tags

products, smoke
```

Phrasing matters for the **rule-based parser** (used when no LLM key is set). These patterns are recognized:

| Pattern in criteria | Becomes |
|---------------------|---------|
| `` loads at `/path` `` / `` Navigate to X at `/path` `` | `navigate` step |
| `Click "Button Name"` | `click` step |
| `` Enter name: `value` `` | `fill` step |
| `` X shows `text` `` / `` heading `text` is visible `` | `assert` step |

With an LLM key configured, free-form specs work too — the LLM extracts requirements using `prompts/parser.md`.

## 2. Generate without running

```bash
argus test generate --spec my-specs/products-page.md
```

Output:

```
Generated 1 test file(s):
  /…/tests/generated/req-products-page-shows-the-full-suite-products-page-shows-the-full-suite.spec.ts
```

Two artifacts were written:

- `tests/fixtures/requirements.json` — the structured requirements extracted from your spec
- `tests/generated/*.spec.ts` — the Playwright test

Inspect the requirements JSON to see exactly what the parser understood:

```bash
cat tests/fixtures/requirements.json
```

If a criterion didn't become a step, rephrase it using the patterns above.

## 3. Inspect the generated test

```bash
cat tests/generated/req-products-page*.spec.ts
```

You'll see your steps translated: `page.goto('/products')`, `waitForPageReady(page)`, `getByText("HyperSDK")` visibility assertions, and the standard console-error check.

## 4. Run the full pipeline

```bash
argus test run --source local --spec my-specs/products-page.md
```

This re-parses, re-generates, and executes — your generated test plus everything in `tests/manual/`. Exit code is non-zero if anything fails, so it's CI-safe.

## 5. Add an LLM (optional but recommended)

In `.env`:

```bash
LLM_PROVIDER=anthropic          # or openai, azure, google, ollama
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-5
```

Regenerate:

```bash
argus test generate --spec my-specs/products-page.md
```

Differences with the LLM path:

- The **parser** handles free-form prose, multiple requirements per file, and infers priorities/tags.
- The **generator** writes richer TypeScript (grouped scenarios, role-based locators tuned to your steps) following `prompts/generator.md`.
- Every LLM-generated file passes a **quality gate** (correct navigation path, no `toBeAttached()`, no duplicate bodies, syntax checks). If it fails twice, the deterministic template is used instead — so a bad LLM day can't break your suite.

## 6. Iterating

- Generated files are plain Playwright specs — you can edit them by hand and move them to `tests/manual/` if you want to "adopt" one permanently. Everything in `tests/manual/` is treated as hand-written and always executed.
- Re-running `generate` for the same requirement overwrites the same filename (`req-<id>-<title>.spec.ts`).
- Delete stale generated tests freely; `tests/generated/.gitkeep` keeps the directory.

**Next:** [Tutorial 3 — Natural-language tests](03-natural-language-tests.md): skip the spec file entirely.
