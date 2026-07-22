---
id: ADR-0012
title: Python is the sole scripting language for framework tooling
status: proposed
date: 2026-07-22
domain: toolchain
scope: repo
projection: instructions
rule: "Implement all framework scripting — pipeline implementations, hooks, and guards — as stdlib-only Python 3; never add Node/.mjs scripts or a PowerShell peer implementation."
---

# Python is the sole scripting language for framework tooling

## Context

The pipeline was designed around two interchangeable implementations — Node and PowerShell — producing byte-identical output, with the drift guard comparing bytes across them (prose in ADR-0006 and ADR-0008; invariant in the adr-pipeline concept doc). That language choice was never recorded as a decision of its own: it exists only in the reasoning sections of other ADRs and in the concept doc.

At decision time, no `.mjs` file and no `scripts/` directory exist in the repository — the Node implementation is prose, not code. The switch is therefore free of migration cost now and only gets more expensive later. Python is already a required runtime in this stack (ADR-0001's tooling, `install_claude_assets.py`), so standardizing on it adds no new runtime dependency, whereas keeping Node would.

The immediate forcing function is the RESEARCH.md guard hook (ADR-0014): hooks must run identically under Claude Code and VS Code Copilot on Windows, with no dependency installation step.

## Decision

Python 3, standard library only, is the single implementation language for all framework scripting: the projection pipeline, lint tooling, PreToolUse/PostToolUse hooks, and guards. There is exactly one implementation of the pipeline, not two.

- **Stdlib-only** is a hard constraint for anything invoked as a hook: hooks must run from a bare interpreter with no venv activation or `pip install` step, because they fire in contexts (agent tool calls) where no environment setup has happened.
- **The dual-implementation invariant is retired.** Byte-determinism remains a contract, but it is now enforced by the drift guard against the one Python implementation across environments (local vs CI), not by cross-checking two implementations against each other.
- **Interpreter invocation is pinned per surface:** justfile recipes and hook registrations invoke Python explicitly (`py -3` on Windows launcher surfaces, `python3` on POSIX CI) rather than relying on an unqualified `python` on PATH. A hook whose interpreter resolution fails exits without firing — a silent fail-open — so the invocation form is part of the contract, not a style choice.

## Rejected alternatives

- **Node + PowerShell as originally planned** — two implementations held in byte-identical lockstep double the maintenance cost of every pipeline change, for a determinism guarantee the drift guard already provides more cheaply. With zero Node code committed, the sunk cost being preserved was nil.
- **Python + PowerShell (keep the peer model, swap the peer)** — preserves the lockstep cost without its original motivation. The dual-implementation design hedged against a missing runtime on Windows; Python is now a required runtime everywhere, so the hedge insures against nothing.
- **PowerShell only** — single-implementation benefits, but weaker cross-platform story for CI parity, and its ecosystem for linting and testing the pipeline's own code is thinner than Python's.
- **Per-tool language choice (no rule)** — the default that produces a polyglot `scripts/` directory one convenience decision at a time; each language added is another runtime CI and contributors must carry.

## Consequences

- The adr-pipeline concept doc's invariant changes: determinism is now a property the single Python implementation must uphold (locale, line endings, directory enumeration order, dict/set iteration order are the hazards), verified by the byte-comparing drift guard — not a cross-implementation equivalence check. ADR-0008 is unaffected: its rule concerns the justfile as the single command surface, which survives unchanged; Node appears only in its rationale.
- The RESEARCH.md guard (ADR-0014) ships as `scripts/hooks/guard_research.py`; the previously prototyped `guard-research.mjs` and its test results are void, and the Python port must be re-verified against the same 14-case matrix.
- The deterministic syntax gate for scripts becomes `python -m py_compile` (or ruff) in place of `node --check`.
- Any future need for a second implementation language is a new ADR superseding this one, not an incremental exception.
