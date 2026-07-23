---
agent: scaffolder
description: Scaffold a Python domain package from the backend block of an approved CONTRACT.yaml.
---

# Domain prompt: Python domain package (rung layout)

Domain payload for the scaffolder agent. Protocol (execution phases,
omission rule, verification discipline, report format, stop conditions) is
defined in the agent definition — this prompt supplies only what is
specific to Python domain packages.

## Binding contract declarations

- `rules` — the package charter and constraints
- `backend.package` and `backend.public_api` — package name and exact exports
- Root `types` — models, enums (including StrEnum), errors, and aliases;
  backend vocabulary is generated in `models.py`/`errors.py`
- Root `invariants` — truths the generated backend must preserve
- Optional backend blocks — presence activates their corresponding modules
- `http.backend.endpoint_ids` — package-provided root `http.endpoints`
- `dependencies.backend` — granted cross-package edges; absence means none
- `rejected_alternatives` and optional `adr_provenance`

## Assumed-present repo state

`app/api/router.py` (assembly), `app/api/dependencies.py` +
`app/api/errors.py` (shared HTTP kernel), `app/db/engine.py`, shared
`metadata`, `AppBaseModel`, import-linter wired into pre-commit and CI.

## Blast radius

Target: `src/app/{{PACKAGE}}/` and `tests/{{PACKAGE}}/`.
Permitted external one-liners:

- `app/api/router.py`: one `include_router` line (iff `api/` is created)
- Composition-root lifespan: one `{{PACKAGE}}.tables` registration import
  (iff `tables.py` is created)
- `pyproject.toml`: `[tool.importlinter]` blocks per this prompt

## The rung model

Files are organized by **role in the dependency order** — not by syntax,
not by subdomain. Each rung imports only strictly lower rungs; never
sideways, never up. Two ports:

- **Port 1 — Python surface**: `__init__.py` re-exports; the only legal
  import path for other domain packages.
- **Port 2 — HTTP adapter**: `{{PACKAGE}}/api/`, consumed only by
  `app.api.router`.

```
src/app/{{PACKAGE}}/
    __init__.py     # port 1: re-exports only
    errors.py       # rung 0 — always
    models.py       # rung 1 — always
    config.py       # rung 0 — CONDITIONAL
    tables.py       # rung 2 — conditional on persistence
    store.py        # rung 3 — conditional on persistence
    service.py      # rung 4 — CONDITIONAL
    jobs.py         # rung 5 — CONDITIONAL
    api/            # rung 5 — CONDITIONAL
        __init__.py     # exports `router` only
        router.py
        schemas.py
        dependencies.py # CONDITIONAL within the adapter
    testing.py      # side module — CONDITIONAL
```

**Service authority (binding).** When `service.py` exists, it is the sole
gateway to `store.py` for everything above it — both ports, both rung-5
adapters:

- Port 1 re-exports service functions, never store functions.
- `api/router.py` and `jobs.py` call service, never store (contract-enforced).
- Housekeeping implementations (recovery, pruning, cleanup) live in
  `store.py`; service exposes them as one-line pass-throughs; `jobs.py`
  only decides *when* to invoke. Pass-through service functions are
  expected, not a smell — they stay one line until an invariant arrives.
  Do not move housekeeping logic up into service to "justify" the
  pass-through.

When `service.py` is absent, port 1 and the adapters call store directly
and this rule is dormant. No per-function exceptions in either state.

## Conditional criteria

Resolve each only from optional block presence under `backend` and `http.backend`.

| Module | Create when… | Otherwise |
|---|---|---|
| `tables.py` + `store.py` | `backend.persistence` is present. Always create together. | Omit both; pure-logic package. |
| `service.py` | `backend.service` is present; create exactly its operations. | Omit. Port 1 may re-export declared store-backed operations directly. |
| `config.py` | `backend.config` is present; create exactly its tunables. | Omit. Never use it for constants. |
| `api/` | `http.backend` is present; implement exactly its selected root endpoints. | Omit entirely. No empty adapter "for later". |
| `api/dependencies.py` | `http.backend.dependency_providers` is non-empty. | Omit. Kernel-only providers import `app.api.dependencies` directly. |
| `jobs.py` | `backend.jobs` is present; create exactly its entries. | Omit. Never park scheduled work in `api/` or `store.py`. |
| `testing.py` | `backend.testing` is present; create exactly its exports. | Omit. |

**Never create**: `utils.py`, `helpers.py`, `constants.py`, `enums.py`,
`types.py`, root-level `schemas.py` ("schema" is reserved for the HTTP
adapter), `repositories.py`, any `_internal/` directory.

## Domain constraints

- Rung order is absolute. `errors.py`, `models.py`, `config.py` import
  nothing package-internal.
- Port 1 returns root `types` projected into `models.py`. StrEnum, Enum, and
  IntEnum declarations live in `models.py`, never a separate `enums.py`.
  SQLAlchemy `Row` objects never cross
  `__init__.py`.
- Intra-package imports are direct and relative (`from ..service import x`).
  Never `from app.{{PACKAGE}} import x` inside the package: port 1 is an
  external boundary, not an internal service locator.
- `config.py`: `pydantic_settings.BaseSettings` subclass,
  `env_prefix = "{{PACKAGE_UPPER}}_"`. No global settings imports.
