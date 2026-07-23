---
name: implement
description: Execute the approved plan or accepted ADR for a task — single source of truth for the implementation phase. Receives the task id explicitly; all task artifacts live in .velocai/tasks/<task-id>/ (ADR-0018).
argument-hint: "task=<task-id> — the workspace under .velocai/tasks/; or an ADR id for post-ADR implementation"
agent: coder
---

# /implement

You are executing **the** implementation contract for this workspace. Same workflow regardless of how you were invoked: from a planner handoff, from a plan-review "Approve & Implement" handoff, or from the user typing `/implement` directly. One canonical procedure; one source of truth.

## Inputs

- `${input:task|}` — kebab-case task id naming the workspace `.velocai/tasks/<task-id>/` (ADR-0018: short descriptive name, never a ticket number or UUID). There is no shared state file; every downstream agent receives the task id explicitly.
- `${input:adr|}` — an ADR reference (`ADR-NNNN` or a path under `docs/adrs/`) for post-ADR implementation work with no plan.

## Resolve the entry context

In order of preference:

1. **Approved plan.** `task` given and `.velocai/tasks/<task-id>/plan.md` exists — the plan is the spec. It must carry `status: approved` in front-matter.
2. **Accepted ADR.** `adr` given — `docs/adrs/adr-<NNNN>-<slug>.md` is the spec. It must carry `status: accepted`; a `proposed` ADR is not yet implementable.
3. **Failing test** — no plan or ADR; a failing test on the branch is the spec.
4. **Freeform** — the user's description in chat is the spec, for changes small enough not to need a plan.

If none of those resolve and you can't find context, **stop** and tell the user what's missing (a plan via the planner, an ADR via `/write-adr`, or a failing test). Look in `.velocai/tasks/` first when resuming — each task has exactly one workspace holding all its artifacts.

## Required reading

After resolving context, open and read:

- The plan (`.velocai/tasks/<task-id>/plan.md`) or the ADR (`docs/adrs/adr-<NNNN>-<slug>.md`) — whichever is the spec.
- Other artifacts in the task workspace — `exploration.md` grounds the plan; a draft `CONTRACT.yaml` there is the contract being implemented.
- `AGENTS.md` — commands, boundaries, repo-specific knowledge.
- `docs/domains/<domain>/CONCEPT.md` and `docs/domains/<domain>/CONTRACT.yaml` for every domain the work touches. Contract entries (declared surface, endpoints, dependency edges) are **binding constraints**, not background.
- Any accepted ADR cited in the plan's front-matter.

Don't load: unrelated ADRs, other tasks' workspaces, generated instruction files (they restate ADR rules you already have at the source), or any file named `RESEARCH.md` — that is a human-only document class you must never read or cite (ADR-0013).

## Procedure

### 1. Confirm the entry condition

If no approved plan / accepted ADR / failing test exists, stop and request one. **Do not improvise scope.**

### 2. Mark status: in-progress on first edit

For plan-driven work: change `status: approved` to `status: in-progress` in the plan's front-matter. Commit this change alone (`chore(plan): mark <task-id> in-progress`) before any code edit. This is the signal to other agents that the task is locked.

For ADR-driven work: accepted ADRs are immutable — never edit one to track progress; this step is a no-op.

### 3. Walk the plan's edits in order

Execute the plan's sequenced edits in order. One commit per step where possible, Conventional Commits format:

```
<type>(<scope>): <subject>

[body]
[footer]
```

**For ADR-driven work:** the ADR's Decision and Consequences sections describe what to build; the frontmatter `rule:` is the invariant your change must make true. Use your judgment on commit boundaries.

### 4. Honor the binding constraints

The plan's non-goals and the repo's standing rules are your refusal list. If the work seems to require violating one, **stop** — do not silently work around it:

- The edit would change a domain's declared surface beyond what its `CONTRACT.yaml` grants → the contract must change first (via the contract pipeline), not the code silently.
- The edit would touch a generated instruction file or sentinel-marked region → change the source ADR and re-run projection instead (ADR-0006).
- The edit would add a dependency → stop and ask; the plan must be revised to name it.
- The edit would modify an ADR with `status: accepted` → never; a new superseding ADR is the only change path.
- The edit would add a Node/`.mjs` script or a PowerShell peer → forbidden; framework scripting is stdlib-only Python 3 (ADR-0012).
- The edit would add a recipe to the framework-owned `justfile` → project recipes go in `justfile.local` (ADR-0011).

### 5. After each step, run the smallest relevant verification

- Targeted tests: `py -3 -m pytest tests/<relevant_file>.py -q` (POSIX: `python3 -m pytest ... -q`) — never an unqualified `python` (ADR-0012).
- Lint the touched files: `py -3 -m ruff check <paths>`.
- Pipeline steps (projection, validation) only through `just` recipes — discover with `just --list`; never invoke pipeline scripts directly (ADR-0008).
- Save the full suite for the end.

If a step fails, **fix the step, don't skip it.** If the plan was wrong, stop and request a plan revision.

**Deliver the tests the plan promised.** If the plan's test plan names a test file or level, write exactly that — do not silently substitute something cheaper. If a promised test is genuinely unfeasible, stop and request a plan revision recording the substitution and its rationale.

