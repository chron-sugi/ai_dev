---
type: reference
title: Backend
scope: backend
updated: 2026-07-18
---

# Backend — Reference

Current-state registry of supported backend tooling, libraries, and conventions. Mutable by design; kept current via PR review. Entries link to an ADR only when the addition was a contested decision. See `docs/adrs/adr-0002-reference-documentation.md` for the document-class rationale.

## Type checking

### mypy — explicit re-exports

| Field | Value |
|---|---|
| **Configuration** | `no_implicit_reexport = true` under `[tool.mypy]` in `pyproject.toml`. |
| **What it does** | Names imported into a module are not re-exported unless declared via `__all__` (or a redundant alias); consumers importing an undeclared name from a package root fail type checking. |
| **Rationale** | Makes `__init__.py` the required declaration point for a package's public API dynamically, across all packages, without maintaining a per-package banned-import list (e.g. ruff TID251). Consumer-side pressure complementing the lint-layer init-purity rules; see `docs/research/pyhon/package_level_boundaries.md` (Layer 2). |
| **ADR** | — |
| **Rule** | `A package exports only what its __init__.py declares in __all__; do not import undeclared names through a package root.` |

## Linting

Rules live in `ruff.toml` at the repository root; every enabled rule has an entry here.

### ruff TID251 — banned APIs

| Field | Value |
|---|---|
| **Configuration** | `TID251` in `lint.extend-select`; per-decision entries under `[lint.flake8-tidy-imports.banned-api]` in `ruff.toml`. |
| **What it does** | Fails lint on any import or reference to a banned symbol or module, printing the entry's `msg` at the violation site. |
| **Rationale** | The projection target for ADRs: moved symbols, deprecated internal APIs, and rejected libraries are banned per-decision, with `msg` pointing at the ADR ID so the fix is discoverable at the point of error. Highest-leverage rule because each entry is authored from a specific decision. |
| **ADR** | — |
| **Rule** | `When an ADR moves a symbol, deprecates an internal API, or rejects a library, add a banned-api entry in ruff.toml whose msg names the ADR ID.` |

### ruff F401 — unused imports, no init exemption

| Field | Value |
|---|---|
| **Configuration** | `F401` (ruff default select) with `ignore-init-module-imports = false` under `[lint]` in `ruff.toml`. The option is deprecated as of ruff 0.14 — flagging `__init__.py` imports becomes the always-on behavior — so drop the line when ruff removes it. |
| **What it does** | Flags unused imports everywhere, including `__init__.py`; an import there survives only as a redundant alias (`import x as x`) or a name listed in `__all__`. |
| **Rationale** | Shim-detection companion to mypy's `no_implicit_reexport`: forces intentional re-exports to be declared explicitly, so `__init__.py` cannot silently accumulate pass-through imports. Producer-side twin of the consumer-side type-checking rule above. |
| **ADR** | — |
| **Rule** | `Re-exports in __init__.py must be declared via an import-as alias or __all__; delete any other unused import.` |

### ruff PGH003/PGH004 — no blanket suppressions

| Field | Value |
|---|---|
| **Configuration** | `PGH003` and `PGH004` in `lint.extend-select` in `ruff.toml`. |
| **What it does** | Bans bare `# type: ignore` (PGH003) and bare `# noqa` (PGH004); every suppression comment must name the specific error code it suppresses. |
| **Rationale** | A bare suppression hides every current and future error on that line, not just the one it was written for. The ruff twin of mypy's ignore-without-code. |
| **ADR** | — |
| **Rule** | `Every # type: ignore or # noqa must name the specific code it suppresses; never use the bare form.` |

### ruff ERA001 — no commented-out code

| Field | Value |
|---|---|
| **Configuration** | `ERA001` in `lint.extend-select` in `ruff.toml`. |
| **What it does** | Flags lines of commented-out code so they fail lint instead of merging. |
| **Rationale** | Agents leave dead code commented "just in case" instead of deleting it. Commented code is a contamination vector: future agents read it as a valid pattern. Version control already preserves deleted code. |
| **ADR** | — |
| **Rule** | `Delete dead code; never comment it out. Git history is the archive.` |

### ruff T201/T203 — no print/pprint

| Field | Value |
|---|---|
| **Configuration** | `T201` and `T203` in `lint.extend-select` in `ruff.toml`. |
| **What it does** | Fails lint on any `print` (T201) or `pprint` (T203) call. |
| **Rationale** | Agents debug with print statements and forget them; banning them mechanically forces the logging discipline we actually want in production code. |
| **ADR** | — |
| **Rule** | `Use the logging framework, never print or pprint, in library and application code.` |

### ruff RUF100 — unused noqa

| Field | Value |
|---|---|
| **Configuration** | `RUF100` in `lint.extend-select` in `ruff.toml`. |
| **What it does** | Flags `# noqa` comments that no longer suppress any actual violation, so they are removed when the underlying error disappears. |
| **Rationale** | Garbage-collects suppression comments that outlived their error — the same lifecycle hygiene as mypy's `warn_unused_ignores`. Stale suppressions mislead readers about what the line is allowed to do. |
| **ADR** | — |
| **Rule** | `Remove any noqa comment that no longer suppresses a live violation.` |

## Entry template

Copy for new entries:

```markdown
### <Name>

| Field | Value |
|---|---|
| **Configuration** | <what is configured / supported> |
| **What it does** | <mechanical effect in the repo> |
| **Rationale** | <why it was added, one or two sentences> |
| **ADR** | <link to docs/adrs/... or —> |
| **Rule** | `<atomic, projectable rule, or omit row>` |
```
