# Autofix Agent

LLM-powered selector repair with optional self-healing and a persistent
skill store, so a fix that's already been confirmed working doesn't need to
be re-derived by the LLM on the next run.

## Modes

| Flag | Behavior |
|------|----------|
| `ENABLE_AUTOFIX=true` | Generate selector fix suggestions on failure |
| `ENABLE_AUTOFIX_APPLY=true` | Patch `tests/manual/` and `tests/generated/` specs and re-run |
| `AUTOFIX_MAX_RETRIES=2` | Max self-heal re-execution attempts |
| `SKILLS_PATH=.zyvor-qa/skills.json` | Where confirmed fixes are remembered |

## Flow

```
fail → analyze → autofix (skills-first) → apply_autofix → execute (loop) → learn_skills → report
```

`autofix` checks the skill store before calling the LLM for each failed
case; only unmatched failures go to the LLM/stub path. If a patched retry
passes, `learn_skills` records the applied fix (or bumps `times_confirmed`
on an existing one) so it's reused directly next time the same selector
breaks.

The skill store is a local JSON file (gitignored by default, like
`screenshots/baselines`), so it doesn't persist across CI runs unless the
caller persists it — e.g. cache `SKILLS_PATH` with `actions/cache` keyed on
the repo.

## Files

- `agents/autofix/agent.py` — skill lookup, then LLM/stub suggestions
- `agents/autofix/apply.py` — patch test source files
- `agents/skills/store.py` — load/save/lookup/record for the skill store
- `orchestrator/nodes/apply_autofix.py` — graph node
- `orchestrator/nodes/learn_skills.py` — records confirmed fixes as skills