### 5a. Distinguish plan correction from architectural escalation

When implementation reveals the plan needs to change, classify the change before acting:

**Plan correction — request a plan revision.** The plan was tactically wrong; the architectural frame is intact:

- A step targets the wrong file or symbol
- A promised test belongs at a different level or path
- A dependency or rollback detail was missed
- A constraint is incomplete but doesn't contradict an accepted ADR

The planner amends `.velocai/tasks/<task-id>/plan.md`; no ADR involved.

**Architectural escalation — stop and recommend `/write-adr`.** The discovery is structural and sets precedent:

- The target state is unimplementable as written, and the fix changes a public API, schema, or contract shape declared in a domain's `CONTRACT.yaml`
- An unanticipated constraint contradicts an existing accepted ADR (the fix is a new superseding ADR — accepted ADRs are never edited)
- A prohibition in the plan turns out to block necessary work, and lifting it is itself architectural (e.g. the plan forbade a dependency and no other approach exists)
- The discovery would make a future implementer ask "why did we do it this way?"

When escalating, **stop the implementation immediately**. Do NOT write code that pre-commits to the ADR's likely outcome. Hand off with: `Implementation blocked at step <N> — architectural escalation required. Recommend /write-adr decision="<one-sentence question>" → accept → revise plan → resume /implement task=<task-id>.`

### 6. Use applicable skills and prompts

When a repo prompt or skill covers the work (scaffolding a domain package, authoring a contract, creating a concept doc), follow it. They encode house conventions; bypassing them creates drift.

### 7. Run the full verification before claiming done

Before declaring work done (this is the repo's Definition of Done, per AGENTS.md):

- `py -3 -m pytest -q` — all tests green
- `py -3 -m ruff check .` — clean, no new suppressions without inline justification
- Any pipeline validation the plan names, run via its `just` recipe

If any check fails, fix it. Don't claim done with a failing check.

### 8. Tick the acceptance criteria

Verify each acceptance criterion in the plan is satisfied per its verification method, and tick them in the plan file.

For ADR-driven work: confirm the ADR's `rule:` now holds in the codebase, and note any Consequences follow-ups that remain (as follow-ups, not silent scope).

### 9. Mark status: done

For plan-driven work: change the plan's `status: in-progress` to `status: done`. Commit (`chore(plan): mark <task-id> done`).

For ADR-driven work: leave the ADR untouched — it is immutable.

Leave the workspace in place. Graduation of durable artifacts (contracts to `docs/domains/<domain>/`, decisions to `docs/adrs/`) and deletion of `.velocai/tasks/<task-id>/` happen at task closeout, not here (ADR-0018).

### 10. Hand off to review

Hand off to the reviewer agent with the task id and the plan path. The plan is the review contract — the reviewer grades the diff against it.

## Output (single message at end)

```
# Implementation complete — <task-id>

**Spec:** .velocai/tasks/<task-id>/plan.md (status: done)  |  docs/adrs/adr-<NNNN>-<slug>.md
**Files changed:** <N> files
**Tests:** <pass/total> passing (py -3 -m pytest -q)
**Lint:** ruff clean

## Steps completed
- <step 1: one-line summary>
- <step 2: one-line summary>
...

## Acceptance criteria
- [x] <criterion>
- [x] <criterion>
...

## Follow-ups (out of scope, not done)
- <thing the user should know about but I didn't touch>
```

If no follow-ups, omit that section.

## Hard refusals

- **Will not** read, write, cite, or create any file named `RESEARCH.md` — human-only document class (ADR-0013). A finding that must reach agents graduates to an ADR.
- **Will not** modify an ADR with `status: accepted` — immutable; supersede with a new ADR instead.
- **Will not** hand-edit a generated instruction file or sentinel-marked region — change the source ADR and re-run projection (ADR-0006).
- **Will not** invoke pipeline scripts directly — pipeline steps run only through `just` recipes (ADR-0008).
- **Will not** add Node/`.mjs` scripts or a PowerShell peer — stdlib-only Python 3 (ADR-0012).
- **Will not** add recipes to the framework-owned `justfile` — project recipes go in `justfile.local` (ADR-0011).
- **Will not** create a `CONSTITUTION.md` or any monolithic hand-edited rules file (ADR-0004).
- **Will not** add a dependency, delete or renumber an ADR, or change the contract/projection schema without asking first.
- **Will not** disable a test instead of fixing it.
- **Will not** add code that exceeds the plan's scope. Work the plan missed is noted as a follow-up, not done.
- **Will not** silently make an architectural choice the plan didn't settle — see step 5a; escalate to `/write-adr` first.
- **Will not** claim done with tests or `ruff check` failing.
- **Will not** commit secrets.

## Multi-agent safety

Each task has exactly one workspace, `.velocai/tasks/<task-id>/`, and there is no shared state file — the task id is passed explicitly. If two `/implement` invocations target the same task, the second to start will see the plan in `status: in-progress` (already locked by the first): stop and ask the user to coordinate — don't attempt parallel implementation of the same plan.

Different task ids in flight = safe by construction (ADR-0018).
