---
agent: scaffolder
description: Scaffold the once-per-repo FastAPI API layer per the approved ADR, with enforced layer ordering and golden files for per-feature router work.
---

# Scaffold: FastAPI API layer

You are scaffolding the HTTP API layer for this repository. This is a
**once-per-repo** task, not a per-feature task. The decision is already made
and approved — do not re-litigate it. Your job is to make the layer's position
in the dependency graph mechanically enforced, and to establish the golden
files that per-feature router work will imitate.

## Inputs

- **ADR**: `docs/adr/{{ADR_ID}}.md` — read this first. Binding items:
  - the layer ordering (`rule` field)
  - the test-scope decision: whether tests may import `_internal` modules
  - the rejected-alternatives section
- **Package**: `src/app/api/`
- **Composition root**: the module the ADR names as owning the app factory
  (referred to below as `app.main`; substitute the ADR's actual name).

## Hard constraints

- Scaffold only. **No business logic, no real endpoints beyond the health
  route, no speculative middleware.**
- The API layer is a **leaf**: nothing outside the composition root imports
  `app.api`, and `app.api` consumes domain packages **only through their
  public surfaces** — never `_internal`, never submodules not re-exported
  in a package `__init__.py`.
- Pydantic v2 idioms only: `model_config`, `model_dump()`,
  `ConfigDict`. No `class Config`, no `.dict()`, no v1 validators.
- Lifespan context manager for startup/shutdown. **Never `@app.on_event`.**
- Handlers are thin: parse/validate in, delegate to domain surface, shape
  response out. If a handler body exceeds ~10 lines, that is a design smell —
  stop and note it rather than proceeding.
- Do not touch `scripts/hooks/**` or `.github/hooks/**`.
- Do not generate or modify Copilot instruction files. That projection is a
  separate step and out of scope here.

## Steps

### 1. Structure

Create:

```
src/app/api/
    __init__.py              # docstring only: leaf layer, cites {{ADR_ID}},
                             # states "imported only by the composition root"
    app.py                   # create_app() factory: lifespan, router registration,
                             # exception handler registration (stubs)
    routers/
        __init__.py          # docstring + explicit list of registered routers
        health.py            # GOLDEN FILE — see below
    schemas/
        __init__.py          # docstring: "HTTP contract models. Domain packages
                             # must never import from here."
tests/api/
    conftest.py              # GOLDEN FILE — see below
    test_health.py           # GOLDEN FILE — see below
```

Update the composition root (`app.main`) to call `create_app()`. Do not put
FastAPI instantiation anywhere except `app.py`.

**Golden router — `routers/health.py`:** a real, working `/health` endpoint
demonstrating the canonical shape: `APIRouter` (no bare `app` decorators),
async handler, `response_model` with a v2 schema defined in `schemas/`,
dependency wiring via `Depends` against a domain package's *public* surface
(use a trivial stub dependency if no domain package exists yet — but prefer a
real one). Module docstring: "Golden file for router modules. New routers
imitate this shape. See {{ADR_ID}}."

**Golden test fixtures — `tests/api/conftest.py`:** app factory invocation,
`httpx.AsyncClient` with `ASGITransport`, and one worked example of
`app.dependency_overrides` substituting a domain dependency. Explicit comment:
overrides are the substitution mechanism for API tests —
`unittest.mock.patch` against module paths is prohibited in this directory.

**Golden test — `tests/api/test_health.py`:** exercises `/health` through the
client fixture, asserts status and response shape against the schema. No
imports from `app.api` internals except the schema under test; no patching.

### 2. Mechanical enforcement

Add to `pyproject.toml` under `[tool.importlinter]` (import-linter is already
a dev dependency from the subpackage scaffold; add it if not):

```toml
[[tool.importlinter.contracts]]
name = "api is the top layer"
type = "layers"
layers = [
    "app.api",
    # domain packages per the ADR's layer ordering, copied verbatim:
    {{LAYER_ORDERING}}
]
containers = ["app"]
```

This single contract enforces both directions: domain packages cannot import
`app.api` (including `app.api.schemas` — the schema-reuse leak), and layer
ordering among domain packages holds. Copy the ordering from the ADR
verbatim; do not infer layers the ADR does not name.

Additionally, one `forbidden` contract for the composition-root rule:

```toml
[[tool.importlinter.contracts]]
name = "only the composition root imports app.api"
type = "forbidden"
source_modules = ["app"]
forbidden_modules = ["app.api"]
ignore_imports = [
    "app.main -> app.api",
    "app.api -> app.api",
]
```

(Adjust `ignore_imports` to match import-linter's semantics for
self-imports if it flags intra-package imports; verify against the installed
version's behavior rather than assuming.)

`lint-imports` is already wired into pre-commit and CI from the subpackage
scaffold; confirm both still pass with the new contracts, and wire it if
this scaffold runs first.

### 3. Verify

Run, in order, and fix failures before proceeding:

1. `lint-imports` — passes clean.
2. **Deliberate violation, direction one:** temporary import of
   `app.api.schemas` from a domain package module. Confirm `lint-imports`
   fails. Remove. Record output.
3. **Deliberate violation, direction two:** temporary import of `app.api`
   from a domain package module. Confirm the forbidden contract fails.
   Remove. Record output.
4. Smoke: `pytest tests/api/` — golden test passes; app factory builds,
   routes mount.
5. `python -c "from app.main import *"` (or the ADR-named entry point) —
   composition root imports cleanly.
6. Existing test suite still passes.

A contract that has never been observed to fail is unverified. Both
violation outputs must appear in the report.

### 4. Report

Write to `.agent/{{TASK_ID}}/scaffold-report.md`:

- Tree of created files, with golden files marked
- Contracts added, with both observed failure outputs from the violation
  checks
- The test-scope decision as read from the ADR, restated in one sentence
  (confirms the ADR was actually consulted)
- Any deviation from this prompt, with reason
- Open items for per-feature router tasks

## Acceptance criteria

- [ ] `create_app()` factory exists; FastAPI instantiated nowhere else
- [ ] Lifespan handler present; zero `@app.on_event` anywhere in the diff
- [ ] Golden router at `routers/health.py` working end-to-end, all v2 idioms
- [ ] Golden conftest + test demonstrating `dependency_overrides`, zero
      `mock.patch` in `tests/api/`
- [ ] Layers contract with ADR-verbatim ordering; composition-root forbidden
      contract present
- [ ] Both deliberate violations performed and observed failing
- [ ] `pytest tests/api/` green; full suite green
- [ ] Zero business logic committed
- [ ] Report written to `.agent/{{TASK_ID}}/scaffold-report.md`
