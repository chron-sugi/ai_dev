---
agent: explorer
description: Produce a workspace-shaped exploration note in .velocai/tasks/<task-id>/exploration.md
---

# /explore

Produce an exploration note, written to `.velocai/tasks/<task-id>/exploration.md`. The note is the **grounding** that the planner uses to draft a plan, and it survives session boundaries. Per-task workspace means multiple explorers can work in parallel without collision.

This prompt activates the **explorer** agent. The explorer is read-only on code and writes only to `.velocai/tasks/<task-id>/`.

## Inputs

- `${input:task|}` — kebab-case slug. Becomes the task id and workspace directory name. **Required.** Example: `add-user-deletion`, `migrate-billing-to-stripe`. If omitted, propose one based on the user's description and confirm before writing.
- `${input:depth|standard|quick,standard,deep}` — how thorough to be. `quick` = map the affected surface and constraints only; skip the prior-art sweep and derive options from the touched files alone. `standard` = the full procedure, including prior-art search and code citations. `deep` = also fetch external references when relevant. Default `standard`.

## Procedure

### Phase 1: Discover prior art

Before writing:

1. Check whether an exploration note already exists at `.velocai/tasks/<task-id>/exploration.md` or under a related task id. If so, do **not** overwrite — propose extending, revising, or writing an `exploration-v2.md` in the same workspace instead. (Exception: a stub with `status: blocked-adr` is completed in place — see Phase 2.5.)
2. Identify the domain(s) this task touches and read `docs/domains/<domain>/CONCEPT.md` for each. Cite specifics.
3. Read `docs/domains/<domain>/CONTRACT.yaml` for each touched domain — contract entries (declared surface, endpoints, granted dependency edges) are binding constraints, not background.
4. Search `docs/adrs/` for ADRs that constrain the option space. Cite specifics.
5. Scan other `.velocai/tasks/<task-id>/` workspaces for prior work on the same or adjacent task ids. Avoid re-deriving.

### Phase 2: Map the territory

Build the fact base, **not** a solution. The explorer's job is to lay out what's true, not to choose.

1. **Problem statement** — restate the user's question in domain terms. If the user said "add user deletion," translate: "Users currently exist in PENDING/ACTIVE/SUSPENDED. We need a fourth state DELETED with the lifecycle described in `docs/domains/users/CONCEPT.md` and a 90-day retention window."
2. **Affected surface** — list every file or module that would change. Include line ranges. The planner uses this to size the work.
3. **Prior art** — point at any similar pattern already in the codebase. Example: "We soft-delete `Organizations` with a `deleted_at` timestamp; see `app/models/organization.py:42`."
4. **Constraints** — list every ADR, domain-contract entry, concept invariant, and convention that constrains the design space.
5. **Options** — enumerate 2–4 viable approaches. For each: one paragraph + the *strongest case for it* + the *single biggest concern*.
6. **Recommendation** — required in every full note; see the binding rule in the template below.
7. **Open questions** — anything you can't resolve from code/docs alone. Flag for human input.

### Phase 2.5: ADR trigger check

Before writing the note, evaluate whether the options enumerated in Phase 2 surface an architectural decision that should be settled by an ADR before any plan is written. The bar is `/write-adr`'s qualification bar: the choice is expensive to reverse, likely to be re-litigated by a future session, or counterintuitive. Concretely, **trigger an ADR (stop and recommend `/write-adr`) if any of these hold:**

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

**If triggered:** Skip the full Phase 3 note. Instead, write a *stub* to the same file, `.velocai/tasks/<task-id>/exploration.md`, with §Affected surface and §Constraints filled (the architect needs these), §Options listed as one-line headers only (no recommendation — the ADR will reframe the option space), and `## Open questions` containing exactly: `Architectural decision required — recommend /write-adr decision="<one-sentence question>" before planning.` Set the front-matter `status:` field to `status: blocked-adr` so downstream tooling sees the exploration is paused pending an ADR.

**Resume path:** once the ADR is accepted, re-run `/explore task=<same-task-id>`. This is the one case where completing the existing note in place is expected: the accepted ADR joins §Constraints, the option space collapses to what the ADR allows, and the note is finished per Phase 3 with `status: ready`.

**If not triggered:** Proceed to Phase 3 as normal. Because the non-trigger criteria guarantee the remaining choice is low-stakes and reversible, the Recommendation you write is binding by default — the planner adopts it unless the human overrides.

The decision rule that separates ADR-worthy from tactical: *would a future developer reading the resulting code ask "why did we do it this way?"* If yes, ADR. If they would read the code and understand, no ADR.

### Phase 3: Write the note

Use this exact shape. Front-matter is machine-readable; sections are human-readable. A completed note sets `status: ready`; only a Phase 2.5 stub uses `status: blocked-adr`.

```markdown
---
task: <task-id>                        # MUST match the workspace directory name
title: <Human-readable title>
status: ready                          # ready | blocked-adr
depth: quick | standard | deep
created: YYYY-MM-DD
agent-id: <session or instance ID>
domains:
  - docs/domains/<domain>/
adrs:
  - docs/adrs/adr-<NNNN>-<slug>.md
related-tasks:                         # any .velocai/tasks/<task-id>/ workspace that touched adjacent work
  - .velocai/<other-task-id>/
---

# Exploration: <title>

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
- Concept: `docs/domains/<domain>/CONCEPT.md`

## Constraints

- ADR-NNNN says <X>. Implication: we can't <Y>.
- `docs/domains/<domain>/CONTRACT.yaml` declares <X>. Implication: <Y>.
- Concept invariant: <X>. Implication: <Y>.

## Options

### Option A: <name>

<one paragraph: the approach>

**Strongest case:** <one sentence>
**Biggest concern:** <one sentence>

### Option B: <name>

<same shape>

## Recommendation

(Binding by default: the planner adopts this unless the human overrides. When an
accepted ADR governs the option space, the recommendation must comply with it.)

<one paragraph naming the chosen option and why.>

## Open questions

- <question requiring human input>
- <question requiring human input>

## Hand-off

Next: the planner drafts a plan from `.velocai/tasks/<task-id>/exploration.md`. Pass `task=<task-id>` explicitly.
```

### Phase 4: Present and stop

Show the proposed exploration note. Surface unresolved open questions clearly. Tell the user:

```
Exploration note drafted: .velocai/tasks/<task-id>/exploration.md
Status: ready | blocked-adr
Open questions for human input: <count>

Next: resolve open questions if any, then invoke the planner with task=<task-id>.
(If status is blocked-adr: run /write-adr first, then re-run /explore task=<task-id>.)
```

## What this prompt does NOT do

- **Propose a plan.** That's the planner's job. The exploration note enumerates options; it doesn't sequence edits.
- **Edit code.** The explorer may write only the exploration artifact under `.velocai/tasks/<task-id>/`.
- **Make architectural decisions.** If Phase 2.5 triggers, write a stub note recommending `/write-adr` and stop. The architect makes the decision; you don't pre-commit to options. (The binding Recommendation in the non-triggered path is not an architectural decision — the trigger criteria guarantee it is low-stakes and reversible.)
- **Skip prior art.** If the same problem has been explored before, you must find that note and either extend it or write a clearly-marked `exploration-v2.md`.

## Multi-agent safety

Different tasks = different workspaces. Multiple explorers can run in parallel on different task ids without contention; there is no shared state file — every downstream agent receives the task id explicitly. Same-task parallel work converges on the existing note (read first, then propose v2 if needed).
