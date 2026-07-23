"""ADR projection pipeline: compiles ADR frontmatter into tool-facing rule surfaces.

Reads ``docs/adrs/*.md`` frontmatter, clusters projectable rules by their
declared domain (ADR-0007), and emits per-domain instruction files for VS Code
Copilot (``.github/instructions/``) and Claude Code (``.claude/rules/``) plus a
universal always-on surface. Generation is deterministic and idempotent; the
drift guard (``--check``) recomputes and byte-compares (ADR-0006). Entry points
are the ``just project`` and ``just project-check`` recipes only (ADR-0008).
Stdlib-only by contract (ADR-0012).
"""
