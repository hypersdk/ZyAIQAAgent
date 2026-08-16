# Regression Agent (Phase 2)

Screenshot-based visual regression detection for Zyvor UI tests.

## Planned capabilities

- Capture baseline screenshots per test on first run
- Compare subsequent runs using pixelmatch / perceptual diff
- Flag visual regressions with diff images in `screenshots/`
- Optional LangGraph node: enable with `ENABLE_REGRESSION=true`

## Usage (Phase 2)

```bash
ENABLE_REGRESSION=true argus test run
```

## Implementation status

Stub only — `compare_screenshots.py` is a placeholder.
