---
id: ADR-0001
title: Python docstring policy — Google style, coverage includes private members
status: accepted
date: 2026-07-16
domain: python-style
projection:
  - .github/instructions/python-docstrings.instructions.md
  - pyproject.toml ([tool.ruff.lint.pydocstyle], [tool.interrogate])
scope: "**/*.py"
rule: "All Python functions, methods (including private/underscore-prefixed), classes, and modules require Google-style docstrings stating intent and contract, not signature restatement. Pydantic model fields require Field(description=...)."
---

# ADR-0001: Python docstring policy

## Context

Agents operate with ephemeral context. Docstrings are persistent, in-file
context that survives across agent sessions; without them, agents
reconstruct intent from signatures and frequently get it wrong. Docstring
emission enforced only via prose instructions drifts — coverage must be
gated mechanically.

Traditional style guidance (PEP 257, Google style guide) permits skipping
docstrings on trivial private helpers. That guidance predates agentic
development, where private members carry no tribal knowledge and are read
cold by agents as often as public ones.

## Decision

1. **Format:** Google style, enforced by Ruff pydocstyle rules
   (`convention = "google"`). Chosen because it is the dominant convention
   in model training data — agents emit it unprompted, minimizing
   enforcement pressure.
2. **Coverage:** All modules, classes, functions, and methods — including
   private/underscore-prefixed — require docstrings. Enforced by
   `interrogate` with `--fail-under=100` (private members are in scope by
   default; do not pass `-i`/`--ignore-private`).
3. **Content:** Docstrings state *why* and *contract* (invariants, side
   effects, raises, units). Restating the signature is a review-rejectable
   defect, not compliance.
4. **Pydantic / dataclasses:** Field-level documentation on Pydantic models
   uses `Field(description=...)`, not comments — descriptions project into
   JSON Schema, OpenAPI, and tool schemas.

## Enforcement layers

| Layer | Mechanism | Catches |
|---|---|---|
| Lint | Ruff `D` rules, `convention = "google"` | Format violations, missing docstrings on public members |
| Coverage | `interrogate --fail-under=100` (pre-commit + CI) | Missing docstrings including private members |
| Golden file | Exemplar module (documented private helper + Pydantic `Field(description=...)`) | Agent pattern-matching |
| Prose | Glob-scoped instruction file (projection of this ADR) | Content quality (why/contract) |

Failures observed in probes or PR review are resolved by tightening the
lint/coverage layer, not by adding instruction prose.

## Rejected alternatives

- **NumPy style** — better for many-parameter scientific APIs; this
  codebase is application code, and NumPy style costs more vertical space
  and more agent steering.
- **reST/Sphinx style** — legacy; hardest to read as plain text, weakest
  fit with what models emit by default.
- **Public-members-only coverage (Ruff D1xx defaults)** — Ruff's missing-
  docstring checks exempt underscore-prefixed names; insufficient for the
  agent-readability goal. Retained for format checking only.
- **Prose-only enforcement** — known to drift past the instruction-volume
  reliability ceiling; prose is the last layer, not the primary one.
- **Docstring-writing via comments on Pydantic fields** — comments do not
  project into schemas; `Field(description=...)` does double duty.
