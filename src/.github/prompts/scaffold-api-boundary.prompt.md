# Scaffold: API boundary subpackage

You are scaffolding a new API boundary in this repository. The decision is already
made and approved — do not re-litigate it. Your job is to make the boundary exist
structurally and mechanically before any feature code is written.

## Inputs

- **ADR**: `docs/adr/{{ADR_ID}}.md` — read this first. The `rule` field is the
  atomic statement of the boundary. The rejected-alternatives section is binding.
- **Package**: `src/app/{{PACKAGE}}/`
- **Direction** (from ADR `scope`/`rule`): whether the contract is
  `forbidden`-only (protect internals) or `layers` (also constrain what this
  package may import).

## Hard constraints

- Scaffold only. **No implementation code, no business logic, no speculative
  helpers.** Every module body is a docstring plus (where required) explicit
  re-exports.
- The public surface is defined **exclusively** in `__init__.py` via explicit
  imports and `__all__`. If it is not re-exported there, it is internal.
- Internal modules live under `src/app/{{PACKAGE}}/_internal/`. Do not use
  bare top-level modules for anything not on the public surface.
- Do not touch `scripts/hooks/**` or `.github/hooks/**`.
- Do not generate or modify Copilot instruction files. That projection happens
  in a separate step and is out of scope here.

## Steps

### 1. Structure

Create:

```
src/app/{{PACKAGE}}/
    __init__.py          # public surface: explicit imports + __all__, module docstring
                         # citing {{ADR_ID}} in the first line
    py.typed
    _internal/
        __init__.py      # empty, one-line docstring: "Internal. Do not import from outside {{PACKAGE}}."
```

The top-level `__init__.py` is the golden file for this boundary. Its docstring
must state, in one sentence each: what the package owns, and that consumers
import from `app.{{PACKAGE}}` only. Stub the public names declared in the ADR
as imports from `_internal` modules; create those `_internal` modules with
docstring-only bodies and `raise NotImplementedError` function/class stubs
matching the ADR's declared surface. No signatures beyond what the ADR names.

### 2. Mechanical enforcement

Add `import-linter` as a dev dependency (respect the repo's existing dependency
manager — check before assuming pip/uv/poetry).

In `pyproject.toml`, add contracts under `[tool.importlinter]`:

**Always:**

```toml
[[tool.importlinter.contracts]]
name = "{{PACKAGE}} internals are private"
type = "forbidden"
source_modules = ["app"]
forbidden_modules = ["app.{{PACKAGE}}._internal"]
ignore_imports = ["app.{{PACKAGE}} -> app.{{PACKAGE}}._internal"]
```

**If the ADR defines a dependency direction:** add a `layers` contract encoding
it instead of duplicating with a second forbidden contract. Copy the layer
ordering verbatim from the ADR — do not infer layers the ADR does not name.

Wire `lint-imports` into the existing quality gates: add it to pre-commit config
and to whichever CI job runs lint. Match the repo's existing patterns for both;
do not invent a new workflow file if a lint job exists.

### 3. Verify

Run, in order, and fix failures before proceeding:

1. `lint-imports` — passes clean.
2. A deliberate violation check: add a temporary import of
   `app.{{PACKAGE}}._internal` from any module outside the package, confirm
   `lint-imports` **fails**, then remove it. Record the failing output in your
   task notes — a contract that has never been observed to fail is unverified.
3. `python -c "import app.{{PACKAGE}}"` — the surface imports cleanly.
4. Existing test suite still passes.

### 4. Report

Write to `.agent/{{TASK_ID}}/scaffold-report.md`:

- Tree of created files
- Contracts added, with the observed failure output from the violation check
- Any deviation from this prompt, with reason
- Open items for the implementation task

## Acceptance criteria

- [ ] Package imports cleanly; public surface matches ADR-declared names exactly
- [ ] `_internal/` exists and holds all non-surface modules
- [ ] Forbidden contract present; layers contract present iff ADR defines direction
- [ ] Violation check performed and contract observed failing
- [ ] `lint-imports` in pre-commit and CI lint path
- [ ] Zero implementation logic committed
- [ ] Report written to `.agent/{{TASK_ID}}/scaffold-report.md`
