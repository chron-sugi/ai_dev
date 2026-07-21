# Content Design Best Practices for GitHub Copilot Custom Agents in VS Code (as of July 18, 2026): A Unified Six-Agent Framework Report

## TL;DR
- **Build thin, contract-shaped agents on top of a durable context/artifact layer.** Each of your six agents should be a `.agent.md` file whose body is a role contract (routing description → mission/non-goals → inputs & missing-input behavior → authority/tools → bounded protocol → output schema → stopping conditions), not a persona essay. VS Code's own subagent docs (updated July 15, 2026) now ship almost exactly your composition — Planner → Plan Architect → Implementer → Reviewer with read-only planners/reviewers and edit-capable implementers — and Microsoft's `hve-core` RPI agents validate the artifact-on-disk handoff pattern.
- **All three uncertain citations from Analysis B are VERIFIED and their figures are accurate.** TeamBench (arXiv:2605.07073) confirms prompt-only verifiers attempt code edits 3.6× more and approve 49% of submissions that fail a deterministic grader; SkillsBench (arXiv:2602.12670) confirms focused 2–3 module skills beat comprehensive docs; and the VS Code subagent guidance documenting Explore→Planner→Plan Architect→Implementer→Reviewer exists.
- **Copilot cannot natively enforce most of your safety-critical constraints in the agent body.** There is no glob-scoped edit-tool restriction in `.agent.md` frontmatter and no native reviewer-can't-edit guarantee; those require PreToolUse hooks (Preview) or CI. Treat the agent file as *guidance*, put deterministic policy in hooks/lint/CI, and keep durable facts in the instruction/AGENTS.md layer — the empirical evidence (ETH Zürich, McMillan, UFMG) says bloated agent bodies cost tokens and reliability without buying compliance.

## Key Findings

### Verification outcomes (first-class deliverable)
1. **TeamBench — VERIFIED, figures accurate.** "TeamBench: Evaluating Agent Coordination under Enforced Role Separation," arXiv:2605.07073v1, posted 8 May 2026. 851 task templates / 931 seeded instances. Confirmed claims: prompt-only teams produce **3.6× more cases where the verifier attempts to edit the executor's code**; verifiers **approve 49% of submissions that fail the deterministic grader**; removing the verifier improved mean partial score in ablation; and **teams help where single agents struggle but hurt where single agents already perform well** (the Full-Team minus Solo gap swings 24.7 points between lowest and highest Solo-score quintiles). Prompt-only and sandbox-enforced teams reached statistically indistinguishable pass rates — enforcement changes *behavior*, not headline pass rate.
2. **SkillsBench — VERIFIED, figures accurate.** "SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks," arXiv:2602.12670, 2026 (Li et al.), 87 tasks across 8 domains from 400 submissions by 142 contributors. Confirmed: **focused skills with 2–3 modules outperform comprehensive documentation**; curated skills boost success by an average +16.2 percentage points across 84 tasks; and **self-generated skills yield negligible or negative performance** — human-curated procedural expertise is what helps.
3. **VS Code subagent guidance — VERIFIED.** The page "Subagents in Visual Studio Code" (code.visualstudio.com/docs/copilot/agents/subagents) documents a coordinator "Feature Builder" that composes `agents: ['Planner', 'Plan Architect', 'Implementer', 'Reviewer']`, with an explicit workflow: Planner breaks down tasks → Plan Architect validates plan against codebase patterns → feedback loop to Planner → Implementer writes code → Reviewer checks → Implementer fixes, iterating "between planning and architecture, and between review and implementation, until each phase converges." Planner and Plan Architect are `tools: ['read', 'search']` (read-only), Implementer gets a cheaper model. This maps almost one-to-one to your six roles (your Exploration agent is their research subagent; your two reviewers split their single Reviewer).
4. **Microsoft HVE-Core RPI — VERIFIED.** `microsoft/hve-core` documents the Research→Plan→Implement→Review (RPI) methodology with specialized custom agents (Task Researcher, Task Planner, Task Implementor, Task Reviewer, plus Task Challenger and an RPI orchestrator). Confirmed behaviors matching Analysis B's claim: findings are **preserved in files, not chat history** ("Research findings are preserved in files, not chat history"); context is **cleared between phases** (`Task Researcher → /clear → Task Planner → /clear → …`); planning artifacts live in `.copilot-tracking/` (plans/, details/, research); planner/researcher **never implement code**; and the framework treats disk artifacts as source of truth precisely because accumulated verbose context causes confusion.

