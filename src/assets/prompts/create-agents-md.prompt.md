---
name: create-agents-md
description: "Author or trim a repo-root AGENTS.md to the evidence-backed minimum: command-first, human-curated, with every enforceable rule pushed to the mechanical layer instead of prose."
agent: agent
argument-hint: "mode=<create|trim> [target=<path, default AGENTS.md>] [lineBudget=<max lines, default 100>]"
---

# Task

Produce a minimal, command-first `${input:target:AGENTS.md}` for this repository.

You are writing **soft context, not enforcement**. AGENTS.md tells the agent what
to do; only the harness (lint, hooks, CI, permissions) proves whether it happened.
Every line you write costs instruction budget on every request, and the causal
evidence (Gloaguen et al., arXiv:2602.11988) shows bloated or auto-generated
files *reduce* task success and raise inference cost by over 20%. Minimal,
human-curated files help; everything else hurts. Act accordingly: your default
answer for any candidate line is **cut**.

## Phase 1 — Discover (read-only)

Before writing anything, gather ground truth:

1. Package manifests, task runners, and CI workflows — extract the *actual*
   build, test, lint, typecheck, and dev-server commands. A wrong command is
   worse than no command; the agent will confidently repeat it.
2. Linter/formatter/type-checker configs — inventory what is already
   mechanically enforced. Anything on this list is banned from the file.
3. Existing instruction files (`AGENTS.md`, `CLAUDE.md`,
   `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`)
   — note overlaps; never duplicate content across them.
4. Genuinely non-obvious repo knowledge: repo-specific tooling (e.g. "use `uv`,
   not pip"), non-standard layout, gotchas, deployment steps. The test:
   *could a competent agent infer this by reading the repo?* If yes, it's out.
5. Canonical detail docs and ADRs worth pointing at (never inlining).

Verify every command you intend to include by running it (or its `--help` /
dry-run form) before writing it down. `STATUS: BLOCKED` with the failing
command if a core command cannot be verified — do not guess.

## Phase 2 — Triage every candidate rule

Classify each rule you're tempted to write, in this order:

| Class | Test | Action |
|---|---|---|
| Tool-enforced | A linter/formatter/type-checker/hook/CI gate already enforces it | **Cut.** The tool is the source of truth. |
| Tool-enforceable | A lint rule, hook, or CI gate *could* enforce it deterministically | **Do not write it as prose.** Recommend the mechanical check in your report; optionally keep a one-line "why + pointer" so the agent makes good edge-case decisions. |
| Prose-only | Judgment, safety boundary, or non-obvious fact no tool can check | Keep — written as an action, never a vibe. |

Push enforceable rules to the fastest layer: PostToolUse hook > pre-commit > CI
> human review.

## Generation template

Produce the file with exactly these sections, omitting any that would be empty:

```markdown
# AGENTS.md

<2–4 sentences: what the project is, stack, product type, where main code lives.
No directory map — the evidence says overviews do not speed file discovery.>

## Commands

<Exact, copy-pasteable, verified. Build, test (with flags), single-test
invocation, lint, typecheck, dev server. This is the highest-value section.>

## Boundaries

🚫 NEVER: <e.g. commit secrets; push to main; add dependencies without discussion>
⚠️ ASK first: <e.g. migrations, deletions, schema changes>
✅ ALWAYS: <e.g. run <verify command> before declaring done>

## Repo-specific knowledge

<Only what cannot be inferred: tooling substitutions with the one-line why
("use `uv`, not pip — lockfile is uv-format"), gotchas, non-standard layout.>

## Pointers

<One line per detail doc or exemplar file: "For X, see docs/X.md". Point at
golden files rather than describing patterns. Never inline their content.>
```

## Validation (run before emitting; reject and revise on any failure)

1. Total length ≤ ${input:lineBudget:100} lines; aim well under.
2. Every line passes the audit question: *"what command proves this was done
   correctly?"* — or is an explicit boundary, why-line, or pointer.
3. No rule a discovered linter/formatter/type-checker config already enforces.
4. No content duplicated from README, CLAUDE.md, or copilot-instructions.md.
5. No directory maps, architecture overviews, or exhaustive style prose.
6. No secrets, no absolute paths, no user-home (`~`, `$HOME`) references.
7. No aspirational language ("clean", "careful", "idiomatic") — actions only.
8. Every command was verified against the repo in Phase 1.
9. Each surviving why-line for an enforceable rule names its enforcement layer.

If `mode=trim`: apply Phases 1–2 to the existing file, treat every current line
as a candidate, and report each cut with its triage class.

## Report (after emitting the file)

1. **Cut list** — every rule removed or withheld, with triage class and, for
   tool-enforceable ones, the recommended mechanical check (hook/lint/CI).
2. **Interop** — remind the user: make AGENTS.md canonical; bridge Claude Code
   with a one-line `CLAUDE.md` containing `@AGENTS.md`; in VS Code enable
   `chat.useAgentsMdFile` (and `chat.useNestedAgentsMdFiles` for monorepos);
   use glob-scoped `.instructions.md` with `applyTo` for path-specific rules.
3. **Maintenance** — review on a cadence and after stack changes; lint it in CI
   (AgentLint/agents-lint) for dead commands and stale paths; when the agent
   repeatedly violates a prose rule, promote it up the enforcement hierarchy
   and delete the prose.
