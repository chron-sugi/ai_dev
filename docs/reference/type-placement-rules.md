# Type Placement Rules

Deterministic placement procedure for enums, models, schemas, and shared types in a domain-package (package-by-feature) layout. Evaluate rules top-down; first match wins. No judgment calls — if a case requires judgment, the rules are incomplete and must be amended via ADR, not improvised.

## Layout contract

```
<app_name>/          # the actual application package name, not a generic "app"
  shared/            # shared vocabulary only — no behavior, no I/O
  <domain>/        # one package per business domain
    enums.py       # domain-owned enums (bottom module: imports nothing from the domain)
    models.py      # persistence / domain models
    schemas.py     # API request/response shapes (transport layer)
    services.py    # behavior
    routes.py      # HTTP endpoints
```

**Root package naming**: the top-level package is named after the application (e.g., `invoicer/`, `fieldkit/`), never a generic `app/`, `src/`, or `backend/`. Generic names carry zero routing information for imports, logs, and tracebacks, and collide when multiple services share a monorepo or an agent works across repos.

## Placement decision procedure

Evaluate in order. Stop at first match.

1. **Single consumer** — If the type is imported by exactly one domain package, it lives in that package. Never place a type in `shared/` "because it might be shared later."
2. **Multiple domain consumers** — If the type is imported by two or more domain packages, it lives in `shared/`. No exceptions, including "principled" one-way imports of another domain's public contract. (Rejected alternative — see ADR below.)
3. **Framework/base machinery** — Base classes, mixins, shared enums, type aliases, and value objects used across domains live in `shared/`, split by concept (`shared/predicates.py`, `shared/identifiers.py`), never a single `shared/types.py` junk drawer.
4. **Transport vs persistence** — Pydantic request/response shapes go in the domain's `schemas.py`; ORM/domain models go in the domain's `models.py`. A type used by both layers is defined once in `models.py` and referenced by `schemas.py`, not duplicated.
5. **Domain-owned enums** — Enums used by exactly one domain are defined in that domain's `enums.py`, never inline in `models.py` or `schemas.py`. `enums.py` is the bottom module of the domain: it imports nothing from the domain, so both `models.py` and `schemas.py` may import from it freely. An enum imported by 2+ domains hoists to `shared/` per rule 2 — conceptual ownership does NOT keep it in the owning domain. When hoisting, preserve ownership as documentation: name the module for the concept (`shared/predicates.py`) and record the owning domain in the module docstring.

## The shared/ contract

`shared/` contains **vocabulary, not behavior**:

- **Allowed**: enums, `NewType`/type aliases, frozen value objects, abstract base classes, protocol definitions, exception types.
- **Forbidden**: functions with business logic, I/O, service classes, anything importing from a domain package. `shared/` imports only stdlib and third-party libraries.

If a candidate for `shared/` contains logic, split it: the vocabulary goes to `shared/`, the logic stays in (or moves to) the domain that owns the behavior.

## Import direction rules

- Domain packages MAY import from `shared/`.
- Domain packages MUST NOT import from other domain packages — not even one-directional imports of public contracts.
- `shared/` MUST NOT import from any domain package.
- Cycle resolution is always **hoist to shared/**, never "make one direction an exception."

## Refactor procedure (moving an existing type)

1. Grep all import sites of the type.
2. Count distinct domain packages among importers.
3. Apply the decision procedure above to determine the target module.
4. Move the type; update imports; do NOT leave a re-export shim in the old location (shims hide the true dependency graph from both linters and agents).
5. Run the import contract check (below) before committing.

## Mechanical enforcement

Prose is the weakest layer. Back these rules with `import-linter`:

```ini
# .importlinter
[importlinter]
root_package = <app_name>

[importlinter:contract:shared-independence]
name = shared imports no domains
type = forbidden
source_modules = <app_name>.shared
forbidden_modules =
    <app_name>.billing
    <app_name>.auth
    <app_name>.filters
    <app_name>.field_definitions

[importlinter:contract:domain-independence]
name = domains do not import each other
type = independence
modules =
    <app_name>.billing
    <app_name>.auth
    <app_name>.filters
    <app_name>.field_definitions
```

Run `lint-imports` in CI and as a pre-push hook. When a new domain package is added, adding it to both contracts is part of the same commit — enforce via a checklist item in the domain-scaffold instruction file.

## ADR rule fields (candidates)

- `rule: types imported by 2+ domain packages live in shared/; shared/ contains vocabulary, not behavior`
- `rule: domain packages never import from other domain packages; cycles resolve by hoisting to shared/`
- `rule: transport shapes live in <domain>/schemas.py; persistence models in <domain>/models.py; shared definitions live once in models.py`

**Rejected alternatives** (record in the ADR so agents don't re-litigate):

- *Permitting one-way imports of another domain's public contract* — rejected: requires per-case judgment about "who defines the concept," which agents apply inconsistently; the strict rule is mechanically checkable and the cost (slightly larger `shared/`) is low.
- *Single shared `shared/types.py`* — rejected: junk-drawer module forces agents to read it on every task; concept-scoped modules keep reads targeted.
- *Enums defined inline in `models.py`* — rejected: mixes vocabulary with model machinery; a dedicated bottom module (`enums.py`) lets both `models.py` and `schemas.py` import enums without layering questions and keeps vocabulary diffs isolated from model diffs.
- *Domain-owned "published" enums imported by other domains (DDD published-language)* — rejected: legitimate in DDD but reintroduces per-import judgment ("blessed contract or illegal sideways reach?") and forces per-module allowlists in the domain-independence contract; the structural rule (2+ importers → `shared/`) is flatly enforceable, and conceptual ownership is preserved via module naming and docstrings in `shared/`.
- *Re-export shims after moves* — rejected: hides true dependency direction from import-linter and inflates the surface agents must read.