### The consensus content structure
Every recommendation below rests on one architectural fact confirmed across official docs and three independent empirical studies: **an agent file is a system prompt, not a database.** The winning pattern is a thin, contract-shaped agent body sitting on top of durable instruction files, on-demand skills, per-task disk artifacts, and deterministic hooks/CI.

## Details

### (a) Consensus content structure: file format, frontmatter, body

**File and location.** Custom agents are `.agent.md` Markdown files with YAML frontmatter plus a Markdown body. VS Code auto-discovers them in the workspace `.github/agents/` folder, your user profile, or an organization `.github` repo; you can add locations via `chat.agentFilesLocations`. VS Code also reads `.claude/agents/*.md` (Claude sub-agent format). In naming conflicts, the lowest level wins (repository overrides organization overrides enterprise).

**Migration.** `.chatmode.md` is deprecated; custom agents are the unified successor. Existing `.chatmode.md` files in `.github/chatmodes/` continue to work and are automatically treated as custom agents; VS Code shows an info marker with a one-click quick-fix to migrate. To convert manually, rename to `.agent.md` and add a `name` field. GitHub has migrated its own repos to `.agent.md`.

**Body cap.** On GitHub.com (Copilot cloud agent), the prompt body has a **30,000-character maximum** — GitHub Docs ("Custom agents configuration"): "The prompt can be a maximum of 30,000 characters." Everything below the frontmatter is the system prompt.

**Frontmatter fields** (VS Code `target: vscode`): `description` (required — the routing signal), `name`, `argument-hint`, `tools` (allowlist; omit or `['*']` = all, `[]` = none), `agents` (subagent allowlist), `model` (single or prioritized fallback list), `user-invocable` (set `false` for delegation-only workers), `disable-model-invocation` (prevents being called as a subagent unless a coordinator explicitly allowlists it), `handoffs` (label/agent/prompt/send/model), `hooks` (Preview), `target` (`vscode` vs `github-copilot`), `mcp-servers`. `target: github-copilot` ignores `argument-hint` and `handoffs`. Reference other files (e.g., shared instructions) via Markdown links, and reference tools in the body with `#tool:<tool-name>` (e.g., `#tool:web/fetch`).

