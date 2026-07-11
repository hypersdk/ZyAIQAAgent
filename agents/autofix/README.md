# Autofix Agent

LLM-powered selector repair with optional self-healing.

## Modes

| Flag | Behavior |
|------|----------|
| `ENABLE_AUTOFIX=true` | Generate selector fix suggestions on failure |
| `ENABLE_AUTOFIX_APPLY=true` | Patch `tests/manual/` and `tests/generated/` specs and re-run |
| `AUTOFIX_MAX_RETRIES=2` | Max self-heal re-execution attempts |

## Flow

```
fail → analyze → autofix → apply_autofix → execute (loop) → report
```

## Files

- `agents/autofix/agent.py` — LLM/stub suggestions
- `agents/autofix/apply.py` — patch test source files
- `orchestrator/nodes/apply_autofix.py` — graph node
