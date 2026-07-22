---
id: ADR-0014
title: Layered enforcement of the RESEARCH.md human-only boundary
status: proposed
date: 2026-07-22
domain: research-docs
scope: ".claude/settings.json,.github/hooks/**,scripts/hooks/**"
projection: none
rule: "Deny agent access to **/RESEARCH.md via Claude Code permission deny rules plus the shared PreToolUse guard scripts/hooks/guard_research.py; never add RESEARCH.md to any projection output or instruction glob."
---

# Layered enforcement of the RESEARCH.md human-only boundary

## Context

ADR-0013 declares files named exactly `RESEARCH.md` human-only. Prose alone does not enforce that: the class exists specifically because its content is a context-poisoning hazard, and the agents to be kept out are the ones that never loaded the instruction. Enforcement must be mechanical and must cover both active runtimes — Claude Code and VS Code Copilot — which have different enforcement vocabularies (Claude Code has permission deny rules; Copilot does not).

The threat model is **accidental context poisoning, not an adversary**. This single assumption drives most design choices below: fail-open error handling, pattern-matching rather than full shell parsing, and acceptance of residual gaps covered only by the prose banner.

This ADR is split from ADR-0013 deliberately, following the ADR-0002/ADR-0003 precedent (policy in one record, enforcement layering in a companion): the class decision is stable, while this mechanism rides a preview surface (VS Code hooks, shipped v1.110) and may be superseded independently.

## Decision

A passive precondition plus four active layers, strongest first. Write-path blocking (create/edit) is included deliberately, not incidentally — the file class is human-maintained.

**Precondition:** `RESEARCH.md` never appears in any projection output, instruction file, or `applyTo` glob. (This is why `projection: none` — see Consequences.)

1. **Claude Code permission deny rules** (strongest; Claude Code only): `Read(**/RESEARCH.md)`, `Edit(**/RESEARCH.md)`, `Write(**/RESEARCH.md)` in `.claude/settings.json` → `permissions.deny`.
2. **Shared PreToolUse hook** (both runtimes): `scripts/hooks/guard_research.py`, a stdlib-only Python 3 script per ADR-0012, exiting 2 with a stderr message on violation. Registered twice: `.claude/settings.json` → `hooks.PreToolUse` (with matcher) and `.github/hooks/research-guard.json` (Copilot/VS Code). VS Code also reads the Claude settings hook config directly; the dual registration is belt-and-braces. The script is **self-filtering by requirement, not choice**: VS Code currently ignores hook matcher values and fires hooks on every tool invocation.
3. **Copilot content exclusion** (optional; requires Business/Enterprise repo-admin access): exclude `**/RESEARCH.md` from all Copilot context, including inline completions — the one surface hooks do not govern. Nice-if-obtainable; not load-bearing.
4. **Prose banner** (weakest; backstop): the fixed first-line notice defined in ADR-0013. The only net for residual paths — content pasted into chat, terminal output the hook didn't parse, future runtimes without hooks.

### Guard script contract

- **Scans path-bearing keys and command strings only; never content fields** (`new_str`, `content`, `old_str`). An agent writing prose *about* this rule mentions "RESEARCH.md" and must not be blocked. Path keys cover both runtimes' vocabularies (`file_path`/`filePath`/`path`/`notebook_path`, array forms `files`/`paths`); command keys (`command`/`cmd`/`script`/`commands`) get a word-bounded match to catch `cat`/`grep`/`sed` invocations.
- **Case-insensitive matching** — Windows filesystems; `research.md` and `RESEARCH.md` cannot coexist there.
- **Fail-open on malformed or unknown input** (exit 0). The threat is accidental, the Claude Code deny rules remain as backstop, and fail-closed would let hook-payload format drift — a live risk on a preview surface — break all agent tool use.
- **Payload tolerance:** accepts both `hookEventName`/`tool_input` (Claude Code, snake_case) and `preToolUse`/`toolInput`/`filePath` (Copilot CLI, camelCase); a missing event name is treated as PreToolUse (VS Code payload variance observed in the wild).
- **Exit-code contract shared across runtimes:** exit 2 = deny; stderr is surfaced to the model as the block reason. The stderr text redirects the agent to `docs/adrs/` — deliberate steering, not bare refusal.

## Rejected alternatives

- **Deny rules only** — covers Claude Code alone; VS Code Copilot has no deny-rule equivalent, so half the surface would rely on prose.
- **Hook only, no deny rules** — discards the strongest available mechanism on the runtime where it exists; the layers are cheap to hold simultaneously.
- **Fail-closed on malformed payloads** — turns payload-format drift on a preview surface into a total outage of agent tool use, to defend against a threat model (adversarial evasion) this ADR explicitly does not claim.
- **Scanning content fields as well as paths** — blocks agents from ever writing about the rule (including this ADR); the poisoning vector is file access, not the string.
- **Full shell parsing for Bash interception** — a losing game; pattern-matching common invocations plus the banner layer is the accepted posture.

## Known gaps (accepted)

- **Arbitrary Bash is not fully interceptable.** Constructed or obfuscated paths bypass the pattern match; layer 4 is the only net. Acceptable under the accidental-poisoning threat model.
- **VS Code hooks are Preview** (v1.110, Feb 2026). The matcher-ignoring behavior is documented current-state, not contract; behavior shifts here are the most likely trigger for superseding this ADR.
- **Copilot inline completions** are untouched by hooks; only layer 3 reaches them, and layer 3's feasibility (repo-admin access) is unconfirmed.

## Consequences

- **`projection: none` precedent.** Enforcement is fully mechanical, so per standing principle the rule is not restated in instruction files. This is the first live use of `none` (defined for "enforced outside the projection system or informational"); this ADR sets that precedent.
- The guard ships in Python per ADR-0012. The previously prototyped `guard-research.mjs` passed a 14-case matrix (deny on Read/Edit/Write/editFiles/bash-cat across both payload dialects; allow on CONCEPT.md, `MARKET_RESEARCH.md`, content-only mentions, unrelated bash, non-PreToolUse events, malformed JSON; Windows backslash paths and lowercase); the Python port must pass the same matrix before this ADR is accepted.
- Pre-acceptance verification items: (1) canary-fact probe — seed a RESEARCH.md with a distinctive false fact, confirm neither runtime can surface it via Read/Grep/Glob/file-search; (2) confirm whether Claude Code deny Read rules also gate Grep/Glob results or only direct Reads (determines how load-bearing the hook is); (3) confirm VS Code fires hooks from `.github/hooks/*.json` in the workplace build; (4) confirm the Copilot plan permits content-exclusion configuration (layer 3 feasibility).
- Hook scripts remain excluded from agent auto-approval per existing policy (ADR-0003 consequence), preventing self-modification of the enforcement layer.
- Future lint rule (deferred until drift observed): verify every RESEARCH.md carries the fixed banner line.