**The tool-group bug (still list individual tools).** When a tool *group/set* name (e.g., `runCommands`, `microsoftdocs/mcp`) is put in the `tools` array, VS Code shows it as enabled in the UI with a checkmark, but the agent **cannot invoke the child tools at runtime** — it reports the tools as "disabled" (microsoft/vscode issue #269600). The fix is to list the individual child tool names explicitly (e.g., `runInTerminal`, `getTerminalOutput`, `terminalLastCommand`). A related, separately-tracked defect: subagents invoked via `runSubagent`/CLI-in-VS-Code may be sandboxed to a read-only set and silently ignore their declared `tools` (issues #290205, #304574) — verify subagent tool access with diagnostics before relying on it. Also note a hard ceiling: Copilot Chat throws "Cannot have more than 128 tools per request," so bloated allowlists can break requests outright.

**`excludeAgent` for instructions files.** In `*.instructions.md` frontmatter, `excludeAgent` currently accepts `"code-review"` or `"coding-agent"` to hide an instruction file from those agents (GitHub changelog, Nov 12 2025); if absent, the file applies to all agents. Note the documented gap: there is **no value that excludes VS Code local Agent mode**, so review-only rules can still leak into coding sessions — a known limitation, not a solved problem.

**The ~1,000-line ceiling and structure.** GitHub Docs ("Using custom instructions to unlock the power of Copilot code review") states: "Best practice: Limit any single instruction file to a maximum of about 1,000 lines. Beyond this, the quality of responses may deteriorate." Keep files concise, use headings/bullets, be direct and imperative, and show examples. A separate, tighter cap applies specifically to review: **Copilot code review only reads the first 4,000 characters of a custom instruction file** ("This limit does not apply to Copilot Chat or Copilot cloud agent"). Agent bodies should be far shorter than the 1,000-line ceiling regardless.

**Verification tooling.** Use the **Chat customization diagnostics view** (right-click Chat → Diagnostics) to see all loaded custom agents, prompt files, instruction files, and skills plus load errors. The **Agent Debug Log panel** (Developer: Open Agent Debug Panel) shows, per request, exactly which instruction/skill/agent files were found and loaded, every tool call's input/output, and the full system prompt sent to the model; the **Chat Debug view** shows raw LLM request/response payloads. The community **Chat Customizations Evaluations** tooling (e.g., Microsoft's `waza`) treats `.agent.md` files as first-class evaluation targets and can auto-inject a `tool_constraint` grader that validates only the declared tools are called.

### (b) The role-contract template (recommended agent-body skeleton)
Analysis B's seven-element contract is the right body structure, and it is compatible with GitHub's 2,500-repo findings (specific persona, exact commands, three-tier boundaries, one real code example beats three paragraphs) and with the UFMG/McMillan evidence (keep it short). Recommended skeleton for each agent body:

1. **Routing-quality description** (in frontmatter `description` + first body line): what problem this agent solves, when to invoke it, what artifact it returns, and the distinguishing boundary from adjacent agents. GitHub's analysis of 2,500+ files found vagueness is the #1 failure — "You are a helpful coding assistant" fails; "You are a test engineer who writes tests for React components, follows these examples, and never modifies source code" works.
2. **Mission + explicit non-goals** — one sentence of mission, then a bulleted "This agent does NOT…" list.
3. **Inputs / preconditions with defined missing-input behavior** — what artifacts/context it expects, and exactly what to do when they are missing: investigate, ask a blocking question, return `BLOCKED`, or hand back to the previous role.
4. **Authority and tool permissions** — the `tools` allowlist plus a plain-language statement of what it may and may not change.
5. **Bounded working protocol** — ~5 phases as guidance ("Understand → Investigate → Draft → Self-check → Report"), NOT a brittle line-by-line program. McMillan's evidence shows compliance decays within a session regardless of file structure, so long prose programs are wasted tokens.
6. **Output schema** — status/verdict vocabulary, findings, evidence, open questions, artifact location, recommended next role, and deviations. This is the machine-readable contract that makes artifact-based handoffs work.
7. **Completion and stopping conditions + cycle caps** — when the agent is done, and hard caps on reviewer↔implementer and planner↔reviewer loops with human escalation.

