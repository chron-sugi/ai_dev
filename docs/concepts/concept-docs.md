---
summary: >
  What concept documents are, where they sit between ADRs and code, and how
  they are created, merged, and pruned — load before writing to docs/concepts/.
scope: "docs/concepts/**"
---

# Concept Documents

A concept document is the canonical home for one unit of durable domain
knowledge: the mental model of how a part of the system actually works, plus
any contextual invariants and hard-won gotchas attached to it. Concept docs
form the middle tier of the knowledge system — ADRs above them hold decisions
and their rationale; the code below them holds everything derivable by
reading it. A concept doc exists only for knowledge that fits neither: too
explanatory for an ADR, too expensive to reconstruct from code.

Concept docs are **pull artifacts**. Nothing projects them into agent context
automatically; agents discover them through `INDEX.md` (generated from
frontmatter summaries) or path-scoped loading via `scope`, and fetch the full
document only when relevant. This is the inverse of ADRs, which push their
`rule` field into generated instructions. The pull-only nature is why the
schema is minimal: two frontmatter fields, one required section, two
conditional ones, a 150-line cap.

Content enters through exactly one write path: distillation at task closeout
(`/concept-create`, typically invoked from `/task-closeout`). Merges update
the owning document in place — the file set stays bounded and improves over
time rather than growing and going stale. Every merge doubles as a
maintenance pass: existing entries contradicted by new task evidence are
proposed for removal. Deletion is the supersession mechanism; there is no
status field, because presence in `docs/concepts/` *means* active and
canonical.

Owns the knowledge tier's format and lifecycle; decision records belong to
`docs/adr/`, agent behavior rules belong to instruction files, and the
distillation workflow itself belongs to the closeout prompts.

## Invariants

- One concept = one file, and the filename is the identifier. Two documents
  claiming overlapping territory breaks canonical-ness — the routing question
  must be resolved (merge or split) before content lands, not after.
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
