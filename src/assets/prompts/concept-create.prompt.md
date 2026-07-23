---
agent: agent
description: Create or update a canonical concept document in docs/domains/<domain>/CONCEPT.md
---

# Concept Document Creation / Merge

You are distilling durable domain knowledge into a canonical concept document.
Concept docs are **pull-loaded on demand** by agents mid-task: every line costs
context budget, and every element must age well. Your job is to produce the
minimum content that passes the bars below — most candidate content should be
rejected or routed elsewhere.

## Step 1 — Route before you write

Concept docs hold **domain knowledge only**. Route everything else first:

- **Decision + rationale** (chose X over Y, constraint accepted) → propose an
  ADR in `docs/adrs/` instead. Do not restate decision rationale in a concept doc.
- **Mechanically checkable rule** → propose a lint rule, hook, or formatter
  config instead. Enforcement outranks documentation.
- **Procedure / how-to** ("to add a provider, do X then Y") → propose an
  instruction-file or prompt-file addition instead.
- **Derivable from code in under a minute** → discard. Agents grep well.

Only knowledge that survives all four routes belongs here.

## What counts as ONE concept

A concept is a **unit of co-loading**: the knowledge an agent needs together
to work correctly in one territory. Tests — all four should hold:

- **One mental model**: explainable as a single system shape. If the mental
  model needs two disjoint explanations, it is two concepts.
- **One noun phrase, no "and"**: if the honest title is "X and Y", split.
- **One contiguous scope**: the `scope` glob covers one territory, not a
  union of unrelated paths.
- **Changes together**: future distills should plausibly touch the document
  as a whole, not always the same isolated region.

**Split** when size pressure coincides with a visible seam (an ownership
boundary listing two independent territories, a disjoint glob, or
region-only updates). **Do not split** interdependent knowledge — if the two
halves would constantly cite each other, cohesion beats size; keep one file.
**Merge** two existing documents that constantly cite each other: they are
one concept that was split wrong.

## Step 2 — Merge into canonical, never create a duplicate

- Check `docs/domains/` for a domain that already owns this topic. If a
  domain's `CONCEPT.md` already owns it, **update it in place**. One concept =
  one domain's `CONCEPT.md`, always.
- Create a new `docs/domains/<domain>/CONCEPT.md` only if no existing domain
  plausibly owns the topic. The domain folder name is the identifier: short,
  kebab-case, stable (e.g., `auth-session`). There is no `id` field — the
  folder name is the ID.
- If ownership is ambiguous between two existing domains, stop and ask the
  human rather than guessing.

## Step 3 — Apply the content bars

Use the template at `.velocai/templates/CONCEPT.md`. Rules:

- **Mental model is required.** 3–10 sentences: how the thing actually works,
  the shape a new agent would otherwise spend twenty minutes reconstructing.
  End it with a one-line ownership boundary ("Owns X; Y belongs to
  concept-Z"). If the mental model is thin enough to skip, the concept doc
  should not exist — say so and stop.
- **Invariants is conditional.** Admit an entry only if it is (a) a must-hold
  property, (b) NOT mechanically checkable, and (c) more than a bare ADR
  citation. Cite the ADR inline where one exists, but the entry must add
  context the ADR doesn't carry.
- **Gotchas is conditional.** Admit an entry only if it caused a real debug
  loop (e.g., carries a `recurring: true` flag in the task's debug report).
  Misleading entry points ("the real entry point is X, not the Y you'd
  expect") belong here.
- **Omit empty sections entirely.** Fixed order, optional presence. Never
  scaffold an empty header.

## Step 4 — Prune while you're here

When merging into an existing document, flag any existing Invariant or Gotcha
that the current task's evidence contradicts, and propose its removal.
Distillation is the maintenance trigger; do not skip this pass.

## Never include

- File paths, line numbers, or code snippets (stable names only, and only
  inside a gotcha that earns it)
- Decision rationale (ADR territory)
- Procedures or step-by-step instructions
- History or changelog narrative ("previously this used…") — git holds that
- Aspirations or roadmap ("eventually this should…") — agents implement
  everything they read as ground truth
- Manually maintained dates, status fields, or related-links lists — git and
  the body carry these

## Constraints

- Frontmatter is exactly two fields: `summary` (one sentence answering
  "should I load this?") and `scope` (glob(s) for the code territory).
  Nothing else.
- Hard cap: 250 lines. If a merge would exceed it, do not raise the cap —
  check the "one concept" tests above: propose a split if a seam exists, or
  propose demoting stale entries if not. Present the choice to the human.

## Step 5 — WAIT for approval

Present the proposed document (or diff, when merging) and any pruning /
split proposals. Do not commit until the human approves.
