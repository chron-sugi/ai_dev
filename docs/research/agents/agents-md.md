# AGENTS.md Best Practices (July 2026): What Belongs, What Doesn't, and Where Mechanical Enforcement Wins

## TL;DR
- **Keep AGENTS.md small, human-written, and command-first.** The strongest 2026 causal evidence (Gloaguen et al., ETH Zurich/LogicStar.ai, arXiv:2602.11988) shows a context file helps only when minimal and carrying genuinely non-obvious repo knowledge; auto-generated or bloated files *reduce* task success and inflate inference cost by over 20%. Everything a linter, formatter, type-checker, hook, or CI gate can enforce should live there, not in prose.
- **AGENTS.md is now a real cross-tool standard** — stewarded by the Linux Foundation's Agentic AI Foundation, "adopted by more than 60,000 open source projects and agent frameworks," and read natively by 20+ tools (OpenAI Codex, Cursor, GitHub Copilot coding agent, Gemini CLI, Windsurf, Aider, Zed, Factory, Jules, Devin, Amp, JetBrains Junie, and more). But adherence is soft context, not enforcement: prose "tells the agent what to do; the harness proves whether it happened."
- **In VS Code + Copilot, AGENTS.md support is real but opt-in.** You must enable `chat.useAgentsMdFile` (and `chat.useNestedAgentsMdFiles` for monorepos); AGENTS.md and `.github/copilot-instructions.md` are *both* loaded and merged (no guaranteed order), and glob-scoped `.instructions.md` files remain the more deterministic tool for path-specific rules.

## Key Findings

1. **The standard is settled; the content debate is not.** AGENTS.md is plain Markdown, no required fields, no mandated frontmatter. It was formalized in August 2025 (OpenAI Codex origins, with Google, Cursor, Factory, and Sourcegraph), donated to the Linux Foundation's Agentic AI Foundation in December 2025, and is now adopted by 60,000+ repos and 20+ tools.

2. **Empirical evidence now exists and is nuanced.** Three 2026 studies plus a late-2025 large-scale descriptive study give the first real data. The headline: *minimal, human-written files help slightly; verbose or auto-generated files hurt.*

3. **The instruction-budget ceiling is real, but the "structure matters" folklore is not well-supported.** The ~150–200 instruction budget is a practitioner heuristic loosely backed by the IFScale benchmark. A rigorous 1,650-session factorial study found file size, instruction position, and file architecture had *no detectable effect* on adherence — but within-session compliance decay is real.

4. **The prose/mechanical boundary is the central design decision.** Current best practice ("harness engineering," coined early 2026): if a rule can be enforced deterministically, it must not be restated in prose. Push checks to the fastest layer — PostToolUse hook > pre-commit > CI > human review.

5. **Tool division of labor has converged.** AGENTS.md = shared cross-tool baseline; CLAUDE.md, `.github/copilot-instructions.md`, `.cursor/rules` = tool-specific overlays. Claude Code does *not* read AGENTS.md natively — bridge with an `@AGENTS.md` import or symlink.



## Details

### What the standard says
AGENTS.md is "a README for agents." The official site recommends sections: project overview, build/test commands, code style, testing instructions, security considerations, plus PR/commit conventions and "anything you'd tell a new teammate." Nested files are supported — the closest AGENTS.md to the edited file wins, and OpenAI's own Codex repo uses 88 files. A v1.1 proposal is adding explicit progressive-disclosure semantics (optional YAML frontmatter with `description`/`tags` for lightweight indexing so harnesses can build an index and load files on demand).

### BELONGS in AGENTS.md
- **Exact, copy-pasteable commands.** Build, test (with flags), lint, typecheck, dev server, single-file test invocations. This is the single highest-value content; the descriptive study found build/run commands in 62.3% of files. Command-first beats prose: "instructions without verification commands are suggestions, not rules." Answer for every line: "what command proves this was done correctly?"
- **A short project-orientation paragraph.** What the project is, stack, product type, where main code lives — enough to distinguish a CLI from a marketing site. Two to four sentences.
- **Safety boundaries and human-in-the-loop triggers.** NEVER (commit secrets, add deps without discussion), ASK (before migrations, deletions), ALWAYS (explain the plan first). These are *soft* — the agent can still drift; back critical ones with hooks/permissions.
- **Non-obvious, genuinely novel repo knowledge.** Repo-specific tooling (e.g., "use `uv`, not pip"), gotchas, non-standard directory layouts, deployment steps. The evidence confirms agents demonstrably *follow* instructions — Gloaguen et al. found repo-specific tools were invoked dramatically more often when named in the file than when not — so the value is telling the agent things it cannot infer.
- **Pointers to detail docs** (progressive disclosure): "For TypeScript conventions, see docs/TYPESCRIPT.md" — a light-touch reference, not inlined content.

### Does NOT belong
- **Anything a linter/formatter/type-checker enforces.** Code style, import order, no-`var`, formatting. "Never put code format rules into AGENTS.md — run Prettier or oxfmt." The tool *is* the constraint; restating it wastes instruction budget, creates drift, and burdens the agent with something it cannot verify.
- **Duplicated documentation / README content.** The overview the agent can read itself. The ETH study found context-file overviews "do not provide effective overviews" and did not speed file discovery.
- **Exhaustive style guides / long prose.** Dilutes signal; agents selectively attend and discard.
- **Secrets.** Keep in gitignored local files (e.g., `CLAUDE.local.md`).
- **Aspirational/vague guidance.** "Keep code clean," "be careful," "idiomatic" — these don't translate to behavior. Write actions, not vibes.
- **Auto-generated `/init` output used as-is.** Treat it as a discard pile of what the agent can already discover, then aggressively trim.
- **Reasoning is the exception:** DO include the "why" behind rules that survive the toolchain-first cut — VS Code's docs and multiple studies agree the "why" improves edge-case decisions (e.g., "use `date-fns` instead of `moment.js` because moment.js is deprecated and increases bundle size").

