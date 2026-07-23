#!/usr/bin/env python3
"""Install Claude Code assets from this repo into the user's ~/.claude directory.

Copies:
  src/assets/agents/*  -> ~/.claude/agents/
  src/assets/prompts/* -> ~/.claude/commands/

Existing files with the same name are overwritten. Standalone — no
third-party dependencies; run from anywhere:

    python install_claude_assets.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

MAPPINGS = [
    (REPO_ROOT / "src" / "assets" / "agents", Path.home() / ".claude" / "agents"),
    (REPO_ROOT / "src" / "assets" / "prompts", Path.home() / ".claude" / "commands"),
]


def copy_tree(src: Path, dest: Path) -> int:
    """Copy every file in ``src`` into ``dest``, returning the count copied."""

    if not src.is_dir():
        sys.stderr.write(f"  SKIP: source not found: {src}\n")
        return 0
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in sorted(src.iterdir()):
        if not item.is_file():
            continue
        target = dest / item.name
        shutil.copy2(item, target)
        sys.stdout.write(f"  {item.name} -> {target}\n")
        count += 1
    return count


def main() -> int:
    """Install every mapped asset directory; exit non-zero if nothing copied."""

    total = 0
    for src, dest in MAPPINGS:
        sys.stdout.write(f"Copying {src} -> {dest}\n")
        total += copy_tree(src, dest)
    sys.stdout.write(f"Done. {total} file(s) copied.\n")
    return 0 if total > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