- `api/schemas.py`: all models inherit `AppBaseModel`; Pydantic v2 idioms
  only; camelCase-aliased models exist ONLY under `api/`. Single flat file.
  Growth rule (record, don't apply): split by resource
  (`invoice_schemas.py`) — never by request/response direction (shape split).
- `api/router.py`: `APIRouter`, async handlers, `response_model` on every
  route, handlers thin (parse → delegate → shape; ~10 lines is a smell —
  stop and note it). Delegates per service authority. May import this
  package's rungs (relative) and the shared HTTP kernel
  (`app.api.dependencies`, `app.api.errors`); never `app.api.router`,
  never another package's rungs.
- Cross-package imports: only `dependencies.backend`, only via port 1, with a
  contract rule/provenance citation.

## Golden files

If `api/` is created: ONE working route end-to-end — the first endpoint ID in
`http.backend.endpoint_ids`, resolved through root `http.endpoints`. A stub dependency is acceptable where the service function is
`NotImplementedError`, but the request/response schema round-trip must be
real. This route is the imitation target for all future routes in the
package.

## Contracts

Add to `[tool.importlinter]`:

```toml
# Port privacy: submodules are private; ports are the only entries
[[tool.importlinter.contracts]]
name = "{{PACKAGE}} internals are private"
type = "forbidden"
source_modules = ["app"]
forbidden_modules = ["app.{{PACKAGE}}.*"]
ignore_imports = [
    "app.{{PACKAGE}} -> app.{{PACKAGE}}.*",
    "app.{{PACKAGE}}.* -> app.{{PACKAGE}}.*",
    "app.api.router -> app.{{PACKAGE}}.api",      # only if api/ exists
    "app.main -> app.{{PACKAGE}}.tables",         # only if tables.py exists
]

# Rung order — include only the rungs that exist
[[tool.importlinter.contracts]]
name = "{{PACKAGE}} rung order"
type = "layers"
layers = [
    "app.{{PACKAGE}}.api | app.{{PACKAGE}}.jobs",
    "app.{{PACKAGE}}.service",
    "app.{{PACKAGE}}.store",
    "app.{{PACKAGE}}.tables",
    "app.{{PACKAGE}}.models | app.{{PACKAGE}}.errors | app.{{PACKAGE}}.config",
]
containers = []
```

**Iff `service.py` exists** — the `layers` contract permits skipping rungs;
this closes that gap for rung 5:

```toml
[[tool.importlinter.contracts]]
name = "{{PACKAGE}} rung 5 goes through service"
type = "forbidden"
source_modules = ["app.{{PACKAGE}}.api", "app.{{PACKAGE}}.jobs"]
forbidden_modules = ["app.{{PACKAGE}}.store", "app.{{PACKAGE}}.tables"]
```

(Include only modules that exist. If a later task adds `service.py` to a
package scaffolded without it, adding this contract is part of that task.)

Amendments to shared contracts:

- **Independence**: add `app.{{PACKAGE}}` to the repo-wide independent-
  modules list. `dependencies.backend` become the contract's declared
  exceptions, commented with a contract rule/provenance citation. No per-edge
  forbidden contracts.
- **Testing** (iff `testing.py`): extend the repo-wide testing-module
  contract — `app.* -> app.{{PACKAGE}}.testing` forbidden. Test trees are
  outside contract scope and unaffected.

## Tests to scaffold

Mirror placement: `tests/{{PACKAGE}}/`.

- Surface test: `import app.{{PACKAGE}}` succeeds; `__all__` matches
  `backend.public_api` exactly.
- Iff `api/`: golden test for the golden route via the shared conftest
  pattern (`httpx.AsyncClient` + `ASGITransport`, `dependency_overrides`).
  Zero `mock.patch` anywhere under `tests/{{PACKAGE}}/`.
- Iff `testing.py`: drift alarm — one test asserting the fake satisfies the
  port-1 surface (same exported names, compatible signatures).

## Deliberate-violation checks

One per contract class; capture each failure output per protocol.

1. **Privacy**: import `app.{{PACKAGE}}.store` (or `models` if no store)
   from another package.
2. **Rung order**: an upward import (`store` → `service`, or `models` →
   `store` in a minimal package).
3. **Independence**: import another domain package's root (one with no
   granted edge) from this package.
4. Iff `api/` — **adapter reach-around**: import
   `app.{{PACKAGE}}.api.schemas` from `service.py` or `store.py` (rung
   contract catches it).
5. Iff `service.py` — **service bypass**: import `..store` from
   `api/router.py` (or `jobs.py` if no api).

## Positive checks

- `lint-imports` clean
- `pytest tests/{{PACKAGE}}/` green; full suite green
- Iff `api/`: app factory builds, route mounts, `/openapi.json` includes it

## Domain acceptance criteria

- [ ] Port 1 exports match `backend.public_api` exactly; if `service.py`
      exists, port 1 re-exports service functions only
- [ ] No never-create modules present
- [ ] All intra-package imports relative; zero `from app.{{PACKAGE}} import`
      inside the package
- [ ] Privacy, rung-order, and independence contracts in place; service-
      bypass contract iff `service.py`; testing contract iff `testing.py`
- [ ] Iff `api/`: golden route working end-to-end, registered in assembly,
      golden test green, zero `mock.patch`
- [ ] Iff `tables.py`: registration import at composition root only