### Length / token budget
- Every token loads on every request. Practitioner consensus: keep root files roughly 40–200 lines; split into nested files above ~150–200 lines. Per HumanLayer's "Writing a good CLAUDE.md," they keep their main repo's root file "under 60 lines," and Anthropic's docs warn "Bloated CLAUDE.md files cause Claude to ignore your actual instructions."
- The "~150–200 instructions" ceiling is a practitioner heuristic (HumanLayer: "Claude Code's system prompt contains ~50 individual instructions… Frontier thinking LLMs can follow ~150-200 instructions with reasonable consistency"), loosely evidence-adjacent. The nearest controlled data is IFScale (Jaroslawicz et al., Distyl AI, arXiv:2507.11538): across "20 state-of-the-art models across seven major providers… even the best frontier models only achieve 68% accuracy at the max density of 500 instructions." Treat the specific number as folklore; treat the *direction* (less is better) as evidence-backed.
- Codex silently truncates AGENTS.md beyond 32 KiB; Copilot and Claude Code have their own file-size ceilings (Copilot custom-agent files are unselectable beyond ~30,000 characters).

### Empirical evidence quality (evidence-backed vs. folklore)

**Study A — "Agent READMEs" (arXiv:2511.12884, Chatlatanagulchai et al., Nov 2025).** Large-scale *descriptive* study of 2,303 context files from 1,925 repos across Claude Code, Codex, and Copilot. Findings: files are complex and hard to read (median Flesch Reading Ease 16.6 for Claude Code — "dense legal contract" territory; AGENTS.md median FRE 39.6, "difficult"), evolve like configuration code through frequent small additions, prioritize functional content (implementation details 69.9%, architecture 67.7%, build/run 62.3%) and neglect security (14.5%) and performance (14.5%). This tells you what people *do*, not what *works* — no causal claim.

**Study B — "Evaluating AGENTS.md" (arXiv:2602.11988, Gloaguen et al., ETH Zurich/LogicStar.ai, Feb 2026).** The strongest *causal* evidence. Benchmark AGENTbench (138 real-world Python tasks from 12 niche repos with developer-written files) plus SWE-bench Lite (300 tasks), across four agent/model pairs (Claude Code/Sonnet-4.5, Codex/GPT-5.2, Codex/GPT-5.1-mini, Qwen Code/Qwen3-30B). Findings: human-written files gave a "+4% average increase in task success rate on AGENTbench"; LLM-generated files were "reducing the task success rate by an average of 3% compared to providing no context file"; both raised inference cost "by over 20%" (LLM-generated +20–23%; developer-written smaller, up to +19%). Directory maps/overviews did NOT speed file discovery. Conclusion: "human-written context files should describe only minimal requirements (e.g., specific tooling to use with this repository)." Notably, when all *other* documentation was stripped, LLM-generated files helped (+2.7% average) — explaining anecdotal "it helped" reports in poorly-documented repos.

**Study C — "Impact of AGENTS.md on Efficiency" (arXiv:2601.20404, Lulla et al., Jan/Mar 2026).** Real GitHub PRs, single agent (Codex/gpt-5.2-codex), 10 repos / 124 PRs. Found ~28.64% lower median runtime and ~16.58% lower median output-token consumption "while maintaining a comparable task completion behavior." Measures *efficiency*, not correctness; the gains were partly driven by a few outlier expensive runs (mean input/total tokens fell but medians were flat), and "comparable completion" rested on a 50-task manual sanity check, not a correctness evaluation.

