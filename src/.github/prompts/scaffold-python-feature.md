---
name: new-agent
description: "Scaffold a new custom agent (.github/agents/<name>.agent.md) from a required input contract. Refuses to generate with missing or vague inputs."
agent: agent
argument-hint: "agentName=<kebab-case> mission=<one sentence> routing=<when to invoke + artifact + boundary> inputs=<preconditions + missing-input behavior> output=<.agent/<task-id>/ path + status vocab> tools=<explicit child tool names> nonGoals=<2+ items> stopping=<conditions + cycle cap> [model=<id>] [userInvocable=false]"
---

# Task

Generate a new GitHub Copilot custom agent definition file at
`.github/agents/${input:agentName}.agent.md`.

You are generating a **role contract**, not documentation. Follow the
generation template and validation rules below exactly. Do not add
sections beyond the template.

## Required inputs

All eight fields below are REQUIRED. If any field is empty, ambiguous, or
fails its quality bar, do NOT generate the file. Instead respond with
`STATUS: BLOCKED` and a list of exactly the missing/failing fields with
one clarifying question each. Never invent defaults.

| Field | Value | Quality bar |
|---|---|---|
| Agent name (kebab-case, becomes filename) | `${input:agentName:kebab-case-name}` | Kebab-case, no spaces |
| Mission (one sentence) | `${input:mission:one imperative sentence}` | Single sentence, imperative |
| Routing description — when to invoke this agent, what artifact it returns, and its boundary vs. adjacent agents | `${input:routing:when to invoke + artifact returned + boundary vs adjacent agents}` | Must fail the vagueness test: "helpful assistant"-style text is rejected |
| Inputs / preconditions, and behavior when they are missing (ask / investigate / return BLOCKED / hand back) | `${input:inputs:preconditions + explicit missing-input behavior}` | Missing-input behavior must be explicit |
| Output artifact: file path under `.agent/<task-id>/`, plus status vocabulary (e.g. `COMPLETE \| BLOCKED \| NEEDS_REVIEW`) | `${input:output:.agent/<task-id>/<file> + closed status vocabulary}` | Path + closed status vocabulary both present |
| Tool allowlist (explicit child tool names, e.g. `read`, `search/codebase`, `runInTerminal` — never umbrella groups like `terminal`) | `${input:tools:comma-separated explicit child tool names}` | Minimal for the role; explicit names only |
| Non-goals / never-do list | `${input:nonGoals:2+ concrete never-do items}` | At least 2 concrete items |
| Stopping conditions and cycle caps (when done; max loop iterations before human escalation) | `${input:stopping:done conditions + numeric cycle cap}` | Numeric cap required if role participates in a review loop |

Optional (omit from frontmatter if not provided — do not guess):
- Model: `${input:model:optional model id}`
- `user-invocable: false` if this is a pure worker invoked only by an orchestrator: `${input:userInvocable:true|false}`

## Generation template

Produce the file with this exact structure:

```markdown
---
description: <routing description, one sentence, distinguishes from adjacent agents>
tools: [<allowlist>]
<model: … only if provided>
<user-invocable: false only if specified>
---

<Routing line: restate what this agent does, when to use it, what it returns.>

## Mission
<One sentence.>

## This agent does NOT
- <non-goals as bullets>

## Inputs
<Expected artifacts/context. Then: "If missing: <explicit behavior>.">

## Authority
✅ Always: <2–4 imperative rules>
⚠️ Ask first: <1–3 rules>
🚫 Never: <non-goals restated as hard prohibitions; include "Never commit secrets">

## Protocol
<≈5 phases as short guidance, e.g. Understand → Investigate → Draft → Self-check → Report. No line-by-line program.>

## Output
Write <artifact> to `.agent/<task-id>/<filename>`.
Report: status (<vocabulary>), findings, evidence (file:line), open questions, recommended next role, deviations.

## Done when
<Stopping conditions. Cycle cap: <N> iterations, then escalate to human.>
```

## Validation (run before emitting the file)

Reject your own draft and revise if any check fails:

1. Body ≤ 150 lines; prefer far less.
2. Frontmatter `description` passes the routing test: a dispatcher reading only the description can decide whether to route here vs. an adjacent agent.
3. `tools` contains only explicit child tool names; total tool count is minimal for the role.
4. No content that belongs in another layer: no lint-enforceable style rules, no repo-wide conventions (those live in instructions files), no orchestration mechanics, no ADR content restated as prose.
5. Imperative voice throughout; `IMPORTANT`/`YOU MUST` used at most twice.
6. Exactly one output artifact path, under `.agent/<task-id>/`.
7. Status vocabulary is a closed set.

## After generation

Output the file, then remind the user to:
1. Verify the agent loads via Chat → Diagnostics (chat customization diagnostics view).
2. Confirm declared tools are actually granted via the Agent Debug Log panel.
3. Run one probe prompt targeting the agent's 🚫 Never list to verify boundary compliance.