**Three-tier boundaries** (GitHub's emergent convention, not a spec requirement): group rules as **✅ Always do / ⚠️ Ask first / 🚫 Never do**. The single most common rule across 2,500+ repos was "Never commit secrets." Use imperative voice; reserve `IMPORTANT`/`YOU MUST` for the one or two genuinely critical rules.

### (c) Per-role content recommendations for all six agents

General rules for all six: give each a routing-quality `description`; keep bodies short (target well under the ~150–200 effective-instruction budget); prefer references to skills/instructions over inlining; set `user-invocable: false` for pure workers if orchestrated by a coordinator; assign models by cost/reasoning need (cheaper/faster models for implementation and mechanical exploration, stronger reasoning models for planning, architecture, and review).

**1. Exploration agent.**
- *Tools:* read-only — `['read', 'search']` plus `web/fetch` if external research is needed; `search/codebase`, `search/usages`, `search/textSearch`.
- *Inputs / missing-input behavior:* a question or feature area. If under-specified, ask one blocking clarifying question, else proceed and note assumptions.
- *Protocol:* locate → read → corroborate → summarize with citations (file:line, URLs).
- *Output schema:* `status`, findings (what EXISTS), evidence (paths/line numbers/citations), open questions, artifact location.
- *Do-not-include:* does NOT decide what SHOULD be built, does NOT plan, does NOT edit.
- *Stopping:* when the question is answered with cited evidence, or `BLOCKED` if the codebase can't answer it.

**2. Planner agent.**
- *Tools:* read-only for research; if it writes a plan file, it needs an edit/create tool — but see the enforcement caveat below.
- *Inputs / missing-input behavior:* exploration findings + goal. If exploration is missing, return `BLOCKED: needs exploration` or invoke the explorer.
- *Protocol:* ingest research → decompose into phased tasks with success criteria → incorporate Plan Architect feedback → finalize.
- *Output schema:* a plan artifact (Overview, Requirements, Implementation Steps, Testing) with checkboxes and references to detail/research by line number (the HVE-Core pattern), plus `status` and `recommended next role`.
- *Do-not-include:* does NOT implement code; does NOT invent APIs — every step traces to cited research.
- *Cycle cap:* planner↔architect iterations capped (e.g., 2–3) before human review.
- **⚠️ Enforcement caveat:** Copilot has **no native way to scope the edit tool to a doc directory**. To restrict the Planner to writing only `docs/` or `.copilot-tracking/`, either give it no edit tool (all-or-nothing) or attach a **PreToolUse hook** that denies edits to paths outside the allowed glob (details in the hooks section).

**3. Implementer / coder agent.**
- *Tools:* the only role with edit + terminal — `['edit', 'search', 'read', 'runInTerminal', ...]` (list terminal child tools individually due to the tool-group bug). Often a cheaper/faster model (VS Code's example uses Claude Haiku 4.5 / Gemini 3 Flash for the Implementer).
- *Inputs / missing-input behavior:* an approved plan. If the plan has unresolved open questions, HALT and require explicit acknowledgment (HVE-Core's "Open Question Gate") rather than improvising.
- *Protocol:* per task: implement → run tests → fix errors before moving on → commit logical units.
- *Output schema:* `status`, changes made (files), test results/evidence, deviations, recommended next role.
- *Do-not-include:* does NOT silently redesign — when the plan is wrong, it **produces a deviation request** and hands back rather than quietly changing architecture.
- *Stopping:* when all plan tasks pass their checks, or `BLOCKED` on a deviation.

**4. Plan Reviewer agent.**
- *Tools:* read-only — `['read', 'search']`.
- *Inputs / missing-input behavior:* the plan artifact (+ research). If missing, `BLOCKED`.
- *Protocol:* check plan against research, feasibility, testing coverage, sequencing/dependencies, and non-goals.
- *Output schema:* verdict ∈ **{PASS, CHANGES_REQUIRED, BLOCKED}**, findings with evidence, and specific change requests routed back to the Planner.
- *Do-not-include:* does NOT rewrite the plan itself; it returns findings.
- *Cycle cap:* planner↔reviewer capped with human escalation.

**5. Implementation Reviewer agent.**
- *Tools:* read-only — `['read', 'search', 'codebase']`. Can run tests/linters read-only if given a scoped terminal tool, but should not edit.
- *Inputs / missing-input behavior:* the diff/implementation + plan. If missing, `BLOCKED`.
- *Protocol:* verify against plan and conventions; check correctness, security, performance, style with severity levels (critical/warning/info).
- *Output schema:* verdict ∈ **{PASS, CHANGES_REQUIRED, BLOCKED}**; **deterministic failures (failing tests, lint errors, type errors) automatically prevent PASS**; findings must carry objective evidence.
- *Do-not-include:* does NOT fix the findings itself (TeamBench shows prompt-only verifiers try to edit executor code 3.6× more — this is the exact failure to design against); does NOT PASS on vibes.
- *Cycle cap:* reviewer↔implementer capped (e.g., 3) before human escalation.

**6. Architect agent.**
- *Tools:* read-only for validation; doc-directory-scoped writes if it maintains an architecture doc (same enforcement caveat as Planner).
- *Inputs / missing-input behavior:* a plan or a design question. Triggered on non-trivial/cross-cutting work, NOT every task.
- *Protocol:* validate plan against codebase patterns; identify reusable utilities/libraries; flag steps that duplicate existing functionality; maintain `system-architecture.md` as source of truth.
- *Output schema:* `status`, architectural findings, reuse recommendations, risks, and feedback routed to Planner.
- *Do-not-include:* does NOT implement; does NOT gate trivial changes.

**Cross-cutting enforcement note:** the read-only guarantee for exploration/reviewers is achieved natively by omitting edit/terminal tools from the allowlist. But "reviewer cannot edit," "planner writes only to docs/," and "deterministic failures block PASS" are **behavioral** guarantees the model can violate; only hooks (PreToolUse deny) and CI make them deterministic. TeamBench is the empirical case for OS/sandbox-level enforcement over prompt-only role separation.

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

### (e) Anti-patterns catalog

**The six UFMG configuration smells** ("Configuration Smells in AGENTS.md Files," arXiv:2606.15828; 100 repos, 91/100 had ≥1 smell):
1. **Lint Leakage (62%)** — restating rules a linter/formatter already enforces. Fix: delete; let the linter own it.
2. **Context Bloat (42%)** — over-specification; the study operationalizes the smell at a **200-line threshold**. (Note: the UFMG paper attributes a ~200-line target to Anthropic guidance, but Anthropic's current published skill-authoring guidance states "Keep SKILL.md body under 500 lines for optimal performance" — treat the exact line number as a soft heuristic, not a hard rule.) Fix: selective loading, move detail to skills/instructions.
3. **Skill Leakage (35%)** — rarely-used procedures in the always-loaded file. Fix: move to a `SKILL.md`.
4. **Conflicting Instructions** — contradictory rules across files (Skill Leakage + Conflicting Instructions raise Context Bloat likelihood by 83%).
5. **Init Fossilization** — stale auto-generated (`/init`) content never revised.
6. **Blind Reference** — pointing at external docs without explaining when/why to read them. Fix: reference with a trigger condition.

**Additional anti-patterns (merged from both analyses):**
- **Persona-heavy prompts** — flavor text ("You are a 10x ninja") instead of a contract. Adds tokens, not compliance.
- **Swiss-army agents** — one generalist that plans, codes, and reviews. Start from one specialist per observed failure mode; give each a single job.
- **Copying repo guidance into agents** — duplicating AGENTS.md/instructions into every agent body. Reference the shared file instead.
- **Deterministic policy expressed in prose** — "never push to main," "only edit docs/" written as instructions. Practitioner reports put CLAUDE.md instruction compliance around 70%, which for destructive rules is a production incident waiting to happen; move to a hook/CI.
- **Bloated tool allowlists** — granting edit/terminal to agents that only read; also risks hitting the hard 128-tools-per-request limit and dilutes tool selection.
- **Chat-history-as-state** — relying on conversation memory across phases instead of disk artifacts; causes the context-exhaustion/confusion that HVE-Core redesigned around.
- **Reviewers that fix findings themselves** — the TeamBench 3.6× code-edit failure; reviewers must return findings, not patches.
- **Reviewer authority without objective evidence** — verifiers approving work that fails a deterministic grader (TeamBench's 49% false-approve). Deterministic failures must auto-block PASS.
- **Circular handoffs without convergence rules** — planner↔reviewer or implementer↔reviewer loops with no cycle cap or human escalation.
- **Mandatory architecture review for trivial work** — gating a one-line fix through the full pipeline; make the Architect trigger-based.
- **Vague descriptions that give no routing signal** — the #1 real-world failure; the `description` must say what problem, when to invoke, what it returns, and how it differs from neighbors.

### Hooks: the deterministic enforcement layer (Preview)
VS Code Copilot supports **agent hooks (Preview)** — official docs (code.visualstudio.com/docs/agent-customization/hooks) with eight lifecycle events in PascalCase: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`. A **`PreToolUse` hook fires before any tool call and can block it** by returning `permissionDecision: "deny"` (or `"ask"`/`"allow"`); the most restrictive decision wins across multiple hooks, and exit code 2 fails closed (denies) even if stdout JSON reports allow. The hook receives `tool_name` and `tool_input` (including target file paths), so it can enforce edit-scope restrictions (e.g., deny any edit outside `docs/`) and block dangerous commands (`rm -rf`, `DROP TABLE`) — the docs' stated purpose: "Enforce security policies: Block dangerous commands like `rm -rf` or `DROP TABLE` before they execute, regardless of how the agent was prompted." Config is JSON in `.github/hooks/*.json` (auto-loaded) or in the `.agent.md` `hooks` frontmatter field (requires `chat.useCustomAgentHooks: true`); VS Code uses the Claude Code / Copilot CLI hook format and auto-converts CLI lowerCamelCase names (`preToolUse`) to PascalCase. **Key limitation:** VS Code currently **ignores Claude-format matcher values** ("Currently, VS Code ignores matcher values, so hooks run on all tool invocations regardless of the matcher"), so the hook script itself must branch on `tool_name`. **Confirmed:** there is **no glob-scoped edit-tool restriction anywhere in `.agent.md` frontmatter** — `tools` scopes *which* tools, never *which paths* — so a PreToolUse hook is the only way to enforce path-scoped writes. This is the mechanism that turns Analysis B's soft constraints (planner-writes-only-docs, reviewer-can't-edit) into hard guarantees.

### (f) Evidence quality / epistemic status

| Claim / source | Tier | Notes |
|---|---|---|
| File format, frontmatter, 30k cap, migration, tool-group bug, `excludeAgent`, ~1,000-line ceiling, 4,000-char review cap, 128-tool limit, diagnostics, hooks | **High — official docs** | code.visualstudio.com, docs.github.com, github.blog changelog, tracked GitHub issues. Hooks are Preview (format may change). |
| VS Code Explore→Planner→Plan Architect→Implementer→Reviewer composition | **High — official docs** | code.visualstudio.com/docs/copilot/agents/subagents. Documented guidance, not a benchmarked prescription. |
| Microsoft HVE-Core RPI patterns | **High-ish — official Microsoft repo** | `microsoft/hve-core`; a shipped product/reference, but a design pattern, not an experiment. |
| GitHub 2,500-repo agents.md analysis | **Medium — vendor analysis** | github.blog; single-author descriptive analysis of public files, not peer-reviewed; correlational (what "successful" files do), no controlled outcome measure. |
| TeamBench (2605.07073), SkillsBench (2602.12670), ETH Zürich (2602.11988), UFMG smells (2606.15828), McMillan factorial (2605.10039) | **Suggestive — arXiv preprints** | Rigorous but mostly tested on **CLI agents (Claude Code, Codex, Qwen Code)**, not Copilot custom agents specifically. Generalization to your VS Code setup is reasonable but unproven. Several are recent and may be unrefereed. |
| Community repos & practitioner writeups (groupzer0/vs-code-agents, addyosmani/agent-skills, awesome-copilot, blogs) | **Low — pattern-level only** | Useful templates and conventions; no outcome evidence. The ~70% CLAUDE.md compliance figure is practitioner-reported, not benchmarked. |

**The ~150–200 line guidance vs. McMillan's null result — an explicit tension.** UFMG operationalizes Context Bloat at ~200 lines, and the "instruction budget" framing (practitioner blogs, citing Anthropic's built-in ~50-instruction system prompt) claims ~150–200 instructions before compliance degrades. But McMillan's factorial study (1,650 Claude Code sessions, arXiv:2605.10039) found **no detectable compliance contrast from file size (25–500 lines), instruction position, multi-file architecture, or conflicting-file presence** after multiple-testing correction (size and conflict nulls supported by affirmative-null Bayes factors); the dominant effect was **within-session attenuation (~5.6% lower compliance odds per generated function, OR=0.944)** and task identity. Reconciliation: the ~200-line rule is best justified by **token cost and context-window economics** (ETH Zürich: context files add 20–23% inference cost; over-retrieval is real) rather than by a proven size→compliance curve. Keep agent bodies short primarily to save tokens and reduce distraction, and manage within-session decay by scoping tasks tightly and using subagents with fresh context — not because a specific line count flips compliance.

### (g) Where consensus ends

**Workflow-level open questions (genuinely unsettled):**
- **More agents vs. one strong agent.** TeamBench shows teams help where single agents struggle but *hurt* where a single agent is already effective; a separate line of work ("Multi-agent teams hold experts back," arXiv:2602.01011) points the same way. Your six-agent pipeline is likely a net win on complex, multi-file, high-uncertainty tasks and a net *loss* on routine ones.
- **Does every task need plan review + architect?** Consensus is *no* — HVE-Core explicitly offers a "quick edits" path, and mandatory heavyweight review on trivial work is a listed anti-pattern. Make Plan Reviewer and Architect trigger-based.
- **Model-per-role assignment.** Docs suggest cheaper models for implementation and stronger reasoning models for planning/review, but the optimal split is untested for your workload — treat as a tunable, not a rule.
- **Autonomous review loops vs. CI/human acceptance.** TeamBench's 49% false-approve rate argues against trusting an LLM verifier as the final gate; deterministic graders (tests/lint/CI) and human acceptance should remain the source of truth, with the review agents as pre-filters.

**Evidence-level caveats:** the strongest empirical results are on CLI agents, not Copilot custom agents; several key papers are 2026 preprints; and the GitHub 2,500-repo analysis is correlational vendor content. Treat the whole stack as well-motivated engineering guidance, not settled science.

### (h) Staged implementation recommendations

**Stage 0 — Layers first (before any agent).** Write a lean `AGENTS.md`/`copilot-instructions.md` with only non-inferable facts (build/test commands, toolchain, structure). Add `*.instructions.md` with `applyTo` globs for language rules. Move bulky procedures into `SKILL.md` files. Stand up the task-artifact directory convention (`.ai/tasks/<task-id>/` or `.copilot-tracking/`). Put deterministic policy in lint/CI now.

**Stage 1 — Thin agents.** Author the six `.agent.md` files using the seven-element contract. Keep each body short. Read-only tools for exploration + both reviewers; edit+terminal for implementer only; doc-scoped writes for planner/architect. Set `user-invocable: false` on pure workers; wire `handoffs` and a coordinator with an `agents:` allowlist. List individual tool names (avoid the tool-group bug).

**Stage 2 — Deterministic guards.** Add PreToolUse hooks (Preview): deny reviewer edits, restrict planner/architect writes to their doc globs, block secrets/destructive commands. Make failing tests/lint auto-block reviewer PASS. Set cycle caps with human escalation.

**Stage 3 — Validate with diagnostics and probe testing.** Use the Diagnostics view and Agent Debug Log to confirm each agent loads the intended files and only its declared tools fire. Write probe tasks that try to make each agent violate its boundary (reviewer editing code, planner writing outside docs, implementer redesigning silently) and confirm hooks block them.

**Stage 4 — Benchmark configurations.** Compare, on a fixed task suite:
1. General-agent baseline (single built-in agent).
2. Explore → Implement.
3. Explore → Plan → Implement.
4. Full review pipeline (Explore → Plan → Plan Review → Implement → Impl Review).
5. Architect-on-trigger (add Architect only for cross-cutting tasks).

**Metrics to capture per configuration:** task success (tests pass), correction/rework rate, edit-scope violations, reviewer false-approval rate (approvals that fail a deterministic grader — TeamBench's key metric), token use, latency, and human-intervention count.

**Thresholds that change the recommendation:** if the full pipeline (config 4) does not beat Explore→Plan→Implement (config 3) on task success for your task mix, drop a reviewer or make it trigger-based. If reviewer false-approvals aren't near zero, the review agents are theater — lean harder on CI. If per-task token cost or latency rises without a success gain, collapse roles. If simple tasks regress under the pipeline vs. baseline, route them to a quick-edit path (the TeamBench "teams hurt where single agents already work" result).

## Recommendations
1. **Build the layers before the agents (Stage 0).** The ETH Zürich and UFMG evidence says an over-stuffed context/agent layer costs 20%+ tokens and reliability. Put only non-inferable facts in AGENTS.md, path rules in `*.instructions.md`, procedures in skills, and per-task state in a `.ai/tasks/` (or `.copilot-tracking/`) artifact directory that is the source of truth for handoffs.
2. **Make every agent body a seven-element contract, not a persona.** Lead with a routing-quality `description`; add mission/non-goals, inputs + missing-input behavior, tools/authority, a ~5-phase bounded protocol, an explicit output schema with a PASS/CHANGES_REQUIRED/BLOCKED vocabulary, and stopping conditions + cycle caps. Use ✅/⚠️/🚫 boundaries and one real code snippet over paragraphs.
3. **Enforce safety-critical constraints with hooks/CI, never prose.** Read-only reviewers via empty edit allowlist; planner/architect doc-scoping and reviewer-can't-edit via PreToolUse deny hooks (Preview, `chat.useCustomAgentHooks: true`); deterministic test/lint failures auto-block reviewer PASS. This is the direct lesson of TeamBench.
4. **Right-size the pipeline per task.** Route trivial work to a quick-edit/Explore→Implement path; reserve Plan Review and Architect for complex, cross-cutting, or high-uncertainty tasks. Benchmark configs 1–5 and let the metrics (not intuition) decide how many roles to keep.
5. **Verify with diagnostics and adversarial probes before trusting autonomy.** Confirm file loading and tool scoping in the Agent Debug Log; run boundary-violation probe tasks; keep CI/human acceptance as the final gate given the 49% LLM false-approve finding.

## Caveats
- **Hooks are Preview** — the format and behavior may change, VS Code ignores Claude-format matchers (branch on `tool_name` in-script), and an org policy can disable hooks. Don't ship a design that depends on unreleased behavior without a CI fallback.
- **No native edit-scoping** — `.agent.md` frontmatter cannot restrict the edit tool to a path glob; it's all-or-nothing per tool. Doc-scoped writes require a hook.
- **Known bugs** — tool *group* names in `tools` don't grant child-tool access (list individual tools); subagents may be sandboxed and silently ignore declared tools. Verify before relying on either.
- **Evidence is mostly from CLI agents** (Claude Code, Codex), not Copilot custom agents; the strongest numbers (TeamBench, SkillsBench, ETH, McMillan) are 2026 preprints. Generalization is reasonable but unproven for your exact stack.
- **The size guidance is contested** — treat short agent bodies and the ~1,000-line instruction ceiling as token-economy heuristics, not proven compliance thresholds; McMillan found file size had no measurable compliance effect, while within-session decay did. The specific "200-line" figure attributed to Anthropic in the UFMG study does not match Anthropic's current published skill guidance (under 500 lines) — use it as a soft signal only.
- **`excludeAgent` gap** — there is no value that excludes VS Code local Agent mode, so review-only instruction files can still leak into coding sessions; and Copilot code review only reads the first 4,000 characters of any instruction file.