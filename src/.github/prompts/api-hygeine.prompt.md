---
description: This prompt is used to audit a Python repository for package-API-boundary hygiene, focusing on `__init__.py` files and their use of `__all__`.


---
# Audit prompt: `__init__.py` API-boundary hygiene

<!--
Usage: paste this entire prompt into any coding agent session with repo access.
Designed for general models: deterministic checks, exact commands, fixed output
schema, no judgment calls required. Flagship models may skip the shell commands
and use AST tooling, but must produce the same output schema.
-->

You are auditing a Python repository for package-API-boundary hygiene. This is a **read-only audit**: do not modify, create, or delete any files. Report only.

Follow the three phases in order. Do not skip phases. Do not add checks beyond the rules listed. If you cannot verify something, mark it `UNVERIFIED` — never guess.

---

## Phase 1 — Inventory

Run these commands (or equivalent) and record the results:

```bash
# All package init files
find . -name "__init__.py" -not -path "*/node_modules/*" -not -path "*/.venv/*"

# All files declaring __all__
grep -rln "^__all__" --include="*.py" . | grep -v -e node_modules -e .venv

# Star imports anywhere
grep -rn "import \*" --include="*.py" . | grep -v -e node_modules -e .venv

# Redundant aliases (import X as X) in init files
grep -rn "import \(\w*\) as \1" --include="__init__.py" . 2>/dev/null || \
grep -rnE "import ([A-Za-z_][A-Za-z0-9_]*) as \1\b" --include="__init__.py" .
```

Output the inventory as a table before proceeding:

| # | File | Is `__init__.py`? | Has `__all__`? | Line count |
|---|------|-------------------|----------------|-----------|

Include every file from the first two commands. If the repo has more than 40 such files, list the first 40 and state the total count.

---

## Phase 2 — Checks

Evaluate each rule against the inventory. Each rule has an ID, a deterministic test, and a severity. Apply the test exactly as written.

**R1 — Leaf `__all__` ban (P1).**
Test: any file from the `__all__` grep whose filename is not `__init__.py`.
Every match is one finding.

**R2 — Init purity (P1).**
Test: any `__init__.py` containing statements other than (a) `import`/`from ... import` statements, (b) a single `__all__` assignment, (c) comments and docstrings. Function defs, class defs, conditionals, version detection, `try/except` around imports, and any call expressions are violations.
Every violating file is one finding; list the offending line numbers.

**R3 — Canonical re-export idiom (P1).**
Test A: any `from x import *` in an `__init__.py` (star re-export).
Test B: any redundant alias `import X as X` / `from .m import X as X` in an `__init__.py`.
Both are violations: the canonical idiom is a plain import plus an `__all__` entry.

**R4 — No package-root imports from inside the package (P0 if a cycle exists, else P1).**
Test: inside any package directory `pkg/`, a module that imports from `pkg` itself (e.g. `from pkg import X` or `from .. import X` resolving to the package root that re-exports leaves) instead of the leaf module.
Mark `UNVERIFIED` if you cannot resolve whether a relative import targets the root; do not guess.

**R5 — `__all__`/import drift (P0).**
Test: for each `__init__.py` with `__all__`: (a) every name in `__all__` is bound by an import in the same file; (b) every imported public name appears in `__all__`. Either direction of mismatch is one finding per name.

**R6 — Private or transitive re-exports (P1).**
Test: any `__all__` entry or `__init__.py` import that (a) starts with `_`, or (b) originates from a third-party package (not the repo's own code, not stdlib).

**R7 — Eager heavy imports (P2, advisory).**
Test: `__init__.py` imports of known heavy modules (pandas, numpy, sqlalchemy, torch, an ORM, requests/httpx at module level). Flag as advisory; do not flag stdlib or intra-package imports.

---

## Phase 3 — Report

Produce exactly this structure. Do not add sections. Do not editorialize outside the template.

```markdown
# __init__.py API audit: <repo name>

## Summary
- Files inventoried: N init files, N leaf files with __all__
- Findings: N P0, N P1, N P2, N UNVERIFIED

## Findings

**<Rule ID>-<n>. <short title>** (<severity>)
- File: <path>:<line(s)>
- Problem: <one sentence, cite the rule>
- Remediation: <from the remediation table below, adapted to this file>

(repeat per finding; group by severity, P0 first)

## UNVERIFIED
(items you could not resolve, with what a human should check)

## Clean
(rules with zero findings — list rule IDs only)
```

### Remediation table (use these; do not invent alternatives)

| Rule | Remediation |
|------|-------------|
| R1 | Delete the leaf `__all__`. If any symbol in it is part of the public API, add an import + `__all__` entry to the package's `__init__.py` instead. |
| R2 | Move logic out of `__init__.py` into a named module; init keeps imports and `__all__` only. |
| R3 | Replace star imports and redundant aliases with explicit `from .leaf import Name` plus a `Name` entry in `__all__`. |
| R4 | Change the import to target the leaf module directly (`from pkg.leaf import X`). |
| R5 | Add the missing import, or remove the stale `__all__` entry — whichever matches the package's actual public API. If unsure which, mark UNVERIFIED. |
| R6 | Remove `_private` names from the API. For third-party types, import them in the consuming module directly, not via the package root. |
| R7 | Advisory only: note the import; recommend the maintainer confirm it is required at package-import time. |

### Example finding (format reference)

**R5-1. `FieldType` listed in `__all__` but never imported** (P0)
- File: `backend/src/metsec/fields/__init__.py:12`
- Problem: `__all__` contains "FieldType" but no import in this file binds that name (R5a); `from x import *` on this package would raise NameError.
- Remediation: add `from .field_enums import FieldType`, or remove the entry if the symbol is no longer public.

---

## Constraints (repeat before finishing)

1. Read-only. No file modifications.
2. Only the seven rules above. Do not report style, formatting, or typing issues.
3. Severities are fixed per rule; do not escalate or downgrade.
4. `UNVERIFIED` over speculation, always.