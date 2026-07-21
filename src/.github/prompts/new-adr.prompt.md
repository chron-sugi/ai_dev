---
description: Author a new Architecture Decision Record in docs/adr/, conforming to the projection schema
---

# Write a New ADR

You are documenting a durable architectural decision. ADRs in `docs/adr/` are the single write path for durable decisions; instruction files, golden files, and lint config are generated from them. Your output must therefore be schema-valid and projection-ready.

## Step 1 — Qualify the decision

Before writing anything, confirm the decision meets at least one of these criteria. If none apply, stop and say so — the content belongs in scratch notes or a code comment, not an ADR.

- Expensive to reverse (datastore, auth model, API contract style, framework version)
- Likely to be re-litigated or undone by a future agent session
- Counterintuitive — it contradicts the statistically common solution an agent would default to

One decision per ADR. If the input contains two decisions, say so and propose splitting before proceeding.

## Step 2 — Gather what you're missing

Read `docs/adr/index.md` (or list `docs/adr/`) and check:

- Does an existing ADR already cover this? If yes, propose a superseding ADR instead and set the `supersedes` link.
- Does this decision conflict with any `accepted` ADR? If yes, stop and surface the conflict — do not write an ADR that contradicts a settled decision without an explicit supersession.

If the decision's rationale, the alternatives that were considered, or the affected file paths are not evident from the conversation or codebase, ask — do not invent rejected alternatives or guess scope globs.

## Step 3 — Write the ADR

Create `docs/adr/NNNN-<kebab-case-title>.md` where NNNN is the next available number. Use exactly this structure:

```markdown
---
id: ADR-NNNN
title: <short noun phrase, the decision not the problem>
status: proposed
date: <today, ISO 8601>
supersedes: <ADR-ID or omit>
scope: "<glob(s) covering the files this decision governs>"
rule: "<ONE atomic, imperative sentence — see constraints below>"
projection: <instructions | golden-file | lint | none>
---

## Context

<2–5 sentences. The forces at play: what problem existed, what constraints
applied. No solution language here.>

## Decision

<1–3 sentences. What was decided, stated as fact. Reference the golden file
or config location if projection is golden-file or lint.>

## Rejected Alternatives

<MANDATORY, never empty. One bullet per alternative:>
- **<Alternative>** — <one-line reason it was rejected>

## Consequences

<2–4 sentences. What becomes easier, what becomes harder, what must now be
maintained. Include migration or follow-up obligations if any.>
```

## Constraints on the `rule` field

The rule is the projectable unit — it gets compiled verbatim into instruction files. It must be:

- **One sentence, imperative mood** ("Use X for Y", "Never do Z")
- **Self-contained** — understandable without reading the ADR body
- **Checkable** — a reviewer or probe can determine pass/fail from it
- **Atomic** — no "and" joining two independent obligations; if you need "and", you likely need two ADRs

Bad: "We prefer to use the cn() helper where possible for class merging and also avoid string concatenation."
Good: "Merge Tailwind classes only via the cn() helper; never concatenate class strings."

## Constraints on `projection`

Choose the *lowest* layer that can express the rule — prose is the last resort:

- `lint` — statically checkable (banned imports, banned syntax, formatting)
- `golden-file` — a pattern best shown by exemplar; name the exemplar file in the Decision section
- `instructions` — only for rules that cannot be mechanized (the residue: "why" pointers, negative rules)
- `none` — decision is durable but needs no agent-facing rule

## Step 4 — Finish

1. Run `scripts/adr-lint` if present and fix any findings.
2. Do NOT edit `.github/copilot-instructions.md`, `.github/instructions/**`, or `docs/adr/index.md` — those are generated. State that the human should review the ADR, flip `status` to `accepted`, and run `scripts/project-adrs`.
3. Output a one-line summary: the ADR id, title, rule, and chosen projection layer.
