### (d) Content layering / separation-of-concerns

| Layer | File / location | What goes here | What does NOT go here | Load model |
|---|---|---|---|---|
| **Agent definition** | `.github/agents/*.agent.md` | Role contract: persona, tools, output schema, boundaries, handoffs, stopping conditions | Durable project facts; bulky procedures; deterministic policy | System prompt when agent selected |
| **Durable project facts** | `copilot-instructions.md` / `AGENTS.md` | Non-inferable project truths: build/test commands, required toolchain, repo structure, hard constraints | Lint rules a formatter enforces; rarely-used procedures; role behavior | Always-on, every session |
| **Path/language rules** | `*.instructions.md` with `applyTo` globs | Language/framework/folder-specific conventions | Project-wide facts; role personas | Loaded when matching files touched |
| **On-demand procedures** | `.github/skills/<name>/SKILL.md` | Bulky, repeatable multi-step procedures (progressive disclosure — only name+description load until invoked) | Always-needed facts; one-off tasks | Body loads only when invoked |
| **Reusable tasks** | `*.prompt.md` (migrating to skills) | Parameterized reusable prompts / slash commands | Persistent conventions | On invocation |
| **Per-task state (task artifacts)** | `.ai/tasks/<task-id>/`, `.agent/<task-id>/`, or HVE-Core's `.copilot-tracking/{research,plans,details}/` | Per-task scratch: research docs, plans with line-referenced details, decision logs, status | Anything durable/reusable across tasks; secrets | Read/written explicitly by agents; **source of truth for handoffs** |
| **Deterministic enforcement** | `.github/hooks/*.json` + scripts; lint/format configs; CI | PreToolUse deny rules, edit-scope guards, secret blocks, test/lint gates | Guidance/personas (put those in the agent) | Runs outside the model, guaranteed |
| **Referenced knowledge** | ADRs, design docs (referenced, not inlined) | Deep rationale — referenced with *when/why to read* | Full inlined contents (Blind Reference smell) | Agent reads on demand |

The task-artifact layer is what makes your multi-agent handoffs robust: per HVE-Core and TeamBench, **disk artifacts, not chat history, are the durable interface between roles.** Each agent's output schema should name the artifact path it wrote and the one the next role should read.
