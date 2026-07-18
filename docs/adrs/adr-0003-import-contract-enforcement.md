---
id: ADR-0003
title: Enforce import placement contracts at pre-push and CI, not pre-commit
status: accepted
date: 2026-07-16
projection: [instruction-files, hooks, ci]
scope: repo
rule: "lint-imports runs at pre-push and in CI; never add import contracts to pre-commit; agents run lint-imports as part of the verify/closeout step after editing */models.py or shared/**"
---

# Enforce import placement contracts at pre-push and CI, not pre-commit

## Status

Accepted — 2026-07-16

## Context

Type placement rules (see companion ADR: shared/ vocabulary package, no domain-to-domain imports) are enforced mechanically via `import-linter` contracts (`shared-independence`, `domain-independence`). The open question was which layer runs the check.

The threat model: a cross-domain import is the most likely agent violation of the architecture. When an agent needs a type, it imports from wherever grep located it — a one-line, innocent-looking diff. Prose (the ADR alone) does not reliably prevent this; enforcement must be mechanical.

Constraints specific to agent-driven development:

- Agents commit far more frequently than humans; per-commit hook latency compounds across a session.
- Agents bypass blocking hooks (`--no-verify`) when a check interrupts mid-flow.
- Agents self-correct best when a check fails in-session, while the change is in working memory — not at PR review time.
- A violating import sitting in a local commit costs nothing; it only matters that it cannot reach the shared branch.

## Decision

Enforcement is layered, matching the existing `.agent/` tracking enforcement pattern:

1. **CI (authoritative)** — `lint-imports` runs in CI; this is the layer an agent cannot bypass.
2. **Pre-push (fast local backstop)** — plain git `pre-push` hook runs `lint-imports`, covering manual and agent push paths before CI.
3. **Harness-level (feedback, not enforcement)** — agents run `lint-imports` in the verify/closeout step; optionally a `PostToolUse` check fires on edits to `*/models.py` and `shared/**` for immediate in-session feedback.

Pre-commit is reserved for fast, per-commit-relevant checks (formatters). Import contracts are excluded from it.

## Rejected alternatives

- **Pre-commit hook** — rejected: violations are rare while agent commits are frequent, so latency cost is paid on every commit for a check that almost never fires there; agents route around blocking commit hooks with `--no-verify`; nothing is gained by catching the violation at commit rather than push.
- **Documentation only (ADR without mechanical enforcement)** — rejected: prose instructions do not survive agent sessions that never loaded them; the violation is a one-line diff that passes human review easily.
- **CI only, no local layer** — rejected: feedback arrives at PR time, outside the agent session that made the change; the agent that could self-correct cheapest never sees the failure.

## Consequences

- New domain packages must be added to both import-linter contracts in the same commit that creates the package (checklist item in the domain-scaffold instruction file).
- Hook scripts remain excluded from agent auto-approval per existing policy, preventing self-modification of the enforcement layer.
- The `PostToolUse` surgical check is optional; if session noise outweighs its value, the verify/closeout run alone provides in-session feedback.
