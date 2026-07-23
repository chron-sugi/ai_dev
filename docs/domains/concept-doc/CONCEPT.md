---
summary: >
  What concept documents are, where they sit between ADRs and code, and how
  they are created, merged, and pruned — load before writing to any
  docs/domains/<domain>/CONCEPT.md.
scope:
  - "docs/domains/**"
---

# Concept Documents

A concept document is the canonical home for one unit of durable domain
knowledge: the mental model of how a part of the system actually works, plus
any contextual invariants and hard-won gotchas attached to it. Concept docs
form the middle tier of the knowledge system — ADRs above them hold decisions
and their rationale; the code below them holds everything derivable by
reading it. A concept doc exists only for knowledge that fits neither: too
explanatory for an ADR, too expensive to reconstruct from code.

Concept docs live in one place (ADR-0009/ADR-0017): every concept lives at
`docs/domains/<domain>/CONCEPT.md` — fixed filename, the folder is the
identifier — beside a sibling `CONTRACT.yaml` that defines the domain's
current executable contract (declared surface, endpoints, granted edges),
with optional ADR provenance. Cross-cutting knowledge that no single
existing domain owns gets its own domain folder rather than a home under an
unrelated domain; the schema and content bars are the same either way.

Concept docs are **pull artifacts**. Nothing projects them into agent context
automatically; agents discover them by scanning `docs/domains/` frontmatter
summaries or path-scoped loading via `scope`, and fetch the full
document only when relevant. This is the inverse of ADRs, which push their
`rule` field into generated instructions. The pull-only nature is why the
schema is minimal: two frontmatter fields, one required section, two
conditional ones, a 250-line cap.

Content enters through exactly one write path: distillation at task closeout
(`/concept-create`, typically invoked from `/task-closeout`). Merges update
the owning document in place — the file set stays bounded and improves over
time rather than growing and going stale. Every merge doubles as a
maintenance pass: existing entries contradicted by new task evidence are
proposed for removal. Deletion is the supersession mechanism; there is no
status field, because presence in a canonical location *means* active and
canonical.

Owns the knowledge tier's format and lifecycle; decision records belong to
`docs/adrs/`, contract state belongs to the domain's `CONTRACT.yaml`, agent
behavior rules belong to instruction files, and the distillation workflow
itself belongs to the closeout prompts.

## Invariants

- One concept = one domain's CONCEPT.md, and its identifier — the domain
  folder name — is fixed at creation. Two documents claiming overlapping
  territory breaks canonical-ness — the routing question must be resolved
  (merge or split) before content lands, not after.
- Placement is decided by ownership, not preference (ADR-0017): knowledge
  owned by one domain goes to that domain's CONCEPT.md; knowledge no single
  domain owns gets its own domain folder. Parking a concept under an
  unrelated domain is a routing error, not a second home.
- A domain's CONCEPT.md never absorbs contract state. Surface, endpoints,
  and dependency edges belong to the sibling CONTRACT.yaml, which is the
  primary executable specification; ADR provenance is optional (ADR-0017).
- Concept docs never project. If distilled content wants to become an
  always-loaded rule, it is an ADR or instruction-file entry wearing the
  wrong extension; the two-field frontmatter is deliberately too poor to
  express projection, so the routing question surfaces at write time.
- A concept is a unit of co-loading: one mental model, one noun-phrase name
  without "and", one contiguous scope, updated as a whole over time. A seam
  in any of these plus size pressure means split; interdependent halves that
  would constantly cite each other mean keep one file — cohesion beats size.
- The 250-line cap resolves by split or demotion, never by raising the cap.
  A concept that cannot be explained within budget, and has a visible seam,
  is two concepts.
- Sections are omitted when empty, never scaffolded. An empty header is an
  invitation for a distill agent to manufacture content to fill it.
