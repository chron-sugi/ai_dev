---
description: This file describes the repo-wide coding conventions and instructions for AI coding agents.


---

# Generate copilot-instructions.md

You are onboarding this repository for AI coding agents by producing `.github/copilot-instructions.md`. This file is the **always-on, repo-wide layer only**. Your output must contain nothing that belongs in a more targeted mechanism (glob-scoped instructions, prompt files, skills, lint config).

Work in three phases. Do not write the file until Phase 3.

## Phase 1 — Code discovery (do this first, silently)

Perform a comprehensive inventory before asking anything:

1. **Identify the stack.** Read manifest files (`package.json`, `pyproject.toml`, `*.csproj`, etc.), lockfiles, and framework config. Note exact major versions where behavior differs across versions.
2. **Map the structure.** Identify top-level directories and their roles. Note where source, tests, config, docs, and generated code live.
3. **Extract working commands.** Find build, test, lint, and run commands from scripts, CI workflows (`.github/workflows/**`), Makefiles, or task runners. Prefer commands proven by CI over ones you infer. If you can execute them, verify they succeed; record any required setup order.
4. **Inventory existing enforcement.** Read linter, formatter, and type-checker configs (ESLint, Prettier, ruff, tsconfig strictness, editorconfig, git hooks). Build a list of rules that are ALREADY mechanically enforced.
5. **Inventory existing agent context.** Check for `AGENTS.md`, `CLAUDE.md`, existing `copilot-instructions.md`, `.github/instructions/*.instructions.md`, ADRs (`docs/adr/**` or similar), and golden/reference files. Note what they already cover.
6. **Detect conventions from code.** Sample representative source files and identify recurring non-obvious patterns: naming, error handling, state management, import style, test structure. Flag patterns that an agent could not infer from a single file.

## Phase 2 — Clarifying questions (ask, then stop and wait)

Present a short summary of what you found, then ask only the questions discovery could not answer. Candidates:

- Conventions that appear inconsistent across the codebase — which variant is canonical?
- Deliberate decisions you can see but not explain (unusual dependency choices, avoided libraries, disabled lint rules) — what is the reasoning? Are there rejected alternatives worth recording?
- Directories or files agents should never touch or should treat as generated.
- Anything the team repeatedly corrects in AI-generated code today.

Ask at most 5–7 questions. Number them. Wait for answers before proceeding.

## Phase 3 — Generate the file

Write `.github/copilot-instructions.md` obeying ALL of these constraints:

**Include (only this):**
- One-paragraph summary of what the app does.
- Tech stack with versions, one line per item.
- Project structure: a short annotated tree or list of key directories.
- Verified build / test / lint / run commands, including required order or setup.
- Cross-cutting coding conventions that apply to the whole repo, written as single, simple statements — one rule per line.
- For each non-obvious rule, the reasoning in the same sentence ("Use X instead of Y because …"). If rejected alternatives are known, name them.
- Concrete preferred/avoided code examples for the 2–3 rules most likely to be violated.

**Exclude (hard rules):**
- Anything already enforced by the linter, formatter, or type checker found in Phase 1. If you're tempted to include it, cite the config that enforces it and drop it.
- Language-, framework-, or path-specific rules. Instead, list them at the end under a heading `## Deferred to scoped instructions` as proposed `.github/instructions/*.instructions.md` files with suggested `applyTo` globs — do not inline them.
- Multi-step task workflows or procedures (belongs in skills or prompt files).
- Personal preferences, tone/verbosity instructions, or anything about how to talk to the user.
- Vague aspirations ("write clean code", "follow best practices") — every rule must be checkable.
- Restating what is obvious from reading any single file.

**Format:**
- Hard cap: 2 pages (~600 words of instruction content). If over, cut lowest-value rules first, or demote them to the deferred list.
- Markdown headings; short lines; no prose paragraphs except the app summary.

After the file, output a short changelog note: what you excluded and why (already-enforced, path-specific, or workflow), so the exclusions are auditable.