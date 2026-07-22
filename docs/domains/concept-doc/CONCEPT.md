---
summary: >
  What concept documents are, where they sit between ADRs and code, and how
  they are created, merged, and pruned — load before writing to docs/concepts/
  or any docs/domains/<domain>/CONCEPT.md.
scope:
  - "docs/concepts/**"
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

Concept docs live in two places, split by scope (ADR-0009). Domain-scoped
knowledge lives at `docs/domains/<domain>/CONCEPT.md` — fixed filename, the
folder is the identifier — beside a sibling `CONTRACT.md` that registers the
domain's current contract (declared surface, endpoints, granted edges), each
entry linking its granting ADR. Cross-cutting knowledge that no single domain
owns lives as `docs/concepts/<name>.md`, where the filename is the
identifier. The schema and content bars are identical in both locations;
only placement and naming differ.

Concept docs are **pull artifacts**. Nothing projects them into agent context
automatically; agents discover them through `INDEX.md` (generated from
frontmatter summaries) or path-scoped loading via `scope`, and fetch the full
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
`docs/adrs/`, contract state belongs to the domain's `CONTRACT.md`, agent
behavior rules belong to instruction files, and the distillation workflow
itself belongs to the closeout prompts.

## Invariants

- One concept = one file, and its identifier is fixed at creation: the
  folder name for a domain CONCEPT.md, the filename for a cross-cutting
  concept. Two documents claiming overlapping territory breaks
  canonical-ness — the routing question must be resolved (merge or split)
  before content lands, not after.
- Placement is decided by scope, not preference (ADR-0009): knowledge owned
  by one domain goes to that domain's CONCEPT.md; `docs/concepts/` admits
  only knowledge no single domain owns. A domain-shaped file appearing in
  `docs/concepts/` is a routing error, not a second home.
- A domain's CONCEPT.md never absorbs contract state. Surface, endpoints,
  and dependency edges belong to the sibling CONTRACT.md, which is a
  registry of ADR-granted facts — every entry cites its granting ADR, and
  the contract file is never the write path for a new grant (ADR-0009).
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
