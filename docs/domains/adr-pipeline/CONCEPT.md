---
summary: >
  How the ADR projection pipeline works — ADRs as compilable source,
  domain-clustered instruction files as output, a CI drift guard as
  enforcement, and the justfile as the only command surface. Load before
  touching the justfile, pipeline scripts, CI workflows, or ADR frontmatter.
scope:
  - "justfile"
  - "scripts/**"
  - ".github/workflows/**"
  - "docs/adrs/**"
---

# ADR Projection Pipeline

The pipeline is a compiler with an enforcement loop. `docs/adrs/` is the
source code: each ADR carries a machine-readable frontmatter surface
(`status`, `domain`, `projection`, `scope`, `rule`) and a prose body that
never compiles — the body exists for humans and future sessions, the
frontmatter for the pipeline. Projection reads the accepted rule set,
clusters rules by their declared `domain`, and emits one instruction file
per domain plus sentinel-marked regions inside shared surfaces; agents read
only compiled output, never the source records. A drift guard re-runs
projection in CI and fails on any divergence from committed output, which
is what turns "don't hand-edit generated files" from a convention into an
unmergeable state. The pipeline has two interchangeable implementations —
Node and PowerShell — and exactly one command surface: justfile recipes,
invoked identically by developers, agents, and CI, so a CI failure is
always reproducible by running the same recipe locally. Everything else in
the repo is a consumer of the pipeline's output, never a participant in it.

Owns the compile-and-enforce machinery: lint, projection, drift check,
status transitions, and the recipes that run them. The decisions being
compiled belong to individual ADRs; per-domain documentation layout belongs
to concept-docs.

## Invariants

- Projection is a pure function of the ADR corpus: the same source must
  produce byte-identical output from either implementation (Node or
  PowerShell), locally or in CI (ADR-0006, ADR-0008). This is why recipes
  run PowerShell with `-NoProfile` — any environment sensitivity (profile
  state, locale, line endings, directory enumeration order) is a pipeline
  bug even when the output looks correct, because the drift guard compares
  bytes, not meaning.
- Rules flow one way: ADR → compiled surface. Projection never writes to
  `docs/adrs/`, and no compiled surface is ever an input to projection
  (ADR-0004, ADR-0005, ADR-0006 jointly define this direction). The one
  pipeline operation that does mutate an ADR is a status transition, and it
  touches only the frontmatter `status` field — never the rule or body.
