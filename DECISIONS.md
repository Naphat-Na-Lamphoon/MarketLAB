# Decisions

- M0/M1 development is local-first until Docker/PostgreSQL is available.
- The simulated channel remains the default and no live ad SDK is added.
- `uv run` is the supported fallback for running backend tests when the selected Python interpreter is externally managed.
- M1 preserves the existing `blocked_by_guardrail`, `winner`, and `inconclusive` names while adding names that match the brief.