**Reconciling B and C (they appear to conflict but don't).** They measure different outcomes on different populations. Study C tested only *real developer-written* files (the category B found helps), measured runtime/output-tokens rather than pass/fail, used one agent, and saw outlier-driven gains. Study B's "20%+ cost increase" is dominated by *LLM-generated* files stuffed with redundant instructions that trigger extra exploration and reasoning. A good human-written AGENTS.md can shorten exploration and reduce verbosity (C) without meaningfully changing whether a task is correctly solved (B). One genuine tension worth flagging: Study C *speculates* (its own word) that upfront structure reduces exploratory navigation, whereas Study B *directly measured* that overviews did not speed file discovery — so treat "an overview saves navigation" with caution.

**Study D — factorial adherence study (arXiv:2605.10039, McMillan, 2026).** 1,650 Claude Code sessions, 16,050 observations. None of four structural variables (file size 25–500 lines, instruction position, single vs. multi-file architecture, adjacent contradictions) produced a detectable adherence effect after multiple-testing correction. What *did* matter: task type and within-session position — compliance degrades as the agent generates more code in a session. This debunks common "put important rules at the top / conflicts kill adherence / bigger files fail" folklore.

**Vercel evals (vendor blog, Jan 27, 2026).** A compressed ~8KB docs index embedded in AGENTS.md hit a 100% pass rate on Next.js 16 API tasks; an Agent Skill maxed out at 79% *only with* explicit invocation instructions (and 53% by default, same as no docs), because "in 56% of cases, the skill was never used." Takeaway: passive always-on context currently beats on-demand retrieval for static framework knowledge. Vendor-sourced and single-framework — directional, not definitive.

**Explicitly folklore / unverified:** Specific percentage-improvement claims from vendor/marketing blogs ("29% faster" headlines that repackage Study C; "makes agents X% better"). The "under 60 lines / performance measurably degrades above it" claim is a practitioner assertion, not a controlled finding — and the factorial study actually found file size didn't affect adherence.

### The prose vs. mechanical enforcement boundary (the harness-engineering view)
This is where the requester's ADR-projection system is directly validated by 2026 best practice. The consensus (Factory.ai, Evil Martians, and multiple harness-engineering writeups):

- **AGENTS.md is the always-loaded prose layer; it explains intent and the "why." It cannot enforce.** "AGENTS.md can say 'no direct pushes to main.' It cannot stop `git push origin main`." Prose gets rationalized away; mechanical checks don't.
- **Enforcement hierarchy — push rules to the fastest deterministic layer:** PostToolUse hook (ms) > pre-commit (s) > CI (min) > human review (h). Blocking hooks > non-blocking warnings > behavioral nudges > prose rules.
- **The workflow:** observe drift → codify as a lint rule / hook / golden file → strip the corresponding prose from AGENTS.md → the tool becomes the source of truth. This is exactly an ADR → projection → lint/golden-file model.
- **ADRs belong in the repo as executable-adjacent artifacts.** They carry timestamps and status (Accepted/Superseded), so an agent can structurally judge validity. Free-form prose describing "how the system works" rots and poisons context — projecting durable ADR decisions into lint configs, golden files, and short instruction *pointers* (rather than long prose) is the correct architecture.
- **Coverage reality:** one practitioner audit classified project rules as ~40% cleanly mappable to linter configs, ~20% partially, and ~40% needing custom multi-condition hooks — so hooks/custom lint rules, not prose, should carry most enforceable rules.
- **Golden files / examples:** studies and VS Code docs agree agents respond better to concrete examples than abstract rules — point AGENTS.md at exemplar files rather than describing patterns in prose.

### Tool division of labor & interop
- **AGENTS.md** = shared, cross-tool baseline (commands, architecture, non-negotiables).
- **Claude Code** reads CLAUDE.md, NOT AGENTS.md natively (confirmed in Anthropic's memory docs). Bridge with a one-line `CLAUDE.md` containing `@AGENTS.md` (recommended — works on Windows, and lets you add Claude-only rules beneath the import) or `ln -s AGENTS.md CLAUDE.md` (symlink needs admin/Developer Mode on Windows). CLAUDE.md adds Claude-specific features: `@import`, path-scoped `.claude/rules/` with a `paths:` frontmatter field, auto memory, and `claudeMdExcludes`. Note Anthropic treats CLAUDE.md as context, not enforced config — "to block an action regardless of what Claude decides, use a PreToolUse hook."
- **GitHub Copilot** reads AGENTS.md, CLAUDE.md, `.github/copilot-instructions.md`, and GEMINI.md natively (Copilot coding agent since August 28, 2025), including nested AGENTS.md.
- **Symlink/pointer patterns:** canonical AGENTS.md + thin per-tool wrappers is the recommended single-source-of-truth setup. Tools like Ruler synthesize and inject instructions for agents that don't read AGENTS.md natively.
- **Keep it tested/maintained:** AGENTS.md rots (stale commands/paths). Treat it as version-controlled code, review on a cadence, and run a linter (AgentLint, agents-lint) in CI to catch dead commands, stale paths, missing enforcement, and contradictions. A wrong command is worse than no command — the agent will confidently repeat it, and once it discovers one mismatch, every other rule loses credibility.

## VS Code-Specific Section

**Native support & the setting.** VS Code automatically detects an `AGENTS.md` in the workspace root and applies it as always-on instructions — but the feature is gated by the `chat.useAgentsMdFile` setting. It historically shipped experimental/off-by-default, so if Copilot appears to ignore AGENTS.md, that setting is the first thing to check. As of the current docs (updated July 8, 2026), AGENTS.md, CLAUDE.md (`chat.useClaudeMdFile`), and `.github/copilot-instructions.md` are all recognized "always-on" instruction categories.

**Precedence / merging when both AGENTS.md and copilot-instructions.md exist.** VS Code does NOT pick one — it *combines* all instruction files into chat context with **no guaranteed order**. On conflict, the documented priority is: (1) personal/user instructions (highest), (2) repository instructions — `.github/copilot-instructions.md` *and* AGENTS.md occupy the *same* tier, (3) organization instructions (lowest). Conflict resolution between two repo-level files is therefore *probabilistic, not deterministic*. Gotcha: do not rely on AGENTS.md "overriding" copilot-instructions.md or vice versa; the cleanest practice is to not duplicate content across both.

**Nested AGENTS.md / monorepos.** Enable the experimental `chat.useNestedAgentsMdFiles` setting. When on, VS Code searches all subfolders recursively and injects each file's relative path into context; the agent decides which to apply based on the files being edited. In Copilot Chat, nested files merge root→leaf with deeper files taking precedence. For monorepos, also consider `chat.useCustomizationsInParentRepositories` (parent-repo discovery). Known gap: the Copilot *CLI* (separate from VS Code Chat) historically discovered nested AGENTS.md only along the cwd→git-root path, so folder-local files in sibling subtrees can be invisible when launched from the repo root — a documented open issue; VS Code Chat is ahead of the CLI here. In multi-root workspaces, config files must sit in the `.github/` directory at the workspace root; per-repo isolation means opening each repo in its own window.

**How glob-scoped `.instructions.md` interact with AGENTS.md.** These are a *different category*: `.instructions.md` files (default location `.github/instructions/`, searched recursively) are file-based and applied conditionally via the `applyTo` glob in YAML frontmatter (or semantic match on the `description`); AGENTS.md is always-on. VS Code's own guidance: start with a single `.github/copilot-instructions.md` for project-wide standards; add `.instructions.md` for per-file-type/framework rules; use AGENTS.md when you want one file recognized across multiple agents. For path-specific rules, `.instructions.md` with `applyTo` is more precise and more deterministic than nested AGENTS.md. All matching files are provided to the model together.

**VS Code gotchas / recommended config.**
- Instructions are NOT used for inline (as-you-type) completions — only chat/agent requests. Mirror critical rules into settings-based instructions or copilot-instructions.md if you need inline coverage.
- Use the **chat customization diagnostics view** (right-click the Chat view → Diagnostics) to see exactly which instruction files loaded — the fastest way to debug "my file isn't applying." Also check the **References** section of a chat response to confirm which files were used.
- For `*.instructions.md`, if no `applyTo` is set the file is not applied automatically; verify the glob matches the file you're editing. Relevant settings: `chat.includeApplyingInstructions`, `chat.includeReferencedInstructions`, `chat.useAgentsMdFile`.
- Files are cached; a modified instruction file may need an explicit reload. Custom-agent files above ~30,000 characters (excluding header) can't be selected.
- Settings-based codeGeneration/testGeneration instructions are deprecated (since VS Code 1.102) — use file-based instructions. Commit-message, PR-description, and code-review instructions still use settings.
- Recommended monorepo setup: a thin, cross-cutting root AGENTS.md + per-package AGENTS.md with `chat.useNestedAgentsMdFiles` on, OR `.github/instructions/*.instructions.md` with `applyTo` globs matching your folder structure — the latter is the more deterministic choice.

## Recommendations

**Stage 1 — Establish the minimal file (do now).**
- Write/trim AGENTS.md to a command-first core: one orientation paragraph + exact commands + safety boundaries (NEVER/ASK/ALWAYS) + pointers to detail docs. Target under ~150 lines; aim lower.
- Delete anything a linter/formatter/type-checker already enforces. Run the audit: for each line ask "what command proves this was done correctly?" If a tool enforces it, cut it.
- If you used `/init`, treat its output as a discard pile of what the agent can already find; keep only the non-obvious.

**Stage 2 — Wire the harness (where your ADR system pays off).**
- Project durable ADR decisions into: (a) lint/format configs, (b) custom lint rules / AST checks for architectural boundaries, (c) golden files *referenced* (not described) from AGENTS.md, (d) pre-commit + PostToolUse hooks, (e) CI gates.
- For every recurring agent mistake, add a mechanical check and *remove* the corresponding prose. Fastest layer wins.
- Keep a short "why + pointer" line in AGENTS.md for each enforced rule so the agent makes good edge-case decisions, but let the tool be the source of truth.

**Stage 3 — Interop & maintenance.**
- Make AGENTS.md canonical. Add a one-line `CLAUDE.md` with `@AGENTS.md`. In VS Code, enable `chat.useAgentsMdFile` (and `chat.useNestedAgentsMdFiles` for monorepos). Don't duplicate content between AGENTS.md and copilot-instructions.md.
- Use glob-scoped `.instructions.md` with `applyTo` for path-specific rules (more deterministic than nested AGENTS.md in VS Code).
- Add an AGENTS.md linter (AgentLint / agents-lint) to CI to catch stale commands/paths and missing enforcement. Review the file on a cadence and after major stack changes.

**Benchmarks/thresholds that would change these recommendations:**
- Agent ignores rules you care about → the file is likely over-budget; cut it and move rules to hooks.
- Compliance degrades late in long sessions → not a file problem (per the factorial study); use subagents/fresh context, not more prose.
- A rule is violated repeatedly despite being in prose → promote it up the enforcement hierarchy (hook/lint/CI).
- Tempted to add an overview/directory map → the causal evidence says it won't speed file discovery; skip it unless the repo structure would genuinely surprise someone who knows the framework.

## Caveats
- **Evidence is young and partly forward-dated.** The strongest causal study (arXiv:2602.11988) is a very recent preprint referencing GPT-5.x models; numbers may shift. The efficiency study (arXiv:2601.20404) did not measure correctness, and its gains were partly outlier-driven (mean vs. median divergence).
- **The "~150–200 instruction budget" and "under 60 lines" figures are practitioner heuristics,** not controlled findings; the factorial study found file size didn't affect adherence. Use them as directional guidance, not hard thresholds.
- **Vendor evals (Vercel) are single-framework and self-interested;** directional only.
- **Percentage-improvement marketing claims should be treated skeptically** and traced to primary sources — several "X% faster" headlines repackage the same efficiency study.
- **Tool behavior changes fast.** Native AGENTS.md support, setting names, and precedence rules shifted repeatedly through 2025–2026; verify `chat.useAgentsMdFile`, nested-file behavior, and Copilot/Claude precedence against current release notes before relying on them.
- **AGENTS.md is soft context, never enforcement** — the load-bearing caveat. Anything that must hold has to be mechanically enforced (lint, hook, CI, permissions), which is precisely why the ADR-projection-plus-harness architecture is the right one.


---
title: Agent indexes in AGENTS.md and subagent auto-invocation in GitHub Copilot
type: exploration
stage: explore
date: 2026-07-16
status: complete
tags: [agentic-workflow, copilot, subagents, agents-md, context-injection]
---

# Agent indexes in AGENTS.md and subagent auto-invocation in GitHub Copilot

## Question

Should AGENTS.md contain an index of available agents/subagents, and does GitHub Copilot require any document reference (index or otherwise) to invoke custom agents as subagents? A secondary constraint: some agent definitions live in user directories, where absolute paths embed a username and break on shared/cloned repos.

## Summary of findings

An AGENTS.md agent index is unnecessary for machine consumption in both Claude Code and GitHub Copilot. Both harnesses discover agent definitions from well-known locations and delegate automatically based on each agent's `description` metadata. An index is prose duplicating a mechanical mechanism — a drift-prone second write path, which contradicts the single-source-of-truth principle the ADR system exists to enforce. The residual value of an index is human navigation and portability to tools without native discovery, and even then it should be a pointer layer (one line per agent, linking to the canonical definition), never a second home for agent behavior.

## Finding 1: Copilot subagent invocation requires no document reference

GitHub Copilot (VS Code agent mode, CLI, and coding agent) invokes custom agents as subagents through three paths, none of which involve AGENTS.md:

1. **Automatic delegation.** Copilot analyzes the user's request, each configured agent's `description` frontmatter field, current context, and available tools, then delegates to a matching agent automatically. The subagent runs in an isolated context window and streams results back to the parent session.
2. **Direct invocation.** Naming the agent in the prompt ("Use the testing subagent to..."), the `/agent` slash command (CLI), or `copilot --agent=<name>`.
3. **Explicit tool call.** Referencing the `#runSubagent` tool in a prompt (VS Code).

Custom agents are also surfaced to the model as tools; the model starts a new agentic loop with a relevant agent when it judges delegation beneficial. By default all custom agents are eligible for automatic selection (`infer: true`).

**Implication:** the `description` field in `.agent.md` frontmatter is the routing mechanism. It plays the same role as the atomic `rule` field in ADR frontmatter — a small, structured, machine-consumed string that drives behavior. Investment belongs in sharp, trigger-oriented descriptions, not in index prose.

## Finding 2: Discovery locations and precedence

Copilot discovers agent profiles (`.agent.md` files) at multiple scopes:

| Scope | Location |
|---|---|
| Repository | `.github/agents/` |
| Organization | `{org}/.github` repository |
| User (CLI) | `~/.copilot/agents/` |
| Enterprise | enterprise-level config |

On filename conflict, narrower scope wins: user overrides repository, repository overrides organization, organization overrides enterprise.

Claude Code behaves analogously: project agents in `.claude/agents/`, personal agents in `~/.claude/agents/`, auto-discovered and auto-delegated via each agent's description.

## Finding 3: Delegation is controllable via frontmatter, not documents

Frontmatter fields govern subagent eligibility mechanically:

- `disable-model-invocation: true` — agent cannot be used as a subagent unless a coordinator explicitly allows it
- `user-invocable: false` — subagent-only; hidden from manual invocation
- `infer: true` (default) — eligible for automatic selection

Nesting caveat: subagents do not spawn further subagents by default. In VS Code, recursive delegation is gated by `chat.subagents.allowInvocationsFromSubagents` (off by default). Copilot CLI (v1.0.66+) exposes concurrency and depth limits via `/settings` for usage-based billing users.

## Finding 4: User-directory agents must not be indexed in repo documents

A repo-committed index referencing agents under a user home directory is wrong on arrival for every other consumer of the repo — a different contributor, CI, or the same person on another machine. This is worse than ordinary drift because it never starts correct. The username instability is the visible symptom; the underlying error is a scoping mismatch: repo files may reference only repo-scoped resources.

Decision rule:

- Agent matters to the project → promote it into version control (`.github/agents/` or `.claude/agents/`); it is then legitimately discoverable and (if ever needed) indexable.
- Agent is personal tooling → leave it in the user directory, unindexed by the repo. A personal registry, if wanted, belongs in user-scoped config (e.g., `~/.claude/CLAUDE.md`).

User-scope discovery makes this costless: user-directory agents participate fully in automatic delegation without any repo reference, and user-level definitions override repo-level ones on name collision.

## Finding 5: When an index still earns its place

A short registry (name + one-line "use when," pointing to the canonical definition) is justified only when both hold: (a) multiple repo-scoped agents exist, and (b) the audience includes humans navigating the repo or tools that read AGENTS.md as a generic entry point without native agent discovery. Two constraints apply:

- Index lines are instruction tokens and count against the practical compliance ceiling (~150–200 instruction tokens); index only agents a coordinator would plausibly delegate to.
- The index is a projection, not a source. Agent behavior lives solely in the `.agent.md` file; the index line should be derivable from (ideally generated from) the definition's frontmatter to prevent drift.

## Decision guidance

Do not add an agents index to AGENTS.md for the current toolchain (Claude Code + GitHub Copilot); both auto-discover and auto-delegate. Treat `.agent.md` `description` fields as the enforcement surface and write them with the same care as ADR `rule` fields. Keep user-directory agents out of all repo documents; promote to `.github/agents/` anything the project depends on. Revisit only if a tool without native discovery joins the toolchain, and then generate the index from frontmatter rather than hand-maintaining it.

## Rejected alternatives

- **Hand-maintained agents index in AGENTS.md** — duplicates auto-discovery; second write path; drift risk; spends instruction-token budget on redundant routing.
- **Repo index referencing user-directory agents** — broken for all other consumers; embeds usernames; scoping mismatch. Using `~`/`$HOME` fixes the path but not the availability problem.
- **`~`/`$HOME` references in shared docs generally** — needing them signals the agent should be promoted or the reference dropped.

## Open questions

- Portability of `.agent.md` frontmatter across Copilot surfaces: some VS Code-specific frontmatter is intentionally ignored by the cloud coding agent; if agent files are shared across surfaces, the portable/editor-specific split should be documented per agent.
- Whether description-driven auto-delegation is reliable enough to skip probe verification — descriptions are a routing contamination vector analogous to instruction files and likely warrant probe prompts of their own.

## Sources

- GitHub Docs — Custom agents and sub-agent orchestration (Copilot SDK): https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents
- GitHub Docs — Asking Copilot questions in your IDE (automatic delegation, `#runSubagent`): https://docs.github.com/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide
- GitHub Docs — Invoking custom agents (Copilot CLI, scope precedence): https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents
- GitHub Docs — Creating custom agents for Copilot CLI: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
- GitHub Changelog (2025-10-28) — Copilot CLI custom agents, `~/.copilot/agents`, agents-as-tools: https://github.blog/changelog/2025-10-28-github-copilot-cli-use-custom-agents-and-delegate-to-copilot-coding-agent/
- awesome-copilot Learning Hub — Agents and Subagents (`disable-model-invocation`, nesting rule, VS Code setting): https://awesome-copilot.github.com/learning-hub/agents-and-subagents/

Note on sourcing: GitHub first-party docs and changelog entries are authoritative for current behavior but change rapidly; the awesome-copilot learning hub is community-adjacent and should be re-verified against first-party docs before being cited in an ADR.


# AGENTS.md Best Practices (July 2026): What Belongs, What Doesn't, and Where Mechanical Enforcement Wins

## TL;DR
- **Keep AGENTS.md small, human-written, and command-first.** The strongest 2026 causal evidence (Gloaguen et al., ETH Zurich/LogicStar.ai, arXiv:2602.11988) shows a context file helps only when minimal and carrying genuinely non-obvious repo knowledge; auto-generated or bloated files *reduce* task success and inflate inference cost by over 20%. Everything a linter, formatter, type-checker, hook, or CI gate can enforce should live there, not in prose.
- **AGENTS.md is now a real cross-tool standard** — stewarded by the Linux Foundation's Agentic AI Foundation, "adopted by more than 60,000 open source projects and agent frameworks," and read natively by 20+ tools (OpenAI Codex, Cursor, GitHub Copilot coding agent, Gemini CLI, Windsurf, Aider, Zed, Factory, Jules, Devin, Amp, JetBrains Junie, and more). But adherence is soft context, not enforcement: prose "tells the agent what to do; the harness proves whether it happened."
- **In VS Code + Copilot, AGENTS.md support is real but opt-in.** You must enable `chat.useAgentsMdFile` (and `chat.useNestedAgentsMdFiles` for monorepos); AGENTS.md and `.github/copilot-instructions.md` are *both* loaded and merged (no guaranteed order), and glob-scoped `.instructions.md` files remain the more deterministic tool for path-specific rules.

## Key Findings

1. **The standard is settled; the content debate is not.** AGENTS.md is plain Markdown, no required fields, no mandated frontmatter. It was formalized in August 2025 (OpenAI Codex origins, with Google, Cursor, Factory, and Sourcegraph), donated to the Linux Foundation's Agentic AI Foundation in December 2025, and is now adopted by 60,000+ repos and 20+ tools.

2. **Empirical evidence now exists and is nuanced.** Three 2026 studies plus a late-2025 large-scale descriptive study give the first real data. The headline: *minimal, human-written files help slightly; verbose or auto-generated files hurt.*

3. **The instruction-budget ceiling is real, but the "structure matters" folklore is not well-supported.** The ~150–200 instruction budget is a practitioner heuristic loosely backed by the IFScale benchmark. A rigorous 1,650-session factorial study found file size, instruction position, and file architecture had *no detectable effect* on adherence — but within-session compliance decay is real.

4. **The prose/mechanical boundary is the central design decision.** Current best practice ("harness engineering," coined early 2026): if a rule can be enforced deterministically, it must not be restated in prose. Push checks to the fastest layer — PostToolUse hook > pre-commit > CI > human review.

5. **Tool division of labor has converged.** AGENTS.md = shared cross-tool baseline; CLAUDE.md, `.github/copilot-instructions.md`, `.cursor/rules` = tool-specific overlays. Claude Code does *not* read AGENTS.md natively — bridge with an `@AGENTS.md` import or symlink.

## Details

### What the standard says
AGENTS.md is "a README for agents." The official site recommends sections: project overview, build/test commands, code style, testing instructions, security considerations, plus PR/commit conventions and "anything you'd tell a new teammate." Nested files are supported — the closest AGENTS.md to the edited file wins, and OpenAI's own Codex repo uses 88 files. A v1.1 proposal is adding explicit progressive-disclosure semantics (optional YAML frontmatter with `description`/`tags` for lightweight indexing so harnesses can build an index and load files on demand).

### BELONGS in AGENTS.md
- **Exact, copy-pasteable commands.** Build, test (with flags), lint, typecheck, dev server, single-file test invocations. This is the single highest-value content; the descriptive study found build/run commands in 62.3% of files. Command-first beats prose: "instructions without verification commands are suggestions, not rules." Answer for every line: "what command proves this was done correctly?"
- **A short project-orientation paragraph.** What the project is, stack, product type, where main code lives — enough to distinguish a CLI from a marketing site. Two to four sentences.
- **Safety boundaries and human-in-the-loop triggers.** NEVER (commit secrets, add deps without discussion), ASK (before migrations, deletions), ALWAYS (explain the plan first). These are *soft* — the agent can still drift; back critical ones with hooks/permissions.
- **Non-obvious, genuinely novel repo knowledge.** Repo-specific tooling (e.g., "use `uv`, not pip"), gotchas, non-standard directory layouts, deployment steps. The evidence confirms agents demonstrably *follow* instructions — Gloaguen et al. found repo-specific tools were invoked dramatically more often when named in the file than when not — so the value is telling the agent things it cannot infer.
- **Pointers to detail docs** (progressive disclosure): "For TypeScript conventions, see docs/TYPESCRIPT.md" — a light-touch reference, not inlined content.

### Does NOT belong
- **Anything a linter/formatter/type-checker enforces.** Code style, import order, no-`var`, formatting. "Never put code format rules into AGENTS.md — run Prettier or oxfmt." The tool *is* the constraint; restating it wastes instruction budget, creates drift, and burdens the agent with something it cannot verify.
- **Duplicated documentation / README content.** The overview the agent can read itself. The ETH study found context-file overviews "do not provide effective overviews" and did not speed file discovery.
- **Exhaustive style guides / long prose.** Dilutes signal; agents selectively attend and discard.
- **Secrets.** Keep in gitignored local files (e.g., `CLAUDE.local.md`).
- **Aspirational/vague guidance.** "Keep code clean," "be careful," "idiomatic" — these don't translate to behavior. Write actions, not vibes.
- **Auto-generated `/init` output used as-is.** Treat it as a discard pile of what the agent can already discover, then aggressively trim.
- **Reasoning is the exception:** DO include the "why" behind rules that survive the toolchain-first cut — VS Code's docs and multiple studies agree the "why" improves edge-case decisions (e.g., "use `date-fns` instead of `moment.js` because moment.js is deprecated and increases bundle size").

### Length / token budget
- Every token loads on every request. Practitioner consensus: keep root files roughly 40–200 lines; split into nested files above ~150–200 lines. Per HumanLayer's "Writing a good CLAUDE.md," they keep their main repo's root file "under 60 lines," and Anthropic's docs warn "Bloated CLAUDE.md files cause Claude to ignore your actual instructions."
- The "~150–200 instructions" ceiling is a practitioner heuristic (HumanLayer: "Claude Code's system prompt contains ~50 individual instructions… Frontier thinking LLMs can follow ~150-200 instructions with reasonable consistency"), loosely evidence-adjacent. The nearest controlled data is IFScale (Jaroslawicz et al., Distyl AI, arXiv:2507.11538): across "20 state-of-the-art models across seven major providers… even the best frontier models only achieve 68% accuracy at the max density of 500 instructions." Treat the specific number as folklore; treat the *direction* (less is better) as evidence-backed.
- Codex silently truncates AGENTS.md beyond 32 KiB; Copilot and Claude Code have their own file-size ceilings (Copilot custom-agent files are unselectable beyond ~30,000 characters).

### Empirical evidence quality (evidence-backed vs. folklore)

**Study A — "Agent READMEs" (arXiv:2511.12884, Chatlatanagulchai et al., Nov 2025).** Large-scale *descriptive* study of 2,303 context files from 1,925 repos across Claude Code, Codex, and Copilot. Findings: files are complex and hard to read (median Flesch Reading Ease 16.6 for Claude Code — "dense legal contract" territory; AGENTS.md median FRE 39.6, "difficult"), evolve like configuration code through frequent small additions, prioritize functional content (implementation details 69.9%, architecture 67.7%, build/run 62.3%) and neglect security (14.5%) and performance (14.5%). This tells you what people *do*, not what *works* — no causal claim.

**Study B — "Evaluating AGENTS.md" (arXiv:2602.11988, Gloaguen et al., ETH Zurich/LogicStar.ai, Feb 2026).** The strongest *causal* evidence. Benchmark AGENTbench (138 real-world Python tasks from 12 niche repos with developer-written files) plus SWE-bench Lite (300 tasks), across four agent/model pairs (Claude Code/Sonnet-4.5, Codex/GPT-5.2, Codex/GPT-5.1-mini, Qwen Code/Qwen3-30B). Findings: human-written files gave a "+4% average increase in task success rate on AGENTbench"; LLM-generated files were "reducing the task success rate by an average of 3% compared to providing no context file"; both raised inference cost "by over 20%" (LLM-generated +20–23%; developer-written smaller, up to +19%). Directory maps/overviews did NOT speed file discovery. Conclusion: "human-written context files should describe only minimal requirements (e.g., specific tooling to use with this repository)." Notably, when all *other* documentation was stripped, LLM-generated files helped (+2.7% average) — explaining anecdotal "it helped" reports in poorly-documented repos.

**Study C — "Impact of AGENTS.md on Efficiency" (arXiv:2601.20404, Lulla et al., Jan/Mar 2026).** Real GitHub PRs, single agent (Codex/gpt-5.2-codex), 10 repos / 124 PRs. Found ~28.64% lower median runtime and ~16.58% lower median output-token consumption "while maintaining a comparable task completion behavior." Measures *efficiency*, not correctness; the gains were partly driven by a few outlier expensive runs (mean input/total tokens fell but medians were flat), and "comparable completion" rested on a 50-task manual sanity check, not a correctness evaluation.

**Reconciling B and C (they appear to conflict but don't).** They measure different outcomes on different populations. Study C tested only *real developer-written* files (the category B found helps), measured runtime/output-tokens rather than pass/fail, used one agent, and saw outlier-driven gains. Study B's "20%+ cost increase" is dominated by *LLM-generated* files stuffed with redundant instructions that trigger extra exploration and reasoning. A good human-written AGENTS.md can shorten exploration and reduce verbosity (C) without meaningfully changing whether a task is correctly solved (B). One genuine tension worth flagging: Study C *speculates* (its own word) that upfront structure reduces exploratory navigation, whereas Study B *directly measured* that overviews did not speed file discovery — so treat "an overview saves navigation" with caution.

**Study D — factorial adherence study (arXiv:2605.10039, McMillan, 2026).** 1,650 Claude Code sessions, 16,050 observations. None of four structural variables (file size 25–500 lines, instruction position, single vs. multi-file architecture, adjacent contradictions) produced a detectable adherence effect after multiple-testing correction. What *did* matter: task type and within-session position — compliance degrades as the agent generates more code in a session. This debunks common "put important rules at the top / conflicts kill adherence / bigger files fail" folklore.

**Vercel evals (vendor blog, Jan 27, 2026).** A compressed ~8KB docs index embedded in AGENTS.md hit a 100% pass rate on Next.js 16 API tasks; an Agent Skill maxed out at 79% *only with* explicit invocation instructions (and 53% by default, same as no docs), because "in 56% of cases, the skill was never used." Takeaway: passive always-on context currently beats on-demand retrieval for static framework knowledge. Vendor-sourced and single-framework — directional, not definitive.

**Explicitly folklore / unverified:** Specific percentage-improvement claims from vendor/marketing blogs ("29% faster" headlines that repackage Study C; "makes agents X% better"). The "under 60 lines / performance measurably degrades above it" claim is a practitioner assertion, not a controlled finding — and the factorial study actually found file size didn't affect adherence.

### The prose vs. mechanical enforcement boundary (the harness-engineering view)
This is where the requester's ADR-projection system is directly validated by 2026 best practice. The consensus (Factory.ai, Evil Martians, and multiple harness-engineering writeups):

- **AGENTS.md is the always-loaded prose layer; it explains intent and the "why." It cannot enforce.** "AGENTS.md can say 'no direct pushes to main.' It cannot stop `git push origin main`." Prose gets rationalized away; mechanical checks don't.
- **Enforcement hierarchy — push rules to the fastest deterministic layer:** PostToolUse hook (ms) > pre-commit (s) > CI (min) > human review (h). Blocking hooks > non-blocking warnings > behavioral nudges > prose rules.
- **The workflow:** observe drift → codify as a lint rule / hook / golden file → strip the corresponding prose from AGENTS.md → the tool becomes the source of truth. This is exactly an ADR → projection → lint/golden-file model.
- **ADRs belong in the repo as executable-adjacent artifacts.** They carry timestamps and status (Accepted/Superseded), so an agent can structurally judge validity. Free-form prose describing "how the system works" rots and poisons context — projecting durable ADR decisions into lint configs, golden files, and short instruction *pointers* (rather than long prose) is the correct architecture.
- **Coverage reality:** one practitioner audit classified project rules as ~40% cleanly mappable to linter configs, ~20% partially, and ~40% needing custom multi-condition hooks — so hooks/custom lint rules, not prose, should carry most enforceable rules.
- **Golden files / examples:** studies and VS Code docs agree agents respond better to concrete examples than abstract rules — point AGENTS.md at exemplar files rather than describing patterns in prose.

### Tool division of labor & interop
- **AGENTS.md** = shared, cross-tool baseline (commands, architecture, non-negotiables).
- **Claude Code** reads CLAUDE.md, NOT AGENTS.md natively (confirmed in Anthropic's memory docs). Bridge with a one-line `CLAUDE.md` containing `@AGENTS.md` (recommended — works on Windows, and lets you add Claude-only rules beneath the import) or `ln -s AGENTS.md CLAUDE.md` (symlink needs admin/Developer Mode on Windows). CLAUDE.md adds Claude-specific features: `@import`, path-scoped `.claude/rules/` with a `paths:` frontmatter field, auto memory, and `claudeMdExcludes`. Note Anthropic treats CLAUDE.md as context, not enforced config — "to block an action regardless of what Claude decides, use a PreToolUse hook."
- **GitHub Copilot** reads AGENTS.md, CLAUDE.md, `.github/copilot-instructions.md`, and GEMINI.md natively (Copilot coding agent since August 28, 2025), including nested AGENTS.md.
- **Symlink/pointer patterns:** canonical AGENTS.md + thin per-tool wrappers is the recommended single-source-of-truth setup. Tools like Ruler synthesize and inject instructions for agents that don't read AGENTS.md natively.
- **Keep it tested/maintained:** AGENTS.md rots (stale commands/paths). Treat it as version-controlled code, review on a cadence, and run a linter (AgentLint, agents-lint) in CI to catch dead commands, stale paths, missing enforcement, and contradictions. A wrong command is worse than no command — the agent will confidently repeat it, and once it discovers one mismatch, every other rule loses credibility.

## VS Code-Specific Section

**Native support & the setting.** VS Code automatically detects an `AGENTS.md` in the workspace root and applies it as always-on instructions — but the feature is gated by the `chat.useAgentsMdFile` setting. It historically shipped experimental/off-by-default, so if Copilot appears to ignore AGENTS.md, that setting is the first thing to check. As of the current docs (updated July 8, 2026), AGENTS.md, CLAUDE.md (`chat.useClaudeMdFile`), and `.github/copilot-instructions.md` are all recognized "always-on" instruction categories.

**Precedence / merging when both AGENTS.md and copilot-instructions.md exist.** VS Code does NOT pick one — it *combines* all instruction files into chat context with **no guaranteed order**. On conflict, the documented priority is: (1) personal/user instructions (highest), (2) repository instructions — `.github/copilot-instructions.md` *and* AGENTS.md occupy the *same* tier, (3) organization instructions (lowest). Conflict resolution between two repo-level files is therefore *probabilistic, not deterministic*. Gotcha: do not rely on AGENTS.md "overriding" copilot-instructions.md or vice versa; the cleanest practice is to not duplicate content across both.

**Nested AGENTS.md / monorepos.** Enable the experimental `chat.useNestedAgentsMdFiles` setting. When on, VS Code searches all subfolders recursively and injects each file's relative path into context; the agent decides which to apply based on the files being edited. In Copilot Chat, nested files merge root→leaf with deeper files taking precedence. For monorepos, also consider `chat.useCustomizationsInParentRepositories` (parent-repo discovery). Known gap: the Copilot *CLI* (separate from VS Code Chat) historically discovered nested AGENTS.md only along the cwd→git-root path, so folder-local files in sibling subtrees can be invisible when launched from the repo root — a documented open issue; VS Code Chat is ahead of the CLI here. In multi-root workspaces, config files must sit in the `.github/` directory at the workspace root; per-repo isolation means opening each repo in its own window.

**How glob-scoped `.instructions.md` interact with AGENTS.md.** These are a *different category*: `.instructions.md` files (default location `.github/instructions/`, searched recursively) are file-based and applied conditionally via the `applyTo` glob in YAML frontmatter (or semantic match on the `description`); AGENTS.md is always-on. VS Code's own guidance: start with a single `.github/copilot-instructions.md` for project-wide standards; add `.instructions.md` for per-file-type/framework rules; use AGENTS.md when you want one file recognized across multiple agents. For path-specific rules, `.instructions.md` with `applyTo` is more precise and more deterministic than nested AGENTS.md. All matching files are provided to the model together.

**VS Code gotchas / recommended config.**
- Instructions are NOT used for inline (as-you-type) completions — only chat/agent requests. Mirror critical rules into settings-based instructions or copilot-instructions.md if you need inline coverage.
- Use the **chat customization diagnostics view** (right-click the Chat view → Diagnostics) to see exactly which instruction files loaded — the fastest way to debug "my file isn't applying." Also check the **References** section of a chat response to confirm which files were used.
- For `*.instructions.md`, if no `applyTo` is set the file is not applied automatically; verify the glob matches the file you're editing. Relevant settings: `chat.includeApplyingInstructions`, `chat.includeReferencedInstructions`, `chat.useAgentsMdFile`.
- Files are cached; a modified instruction file may need an explicit reload. Custom-agent files above ~30,000 characters (excluding header) can't be selected.
- Settings-based codeGeneration/testGeneration instructions are deprecated (since VS Code 1.102) — use file-based instructions. Commit-message, PR-description, and code-review instructions still use settings.
- Recommended monorepo setup: a thin, cross-cutting root AGENTS.md + per-package AGENTS.md with `chat.useNestedAgentsMdFiles` on, OR `.github/instructions/*.instructions.md` with `applyTo` globs matching your folder structure — the latter is the more deterministic choice.

## Recommendations

**Stage 1 — Establish the minimal file (do now).**
- Write/trim AGENTS.md to a command-first core: one orientation paragraph + exact commands + safety boundaries (NEVER/ASK/ALWAYS) + pointers to detail docs. Target under ~150 lines; aim lower.
- Delete anything a linter/formatter/type-checker already enforces. Run the audit: for each line ask "what command proves this was done correctly?" If a tool enforces it, cut it.
- If you used `/init`, treat its output as a discard pile of what the agent can already find; keep only the non-obvious.

**Stage 2 — Wire the harness (where your ADR system pays off).**
- Project durable ADR decisions into: (a) lint/format configs, (b) custom lint rules / AST checks for architectural boundaries, (c) golden files *referenced* (not described) from AGENTS.md, (d) pre-commit + PostToolUse hooks, (e) CI gates.
- For every recurring agent mistake, add a mechanical check and *remove* the corresponding prose. Fastest layer wins.
- Keep a short "why + pointer" line in AGENTS.md for each enforced rule so the agent makes good edge-case decisions, but let the tool be the source of truth.

**Stage 3 — Interop & maintenance.**
- Make AGENTS.md canonical. Add a one-line `CLAUDE.md` with `@AGENTS.md`. In VS Code, enable `chat.useAgentsMdFile` (and `chat.useNestedAgentsMdFiles` for monorepos). Don't duplicate content between AGENTS.md and copilot-instructions.md.
- Use glob-scoped `.instructions.md` with `applyTo` for path-specific rules (more deterministic than nested AGENTS.md in VS Code).
- Add an AGENTS.md linter (AgentLint / agents-lint) to CI to catch stale commands/paths and missing enforcement. Review the file on a cadence and after major stack changes.

**Benchmarks/thresholds that would change these recommendations:**
- Agent ignores rules you care about → the file is likely over-budget; cut it and move rules to hooks.
- Compliance degrades late in long sessions → not a file problem (per the factorial study); use subagents/fresh context, not more prose.
- A rule is violated repeatedly despite being in prose → promote it up the enforcement hierarchy (hook/lint/CI).
- Tempted to add an overview/directory map → the causal evidence says it won't speed file discovery; skip it unless the repo structure would genuinely surprise someone who knows the framework.

## Caveats
- **Evidence is young and partly forward-dated.** The strongest causal study (arXiv:2602.11988) is a very recent preprint referencing GPT-5.x models; numbers may shift. The efficiency study (arXiv:2601.20404) did not measure correctness, and its gains were partly outlier-driven (mean vs. median divergence).
- **The "~150–200 instruction budget" and "under 60 lines" figures are practitioner heuristics,** not controlled findings; the factorial study found file size didn't affect adherence. Use them as directional guidance, not hard thresholds.
- **Vendor evals (Vercel) are single-framework and self-interested;** directional only.
- **Percentage-improvement marketing claims should be treated skeptically** and traced to primary sources — several "X% faster" headlines repackage the same efficiency study.
- **Tool behavior changes fast.** Native AGENTS.md support, setting names, and precedence rules shifted repeatedly through 2025–2026; verify `chat.useAgentsMdFile`, nested-file behavior, and Copilot/Claude precedence against current release notes before relying on them.
- **AGENTS.md is soft context, never enforcement** — the load-bearing caveat. Anything that must hold has to be mechanically enforced (lint, hook, CI, permissions), which is precisely why the ADR-projection-plus-harness architecture is the right one.