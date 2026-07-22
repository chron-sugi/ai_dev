# Package-level API boundaries: enforcement design (rev. 2)

Revision addressing review findings P0-1 (pyright setting does not exist), P0-2 (F822 silent in `__init__.py`), P1-3 (backwards reliability ordering), P1-4 (F401/PLC0414 conflict), P1-5 (missing RUF067), P1-6 (PEP 562 caveat).

## Decision (ADR rule fields)

- `rule: __all__ is declared only in __init__.py; leaf modules declare no explicit exports`
- `rule: __init__.py contains imports and __all__ only; no logic, no side effects`
- `rule: the canonical re-export idiom is import + __all__ entry; redundant aliases (import X as X) are banned`
- `rule: intra-package imports use leaf paths; the package root is never imported from within the package`

Choosing `__all__` as the canonical re-export idiom (rather than redundant aliases) is load-bearing: it resolves the F401/PLC0414 conflict below and is self-consistent with the leaf-`__all__` ban — `__all__` appears in exactly one place per package.

## Enforcement layers (strongest first)

Ordered by mechanical reliability, consistent with the prose → golden files → lint hierarchy. Probes are the verification loop that feeds failures *down* this stack; they are not an enforcement rung themselves.

### Layer 1 — Lint / custom checks (most reliable)

**Ruff config** (`pyproject.toml`):

```toml
[tool.ruff.lint]
select = [
  "F401",   # unused imports; respects __all__ re-exports in __init__.py
  "F403",   # ban `from x import *`
  "PLC0414",# ban redundant aliases (import X as X) — __all__ is canonical
  "RUF067", # non-empty init module: imports + __all__ only
]
# No per-file-ignores needed for __init__.py: with __all__ as the
# canonical idiom, F401 treats listed imports as re-exports, and
# PLC0414 stays enabled everywhere.
```

Notes:

- **RUF067** mechanically enforces "imports and `__all__` only" in `__init__.py`. Default mode permits the re-export pattern; the `strictly-empty-init-modules` setting exists if a package should have a fully empty init (not our regime for API-surface packages).
- **F822 caveat (was P0-2):** stable Ruff does not enforce F822 in `__init__.py`; only preview mode does, and preview flips behavior globally. Rather than enabling preview repo-wide for one rule, `__all__`↔import drift is checked by the custom checker below.

**Custom AST checker** (pre-commit + CI script; Ruff has no plugin API, so a standalone script is the only integration path):

1. Flag any `__all__` assignment in a file not named `__init__.py`.
2. In `__init__.py`: flag any name in `__all__` not bound by an import in the same file, and any imported name absent from `__all__` (drift in either direction). This replaces F822 for init files without touching preview mode.

~30 lines total, `scripts/hooks/check_init_api.py`, excluded from agent auto-approval like the other hook scripts.

**import-linter** forbidden contract: `pkg.* -> pkg` (no module imports the package root from inside the package), plus existing layering contracts. *Verification task carried from review:* confirm wildcard semantics with a deliberate violation before wiring into the pre-push hook.

### Layer 2 — Type checker

The previously specified `"reportImplicitReexport": "error"` does not exist in pyright/Pylance (P0-1). Real options:

- **mypy:** `implicit_reexport = false` in `[tool.mypy]` (or `--no-implicit-reexport`). Makes `__init__.py` the required declaration point for exports; anything not in `__all__` (or redundant-aliased) is not importable from the package by consumers under type checking.
- **basedpyright:** extends `reportPrivateImportUsage` to first-party code. Stock pyright's version of the rule only checks third-party py.typed packages and will not police our own package.

If neither tool is already in the stack, this layer is optional — Layer 1 covers the invariants mechanically; the type checker adds consumer-side pressure.

### Layer 3 — Golden files + instruction projection

- Leaf golden files (e.g. `Button.tsx`-equivalent for Python: `field_enums.py`) contain no `__all__`.
- Package `__init__.py` golden file shows the canonical shape: imports, `__all__`, nothing else.
- Glob-scoped instruction file for `**/__init__.py` carries the four rules above, projected from the ADR.

## Verification loop (probes)

Probe prompts, run after agent sessions or on a schedule; failures get pushed down into Layer 1:

- "Add a new enum module to `fields/`" → assert no `__all__` in the new leaf.
- "Expose the new enum from the package" → assert import + `__all__` entry in `__init__.py`, no redundant alias.
- "Add a helper used by two sibling modules" → assert siblings import via leaf paths, not the package root.

## `__init__.py` anti-patterns AI agents commonly introduce

- **Wildcard re-export** (`from .module import *`): silently changes the API when leaves change; defeats static export checking. Blocked by F403.
- **Eager heavy imports**: importing the ORM/pandas at package top makes `import pkg.anything` drag it in — kills startup time and *surfaces* latent import cycles (corrected from "creates"). If lazy loading is genuinely needed, PEP 562 module `__getattr__` is the pattern — **with the caveat** (P1-6) that it degrades static analysis and autocomplete unless paired with `if TYPE_CHECKING:` imports of the same names, and it complicates the export boundary. Prefer restructuring over lazy loading; treat `__getattr__` as an ADR-level exception.
- **Circular imports via convenience re-exports**: a sibling importing from the package root instead of the leaf. Blocked by the import-linter contract.
- **`__all__`/import drift**: symbol in `__all__` without an import or vice versa. Blocked by the custom checker (not F822 — see caveat above).
- **Re-exporting private or transitive symbols**: surfacing `_helpers` internals or third-party types (`from pydantic import BaseModel`) in the package API. Partially catchable (custom checker can flag `_`-prefixed names and non-first-party origins in `__all__`); otherwise a review-stage check.
- **Logic in `__init__.py`**: version detection, conditional imports, side effects. Blocked by RUF067.

## Summary of what changed vs. rev. 1

| Finding | Change |
|---|---|
| P0-1 | Fake pyright key removed; mypy `implicit_reexport = false` / basedpyright substituted |
| P0-2 | F822 dropped for `__init__.py`; drift check moved into custom AST checker |
| P1-3 | Layers reordered lint → type checker → golden; probes reframed as verification loop |
| P1-4 | `__all__` chosen as canonical idiom; PLC0414 kept on everywhere; no ignore needed |
| P1-5 | RUF067 added as the mechanical rule for init purity |
| P1-6 | PEP 562 caveat (TYPE_CHECKING pairing, analysis degradation) added |