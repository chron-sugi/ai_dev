---
agent: scaffolder
description: Domain payload for the scaffolder agent — scaffold a Feature-Sliced Design 2.1 frontend slice from an approved ADR.
---
# Domain prompt: FSD frontend slice

Domain payload for the scaffolder agent. Protocol (execution phases,
omission rule, verification discipline, report format, stop conditions) is
defined in the agent definition — this prompt supplies only what is
specific to Feature-Sliced Design 2.1 frontend slices.

## Parameters

- `{{SLICE}}` — slice name (matches `{{BACKEND_PACKAGE}}` when paired)
- `{{LAYER}}` — FSD layer the ADR places this slice on
  (`pages` | `widgets` | `features` | `entities`)
- `{{BACKEND_PACKAGE}}` — paired backend domain package; empty for
  frontend-only slices. Non-empty ⇒ the seam section activates.

## Binding ADR sections

- `rule` field — the slice charter
- Layer placement and the reason it isn't `pages` (pages-first is the
  default; any lower layer requires the ADR to name ≥2 consumers)
- Endpoints consumed, if any (must match `{{BACKEND_PACKAGE}}`'s declared
  endpoints)
- Granted @x cross-import edges (default: none)
- Rejected alternatives

## Assumed-present repo state

FSD foundation from the repo-level frontend scaffold; stop and report if
missing:

- `src/app/`, `src/pages/`, `src/shared/` layers
- `src/shared/ui/` seeded with the design system (golden `Button.tsx`,
  `cn()` helper, Tailwind v4 CSS-first entry)
- Steiger (`@feature-sliced/steiger-plugin`) wired into pre-commit and CI
- Typegen pipeline: committed OpenAPI spec exported from the backend,
  generated types in `src/shared/api/`, regen-diff check in CI
- ESLint/Prettier Tailwind configs per the Tailwind v4 kit

If `{{BACKEND_PACKAGE}}` is non-empty: the paired backend adapter exists
and its routes appear in the committed OpenAPI spec. Absent ⇒ stop
(dispatch is mis-sequenced).

## Blast radius

Target: `src/{{LAYER}}/{{SLICE}}/` and its test location per the repo's
test convention. Permitted external one-liners:

- If `{{LAYER}}` is `pages`: route registration, matching the repo's
  existing routing pattern — one entry, nothing more.

No edits to `src/shared/**`, other slices, Steiger config, or the typegen
pipeline. If a needed shared primitive is missing, that is a stop
condition, not a license to add it.

## Structural model (FSD 2.1)

The slice is a folder on its layer with a public API and internal
segments. FSD's import rule is the repo-level rung order: a slice imports
only layers strictly below; slices on the same layer are independent
except ADR-granted @x edges.

```
src/{{LAYER}}/{{SLICE}}/
    index.ts        # public API: re-exports only — the slice's port
    ui/             # segment — CONDITIONAL
    api/            # segment — CONDITIONAL
    model/          # segment — CONDITIONAL
    lib/            # segment — CONDITIONAL, fenced
```

**Pages-first (binding).** This prompt scaffolds the one slice the ADR
declares, on the layer the ADR declares. It never creates additional
slices on `widgets`/`features`/`entities` speculatively — extraction to
lower layers happens mid-life, criterion-fired (a second consumer observed
and named), as its own dispatch.

**API-segment authority (binding, seam analog of backend service
authority).** All server communication goes through the slice's `api/`
segment, which wraps the generated client/types from `shared/api`.
Components in `ui/` never call `fetch` directly and never import from
`shared/api` directly — they import their own slice's `api/` functions.
Keeps every endpoint consumption greppable per slice and gives mocking a
single seam in tests.

## Conditional criteria

| Segment | Create when… | Otherwise |
|---|---|---|
| `ui/` | The slice renders anything. (Nearly always for `pages`/`widgets`.) | Omit — logic-only slice. |
| `api/` | `{{BACKEND_PACKAGE}}` is non-empty, or the ADR names endpoints consumed. | Omit. Never create an empty api segment "for later". |
| `model/` | The ADR names state that outlives a single component (stores, cross-component state, non-trivial client logic). Component-local state stays in the component. | Omit. |
| `lib/` | A helper is needed by ≥2 modules *within this slice* and is slice-specific. | Omit. One consumer ⇒ helper stays local to its module. Repo-wide utility ⇒ stop and report (shared/ is out of blast radius). |

