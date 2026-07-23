---
id: ADR-0021
title: Copilot file naming applied at deploy time, not in framework source
status: accepted
date: 2026-07-23
domain: velocai-artifacts
scope: "src/assets/**"
rule: "Rename velocai assets to the VS Code Copilot naming convention only during a user-requested deploy, never in the framework source tree."
projection: instructions
---

# Copilot file naming applied at deploy time, not in framework source

## Context

velocai's agent-facing assets (`src/assets/agents/`, `src/assets/prompts/`, `src/assets/instructions/`) are consumed through more than one AI tool surface, and each tool imposes its own file naming and location: VS Code Copilot expects assets under `.github/` folders with Copilot-specific suffixes, while Claude Code expects bare `<name>.md` files under `.claude/` directories. The source tree currently names assets with velocai's own type suffixes (`<name>.agents.md`, `<name>.prompt.md`, `<name>.instructions.md`). Without a settled rule, each new asset or deploy target re-opens the question of whose convention the source files should carry, and an agent session can plausibly "fix" source filenames to match whichever tool it is currently deploying to.

## Decision

Assets in the framework source tree are not named using Claude's file naming convention or any other tool's; they keep velocai's own tool-neutral names. Renaming to the VS Code Copilot naming convention happens only as a transform inside the deploy step that copies assets into the Copilot folders under `.github/`, and that deploy runs only on explicit user request.

## Rejected Alternatives

- **Name source assets with the Copilot convention directly** — couples the tool-neutral framework source to one deploy target; every other target would still need rename logic, and a Copilot convention change would force source-tree churn.
- **Name source assets with Claude's convention (bare `<name>.md` in tool-shaped directories)** — same single-tool coupling, and bare names drop the type suffix that lets a filename identify its asset class on sight.
- **Keep pre-renamed per-tool copies in the source tree** — duplicates every asset once per target and invites drift between the copies.
- **Rename automatically on framework deploy without a user request** — writing into a consumer repository's `.github/` Copilot folders is a user-visible integration choice, and those surfaces are generated-and-hand-edit-forbidden territory (ADR-0006) that velocai should not touch unsolicited.

## Consequences

The source tree stays tool-neutral: adding a new deploy target means adding a rename mapping to the deploy step, never renaming source files. The deploy step must now own and maintain an explicit per-asset-class mapping from velocai names to Copilot names, and that mapping is the only place the Copilot convention is encoded. Agents must not create Copilot-named files under `src/assets/` or hand-copy renamed assets into `.github/`; deployed Copilot copies are derived artifacts, refreshed only by re-running the user-requested deploy.
