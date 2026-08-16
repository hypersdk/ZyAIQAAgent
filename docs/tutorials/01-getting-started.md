# Tutorial 1 — Getting Started

Install the agent, run the built-in smoke tests against zyvor.dev, and read your first report. No LLM key, no GitHub token — the minimal path.

**Prerequisites:** Python 3.9+ (3.11 recommended), Node.js 20+, Git.

---

## 1. Clone and install

```bash
git clone <this-repo>
cd Zyvor Argus

cp .env.example .env
make install
```

`make install` does three things:

1. `pip install -e ".[dev]"` — installs the `argus` CLI and Python deps
2. `npm install` — installs Playwright and TypeScript
3. `npx playwright install --with-deps chromium` — downloads the browser

Verify:

```bash
argus --help
```

You should see the command list: `run`, `test`, `generate`, `discover`, `create`, `regression`, `serve`.

## 2. Configure the target

Open `.env`. For this tutorial only one line matters:

```bash
ZYVOR_BASE_URL=https://zyvor.dev
```

Leave the LLM and GitHub sections empty — everything in this tutorial works without them.

## 3. Run the smoke tests

```bash
argus test exec
```

This runs the hand-written specs in `tests/manual/` (homepage, navigation, product suite, visual baseline placeholders) with Chromium:

```
Running Playwright tests against https://zyvor.dev...
Results: 11 passed, 0 failed
```

Behind the scenes, custom fixtures captured console logs, network errors, and API calls for every test — that's what the later pipeline stages analyze.

## 4. Run the full pipeline

```bash
argus test run --source local
```

Without `--spec`, this uses the example spec `prompts/examples/vm-create.md`. The pipeline:

1. **parses** the spec into structured requirements (rule-based, since no LLM key is set)
2. **generates** a Playwright test into `tests/generated/` from the Jinja2 template
3. **executes** everything in `tests/manual/` + `tests/generated/`
4. **analyzes** logs, builds the report, and (if Node can render it) a PDF

```
Results: 12 passed, 0 failed, 12 total
Generated tests: 1 file(s)
Report: /…/reports/qa-summary.html
PDF report: /…/reports/qa-summary.pdf
```

## 5. Read the report

```bash
open reports/qa-summary.html      # macOS
# or the interactive Playwright report:
npm run report
```

The HTML report shows the summary block, per-test results with durations and browsers, and — when tests fail — error messages, screenshots, videos, and the failure analysis section.

## 6. Look at what was generated

```bash
cat tests/generated/req-administrator-creates-a-vm*.spec.ts
```

Note the conventions every generated test follows: fixtures from `playwright/fixtures/base`, `waitForPageReady()` after navigation, `toBeVisible()` assertions, and a console-error check at the end. Your hand-written tests in `tests/manual/` should follow the same pattern (see [test-authoring.md](../test-authoring.md)).

## Where you are now

```
spec (.md) ──► parse ──► generate ──► execute ──► report
                                        ▲
                     tests/manual/ ─────┘  (always included)
```

**Next:** [Tutorial 2 — From spec to test](02-spec-to-test.md), where you write your own spec instead of using the example.