**Never create**: top-level or slice-level `components/`, `hooks/`,
`utils/`, `helpers/`, `types.ts` (types live in `model/`, or come
generated via `shared/api`), `styles/` folders (Tailwind v4 kit rules
apply), hand-written types duplicating OpenAPI schemas, `config/` segment
(runtime config is foundation-owned), any segment name not in the table.

## Domain constraints

- `index.ts` re-exports only what other layers legitimately consume —
  minimal surface, not a barrel of everything. Intra-slice imports are
  relative and never go through `index.ts`.
- `ui/` components use `shared/ui` primitives and `cn()`; Tailwind v4 kit
  rules apply in full (no v3 patterns).
- `api/` functions type their inputs/outputs exclusively with generated
  types imported from `shared/api`. Zero hand-declared request/response
  shapes.
- `model/` may import the slice's `api/` and `shared`; never `ui/`.
  Segment order within the slice: `ui → model → api → (shared)`, `lib`
  importable by all.
- @x cross-imports: only ADR-granted edges, using FSD's @x notation,
  commented with the ADR id at the import site.
- Framework specifics (router, state library, test runner) follow the
  repo's existing patterns — match, don't introduce.

## Golden files

- One `ui/` component demonstrating the canonical shape: `shared/ui`
  primitives, `cn()`, props typed from `model/` or generated types —
  the imitation target for the slice's future components.
- If `api/` exists: one function wrapping the generated client for the
  simplest ADR-declared endpoint — real request/response typing
  round-trip, `NotImplementedError`-equivalent (`throw new Error("not
  implemented")`) is NOT acceptable here; the wiring must work against
  the generated types (compile-time proof is the point).
- If `{{LAYER}}` is `pages`: the page component composes the golden ui
  component and mounts on its registered route.

## The seam (active iff `{{BACKEND_PACKAGE}}` non-empty)

The contract is owned by the ADR; the committed OpenAPI spec is its
compiled form; generated types in `shared/api` are its TypeScript
projection. This slice consumes the projection — it never re-declares it.

- Every request/response type in `api/` traces to a generated type.
- If a declared endpoint is missing from the spec: stop and report
  (backend defect or mis-sequenced dispatch — not yours to fix).
- Do not run or modify the typegen pipeline; consume its committed
  output.

## Deliberate-violation checks

One per enforcement class; capture each failure output per protocol.

1. **Public-API sidestep** (Steiger `no-public-api-sidestep`): temporary
   import of another slice's internal module, bypassing its `index.ts`.
2. **Layer order** (Steiger `forbidden-imports`): temporary import from a
   higher layer (e.g., this slice importing from `pages` if on a lower
   layer; if on `pages`, import another page).
3. **Slice independence** (Steiger `forbidden-imports`): temporary
   cross-import of a same-layer slice without @x.
4. Iff `api/` — **typegen drift**: temporary edit to a generated file in
   `shared/api` → run the regen-diff check → observe failure → revert.
   (Read-only verification of foundation machinery; reverting restores
   the committed state, so this does not violate blast radius.)

Note: the api-segment-authority rule (no raw `fetch` in `ui/`) is
foundation-enforced via ESLint restricted-syntax; if the foundation rule
is absent, record that as a deviation — do not add lint rules from this
dispatch.

## Positive checks

- Steiger clean; ESLint/Prettier clean; TypeScript compiles
- Regen-diff check clean (spec and generated types agree)
- Test suite green, including scaffolded tests:
  - surface test: `index.ts` exports exactly the ADR-declared names
  - iff `api/`: one test exercising the golden api function against a
    mocked transport per the repo's mocking pattern — never by
    hand-mocking generated types
- Iff `{{LAYER}}` is `pages`: app builds and the route renders

## Domain acceptance criteria

- [ ] Slice exists on the ADR-declared layer; no other slices created
- [ ] Segment set matches the decision table; omissions recorded
- [ ] No never-create items; zero hand-written schema-duplicate types
- [ ] `index.ts` surface matches ADR-declared names; surface test passes
- [ ] Golden ui component uses shared/ui + cn(); golden api function
      compiles against generated types
- [ ] All ui server communication routed through the slice's `api/`
- [ ] @x edges only where ADR-granted, commented with ADR id
- [ ] All violation checks performed and observed failing
- [ ] Route registered iff `pages` layer, one line only