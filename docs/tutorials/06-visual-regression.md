# Tutorial 6 — Visual Regression

Catch unintended visual changes by pixel-comparing screenshots against stored baselines.

**Prerequisites:** [Tutorial 1](01-getting-started.md).

---

## 1. How it works

```
test run (screenshots on) ──► screenshots/current/
                                    │  pixel diff (Pillow or Rust)
screenshots/baselines/  ────────────┤
                                    ▼
                     pass (≤ threshold) / fail (> threshold)
                              + screenshots/diffs/diff-*.png
```

Screenshots come from two places: everything Playwright captured in `test-results/`, plus explicit `captureBaseline(page, 'name')` calls in tests (see `tests/manual/visual-regression.spec.ts`).

## 2. Capture baselines

First run — record what "correct" looks like:

```bash
make regression-update
# equivalent: ENABLE_REGRESSION=true argus vision regression --update-baselines
```

```
  ✓ homepage-hero.png: 0.0% — Created baseline: …/screenshots/baselines/homepage-hero.png
  ✓ products-section.png: 0.0% — Created baseline: …
```

Commit the baselines if you want them versioned (recommended for CI):

```bash
git add screenshots/baselines/
```

## 3. Compare

On subsequent runs:

```bash
make regression
# equivalent: ENABLE_REGRESSION=true argus vision regression
```

```
  ✓ homepage-hero.png: 0.31% — pass
  ✗ products-section.png: 4.87% — Visual diff 4.87% exceeds threshold 1.0%
```

On failure, inspect the diff image — changed pixels glow against black:

```bash
open screenshots/diffs/diff-products-section.png
```

If the change was intentional, re-capture: `make regression-update`.

## 4. Regression inside the full pipeline

Set in `.env`:

```bash
ENABLE_REGRESSION=true
REGRESSION_THRESHOLD=1.0     # percent; raise for noisy pages
```

Now every `argus test run` compares screenshots, and a regression failure routes the pipeline down the **fail** branch — failure analysis, optional autofix, and a report flagging the diffs. `ENABLE_REGRESSION=true` also switches Playwright to capture screenshots for *every* test, not just failures.

## 5. Add a page to visual coverage

Add a test that captures a named baseline:

```typescript
// tests/manual/visual-regression.spec.ts
test('pricing page visual baseline', async ({ page }) => {
  await page.goto('/pricing');
  await waitForPageReady(page);
  await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();

  if (process.env.ENABLE_REGRESSION === 'true') {
    await captureBaseline(page, 'pricing-page');
  }
});
```

Then `make regression-update` once to record it.

## 6. Faster diffs with Rust (optional)

For large screenshot suites, the Rust binary is much faster than Pillow:

```bash
make rust                     # needs a Rust toolchain (cargo)
# .env
ENABLE_RUST_PROCESSOR=true
```

The bridge (`agents/regression/rust_bridge.py`) finds `rust/target/release/zyvor-diff` automatically, or set `ZYVOR_DIFF_BINARY=/path/to/zyvor-diff`. Same threshold semantics, same JSON diff output.

## Tips

- **Dynamic content is the enemy.** Carousels, timestamps, A/B banners diff every run. Keep visual tests on stable pages, or raise the threshold for those baselines.
- Baseline and current images with different dimensions are resized before comparison — recapture baselines after viewport/layout changes rather than trusting resized diffs.
- Baselines are keyed by filename; renaming a capture orphan the old baseline (delete it manually).

**Next:** [Tutorial 7 — Self-healing autofix](07-self-healing-autofix.md).
