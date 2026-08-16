# Tutorial 7 — Self-Healing Autofix

When the product's UI changes and selectors break, the agent can diagnose the failure, suggest repaired selectors, patch the test files, and re-run — automatically.

**Prerequisites:** [Tutorial 1](01-getting-started.md); an LLM key for useful suggestions (a rule-based stub exists but only produces generic hints).

---

## 1. The failure branch

Recall the pipeline routing: any test failure (including regression/API/log failures) sends the run down the fail branch.

```
execute ─► … ─► fail? ─► analyze ─► autofix ─► apply_autofix ─► re-execute
                                                    │                │
                                                    └── report ◄─────┘ (when fixed,
                                                                        retries exhausted,
                                                                        or apply disabled)
```

Three flags control how far down this path the agent goes:

| Flag | Effect |
|------|--------|
| `ENABLE_LLM_ANALYSIS=true` *(default)* | `analyze`: root cause, affected area, suggested fix, flake assessment — built from error messages, console/network logs, and artifact paths |
| `ENABLE_AUTOFIX=true` | `autofix`: concrete selector replacement suggestions per failed test |
| `ENABLE_AUTOFIX_APPLY=true` | `apply_autofix`: patch the spec files in place and re-run failed tests |

## 2. Suggestions only (safe mode)

```bash
# .env
ENABLE_AUTOFIX=true
ENABLE_AUTOFIX_APPLY=false
```

Run the pipeline with a failing test. The report (and PR comment) now includes a **Suggested Fixes** section:

```
### Suggested Fixes
- `page.getByRole('link', { name: /schedule.*demo/i })`
```

Each suggestion carries the original selector, the replacement, a confidence level, and an explanation. You apply them by hand — nothing touches your files.

## 3. Full self-healing

```bash
# .env
ENABLE_AUTOFIX=true
ENABLE_AUTOFIX_APPLY=true
AUTOFIX_MAX_RETRIES=2
```

Now after suggestions are produced:

1. `apply_autofix` locates each failed test's spec file by its test title (searched in `tests/manual/` and `tests/generated/`).
2. It replaces the broken selector with the suggestion (first match, one replacement per suggestion). Low-confidence suggestions with unknown selectors are skipped.
3. If any file was patched, the pipeline **re-executes** the tests.
4. The loop repeats until tests pass or `AUTOFIX_MAX_RETRIES` is exhausted; then the final state is reported.

Patched suggestions are marked in the report: `[applied to homepage.spec.ts]`.

## 4. Try it end to end

Break a test deliberately:

```typescript
// in tests/manual/navigation.spec.ts, change:
const demoCta = page.getByRole('link', { name: /schedule.*demo|book.*demo/i });
// to something wrong:
const demoCta = page.getByRole('link', { name: /request.*quote/i });
```

Run `argus test run --source local` and watch the fail branch: analysis names the test and the missing locator, autofix proposes a role-based selector from the actual error context, apply patches the file, and the re-run goes green.

Afterwards, review what changed:

```bash
git diff tests/
```

## 5. Guardrails and caveats

- **Review patches like any other diff.** Self-healing fixes *selectors*, not *intent* — if the UI genuinely lost the Schedule Demo button, patching the test to match whatever is there would mask a real regression. The failure analysis (flake assessment) helps you judge which case you're in.
- Autofix runs only on the fail branch; passing suites are never touched.
- The retry budget is global per run (`metadata.autofix_retries`), so a flapping test can't loop forever.
- In CI, prefer suggestions-only mode plus a human-reviewed commit; reserve full apply mode for scheduled maintenance runs where you inspect the resulting diff.

**Next:** [Tutorial 8 — Notifications & reports](08-notifications-and-reports.md).
