"""CLI for the projection pipeline: ``py -3 -m app.projection [--check]``.

Never invoked directly — the only supported entry points are the ``just
project`` and ``just project-check`` recipes (ADR-0008). Output goes through
``sys.stdout``/``sys.stderr`` writes so the repo's no-print lint policy holds
for pipeline code too.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.projection.emit import EmitError, apply, check
from app.projection.frontmatter import FrontmatterError
from app.projection.model import cluster, load_corpus


def _summary(prefix: str, items: list[str]) -> str:
    """Format one count line, with the item list indented when non-empty."""

    lines = [f"{prefix}: {len(items)}"]
    lines.extend(f"  {item}" for item in items)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run projection (default) or the drift guard (``--check``).

    Returns:
        Process exit code: 0 on success or a clean check; 1 on drift or any
        corpus/emit error.
    """

    parser = argparse.ArgumentParser(
        prog="app.projection",
        description="Project ADR rules into tool-facing instruction surfaces.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute and diff against committed output; write nothing",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root containing docs/adrs/ (default: current directory)",
    )
    args = parser.parse_args(argv)

    try:
        records = load_corpus(args.root / "docs" / "adrs")
        clustered = cluster(records)
        projected = sum(len(members) for members in clustered.domains.values()) + len(
            clustered.universal
        )
        header = f"{len(records)} ADRs read, {projected} rules projected"
        for record, reason in clustered.excluded:
            header += f"\nexcluded {record.id}: {reason}"
        if args.check:
            result = check(args.root, clustered)
            sys.stdout.write(f"{header}\n{_summary('drift', result.drift)}\n")
            return 1 if result.drift else 0
        result = apply(args.root, clustered)
        sys.stdout.write(
            f"{header}\n"
            f"{_summary('written', result.written)}\n"
            f"{_summary('deleted', result.deleted)}\n"
            f"unchanged: {len(result.unchanged)}\n"
        )
        return 0
    except (FrontmatterError, EmitError) as error:
        sys.stderr.write(f"projection failed: {error}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
