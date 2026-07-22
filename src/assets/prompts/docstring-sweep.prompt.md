---
agent: coder
description: "Two-phase docstring sweep: inventory the codebase, then write Google-style docstrings per ADR-0001. Run on a dedicated branch."
---

# Docstring Sweep

You are performing a documentation-only sweep of this Python codebase.
Governing decision: **ADR-0001** (Google style; coverage includes private
members; Pydantic fields use `Field(description=...)`). Do not re-litigate
these choices.

**Hard constraint: zero behavior change.** You may add or rewrite
docstrings and `Field(description=...)` arguments. You may not rename,
reorder, reformat, refactor, or "fix" anything else you notice. If you find
a bug, record it in the inventory file — do not touch it.

---

## Phase 1 — Inventory (no code edits)

1. Run the coverage tooling to get ground truth. Do not estimate by
   reading files:
   ```
   interrogate -v .
   ruff check --select D .
   ```
2. Write `.agent/<task-id>/docstring-inventory.md` containing:
   - **Coverage summary**: overall %, per-package %.
   - **Symbol table**: one row per missing or defective docstring —
     `path :: symbol | construct type | state | priority`.
     - *construct type*: module, class, public fn, private fn, method,
       property, Pydantic model, dataclass, dunder, test.
     - *state*: `missing`, `signature-restatement`, `stale` (contradicts
       code), `wrong-format`.
     - *priority*: P1 = public API and anything an agent must not
       misuse (side effects, I/O, invariants); P2 = private helpers with
       non-obvious logic; P3 = trivial one-liner candidates.
   - **Ambiguity list**: symbols whose intent you cannot determine from
     the code. **Never guess intent** — a wrong docstring is worse than
     none, because agents and humans trust it over the code. These get
     `TODO(docstring): intent unclear — <specific question>` and a row
     here for human review.
3. Stop and present the inventory summary before Phase 2.

## Phase 2 — Write (batch by module)

Work module-by-module in priority order. After each batch, re-run
`interrogate` and `ruff check --select D` and fix findings before moving on.

### Content rules — every docstring

**In:** intent (*why this exists*), contract (invariants, units, ranges),
side effects (I/O, mutation, network, global state), `Raises:` for
exceptions callers must handle, concurrency/ordering assumptions.

**Out:** signature restatement, type information already in annotations,
implementation narration ("loops over the list"), historical commentary
("previously this used X"), anything the next edit will silently
invalidate (line numbers, hardcoded values duplicated from constants).

The test: *does this sentence tell a cold reader something the signature
and body do not?* If no, delete the sentence. A precise one-liner beats a
padded multi-section block.

### Per-construct rules

- **Module**: 1–3 lines — what lives here and why it's grouped;
  ownership boundary if relevant ("all Azure DevOps hook adapters").
- **Class**: responsibility + lifecycle (who constructs it, is it
  reusable/stateful/thread-safe). Document invariants that methods rely on.
- **Public function/method**: full Google sections as warranted —
  `Args:` only for params with semantics beyond their name/type (units,
  valid ranges, sentinel values); `Returns:` when non-obvious; `Raises:`
  always when it raises deliberately.
- **Private function/method**: required (ADR-0001), but one line is the
  default: why it was factored out, or the non-obvious trick it performs.
  Expand only when it hides an invariant.
- **Behavior/command methods** (mutating, I/O, `run`/`apply`/`sync`
  style): lead with the effect and its scope, then idempotency
  ("safe to re-run"/"not idempotent"), then failure mode — what state
  remains if it raises midway.
- **Query/accessor methods & properties**: one line; state staleness or
  caching if any. If truly self-evident (`is_empty`), one line, no
  sections.
- **Pydantic models / dataclasses**: class docstring = what the model
  represents and where it's serialized (API, config file, tool schema).
  Every field gets `Field(description=...)` — write descriptions as
  schema-consumer-facing text, since they project into JSON Schema and
  agent tool schemas. No `Args:` section duplicating fields.
- **Dunders**: skip unless behavior is surprising (e.g., `__eq__`
  ignoring a field).
- **Generators/context managers**: `Yields:` and what setup/teardown the
  `with` block guarantees.

### Existing docstrings

Preserve correct ones untouched. Rewrite `signature-restatement` and
`stale` entries — stale is P1 regardless of visibility. Convert
non-Google formats only when already editing that symbol's docstring for
another reason; format-only churn is out of scope for this sweep.

## Closeout

- Final `interrogate -v .` and `ruff check --select D .` must pass.
- Update the inventory file with final coverage % and the unresolved
  ambiguity list.
- Commit in module-sized commits: `docs(docstrings): <package> per ADR-0001`.
- The inventory file follows the standard `.agent/` lifecycle — it is
  review material, removed at task closeout.
