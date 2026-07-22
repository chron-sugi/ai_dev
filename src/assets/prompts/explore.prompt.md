---
agent: explorer
description: Produce a workspace-shaped research note in .velocai/research/<task-slug>.md.
tools:
  - search/codebase
  - search/usages
  - search/fileSearch
  - search/textSearch
  - search/listDirectory
  - read/readFile
  - web/fetch
  - edit/editFiles
---

# /research

Produce a research note for **[[ project_title ]]**, written to `.velocai/research/<task-slug>.md`. The note is the **grounding** that the planner uses to draft a plan, and it survives session boundaries. Per-task filename means multiple researchers can work in parallel without collision (same property `/rpi-plan` has).

This prompt activates the **researcher** agent. The researcher is read-only on code and writes only to `.velocai/research/`.

## Inputs

- `${input:task|}` — kebab-case slug. Becomes the filename. **Required.** Example: `add-user-deletion`, `migrate-billing-to-stripe`. If omitted, propose one based on the user's description and confirm before writing.
- `${input:depth|standard|quick,standard,deep}` — how thorough to be. `quick` = ≤30 minutes of code reading. `standard` = include prior-art search and code citations. `deep` = also fetch external references when relevant. Default `standard`.

## Procedure

### Phase 1: Discover prior art

Before writing:

1. Check whether a research note already exists at `.velocai/research/<task>.md` or with a related slug. If so, do **not** overwrite — propose extending, revising, or writing a `<task>-v2.md` instead.
2. Search `docs/concepts/` for any concept doc that names the entity/workflow this task touches. Cite specifics.
3. Search `docs/adrs/` for ADRs that constrain the option space. Cite specifics.
4. Scan recent `.velocai/plans/` for prior work on the same slug or adjacent slugs. Avoid re-deriving.

### Phase 2: Map the territory

Build the fact base, **not** a solution. The researcher's job is to lay out what's true, not to choose.

1. **Problem statement** — restate the user's question in domain terms. If the user said "add user deletion," translate: "Users currently exist in PENDING/ACTIVE/SUSPENDED. We need a fourth state DELETED with the lifecycle described in `docs/concepts/example.md` and a 90-day retention window."
2. **Affected surface** — list every file or module that would change. Include line ranges. The planner uses this to size the work.
3. **Prior art** — point at any similar pattern already in the codebase. Example: "We soft-delete `Organizations` with a `deleted_at` timestamp; see `app/models/organization.py:42`."
4. **Constraints** — list every ADR, concept invariant, and convention that constrains the design space.
5. **Options** — enumerate 2–4 viable approaches. For each: one paragraph + the *strongest case for it* + the *single biggest concern*.
6. **Recommendation (optional, soft)** — if one option is clearly best, say so with reasoning. Otherwise stop at the options list and let the planner choose.
7. **Open questions** — anything you can't resolve from code/docs alone. Flag for human input.

### Phase 2.5: ADR trigger check

Before writing the note, evaluate whether the options enumerated in Phase 2 surface an architectural decision that should be settled by an ADR before any plan is written.

**Trigger an ADR (stop and recommend `/write-adr`) if any of these hold:**

- Two or more options would cross module boundaries differently
- Two or more options would expose different public contracts (API shape, schema shape, event shape)
- Two or more options would change which dependency is load-bearing
- Two or more options would set precedent for future work on similar problems
- No existing accepted ADR governs the option space, and the options are not interchangeable

**Do NOT trigger an ADR if:**

- The options differ only in implementation detail (one uses a helper function, another inlines)
- All options fit within an existing accepted ADR's frame
- The choice is reversible at near-zero cost (a feature flag, a config value)
- The choice is purely stylistic (naming, internal organization)

**If triggered:** Skip the full Phase 3 note. Instead, write a *stub* research note with §Affected surface and §Constraints filled (the architect needs these), §Options listed as one-line headers only (no recommendation — the ADR will reframe the option space), and `## Open questions` containing exactly: `Architectural decision required — recommend /write-adr decision="<one-sentence question>" before /rpi-plan.` Set the front-matter `loop:` field to `loop: rpi (blocked: adr)` so downstream tooling sees the research is paused pending an ADR.

**If not triggered:** Proceed to Phase 3 as normal.

The decision rule that separates ADR-worthy from tactical: *would a future developer reading the resulting code ask "why did we do it this way?"* If yes, ADR. If they would read the code and understand, no ADR.

### Phase 3: Write the note

Use this exact shape. Front-matter is machine-readable; sections are human-readable.

After writing `.velocai/research/<slug>.md`, also write `<slug>` (one line, no trailing newline) to `.velocai/.current-task` using `edit/editFiles`. This allows `/rpi-plan` and subsequent agents to find the active task without the user retyping the slug.

```markdown
---
task: <slug>                          # MUST match filename
title: <Human-readable title>
loop: rpi                              # always rpi for research
depth: quick | standard | deep
created: YYYY-MM-DD
agent-id: <session or instance ID>
concepts:
  - docs/concepts/<noun>.md
adrs:
  - docs/adrs/<NNNN>-<slug>.md
related-plans:                         # any .velocai/plans/ that touched adjacent work
  - .velocai/plans/<slug>.md
---

# Research: <title>

## Problem

One paragraph restating the question in domain terms. Cite the user's request.

## Affected surface

| Path | What it does | Why this task touches it |
|---|---|---|
| `apps/api/src/app/<X>.py:<lines>` | <role> | <reason> |
| ... | ... | ... |

## Prior art

- Similar pattern: `<path:line>` — <short description>
- ADR-NNNN: <short description>
- Concept: `docs/concepts/<noun>.md`

## Constraints

- ADR-NNNN says <X>. Implication: we can't <Y>.
- `docs/conventions.md#section` says <X>. Implication: <Y>.
- Concept invariant: <X>. Implication: <Y>.

## Options

### Option A: <name>

<one paragraph: the approach>

**Strongest case:** <one sentence>
**Biggest concern:** <one sentence>

### Option B: <name>

<same shape>

## Recommendation

(Soft — the planner makes the final call.)

<one paragraph if there's a clear winner. Otherwise: "All three options are viable; planner to choose based on <criterion>.">

## Open questions

- <question requiring human input>
- <question requiring human input>

## Hand-off

Next: `/rpi-plan task=<same-slug> from-research=.velocai/research/<slug>.md`.
```

### Phase 4: Present and stop

Show the proposed research note. Surface unresolved open questions clearly. Tell the user:

```
Research note drafted: .velocai/research/<slug>.md
Open questions for human input: <count>

Next: resolve open questions if any, then invoke /rpi-plan (slug saved to .velocai/.current-task).
```

## What this prompt does NOT do

- **Propose a plan.** That's the planner's job. The research note enumerates options; it doesn't sequence edits.
- **Edit code.** Researcher may write only the research artifact under `.velocai/research/`.
- **Make architectural adrs.** If Phase 2.5 triggers, write a stub note recommending `/write-adr` and stop. The architect makes the decision; you don't pre-commit to options.
- **Skip prior art.** If the same problem has been researched before, you must find that note and either extend it or write a clearly-marked `-v2.md`.

## Multi-agent safety

Different tasks = different research note files. Multiple researchers can run in parallel on different slugs without contention. Same-slug parallel work converges on the existing note (read first, then propose v2 if needed).
