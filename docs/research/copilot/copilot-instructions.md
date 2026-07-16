**What belongs in copilot-instructions.md** — always-on, repo-wide context every request benefits from:

- App summary and tech stack (one line each)
- Project structure — where things live, so the agent doesn't rediscover it
- Build/test/run commands that actually work, to minimize bash command and build failures
- Cross-cutting coding conventions, written as single, simple statements — one instruction per piece of information
- The reasoning behind rules ("use date-fns instead of moment.js because moment.js is deprecated"), since knowing why helps the AI in edge cases — this maps directly onto your ADR `rule` + rejected-alternatives projection
- Concrete preferred/avoided code examples rather than abstract rules

GitHub's own onboarding prompt caps it at no longer than 2 pages, with instructions broadly applicable to the entire project — consistent with your ~150–200 instruction-token compliance ceiling.

**What should NOT go in there:**

- Anything a linter or formatter already enforces — focus on non-obvious rules. Your enforcement-layering principle, verbatim in the official docs now.
- Language-, framework-, or path-specific rules — those belong in glob-scoped `*.instructions.md` files via `applyTo` (e.g., your Tailwind v4 rules scoped to `**/*.tsx` and `**/*.css`)
- Task workflows and multi-step procedures — VS Code now supports agent skills that load when a task matches, and custom agents for roles like reviewer or planner, so progressive disclosure is first-class; don't burn always-on budget on it
- Reusable task prompts → `.github/prompts/*.prompt.md`
- Personal preferences → user-level instructions, not the repo file
- Conversational fluff, tone requests, or long prose — every token competes with the ~2-page budget

One newer thing worth knowing: typing `/init` in chat generates a copilot-instructions.md tailored to your codebase, and VS Code now discovers customization files at the repo root even when you open a monorepo subfolder (opt-in setting). There's also a Chat Customizations Evaluations extension (preview) that analyzes instruction files for vague, contradictory, or overly complex rules — essentially automated probe verification for the instruction layer.

The July 2026 mental model: copilot-instructions.md is the thin always-on layer (orientation + non-obvious cross-cutting rules); everything conditional moves to instructions files, skills, prompts, or agents.