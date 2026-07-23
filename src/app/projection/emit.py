"""Idempotent emission: desired-outputs map, sentinel merge, notice-gated sweep.

The whole write side reduces to one shape (ADR-0006): derive ``{relative path:
rendered content}`` for every target, write only where bytes differ, delete
only notice-bearing files that fell out of the map, and let ``--check`` be a
pure recompute-and-diff of the same map. Files are read and written as raw
UTF-8 bytes with ``\\n`` newlines so platform newline translation can never
break byte determinism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.projection.model import ClusteredCorpus
from app.projection.render import (
    GENERATED_NOTICE,
    SENTINEL_BEGIN,
    SENTINEL_END,
    render_claude_domain,
    render_claude_universal,
    render_copilot_domain,
    render_copilot_universal_block,
)

#: Directories the pipeline fully owns: any notice-bearing file here that is
#: not in the desired-outputs map is an orphan and is deleted on write runs.
SWEEP_DIRS = (".github/instructions", ".claude/rules")

#: The shared surface the pipeline only partially owns via the sentinel region.
COPILOT_SHARED_SURFACE = ".github/copilot-instructions.md"


class EmitError(ValueError):
    """A target file is in a state the emitter refuses to touch (sentinel damage)."""


@dataclass
class EmitResult:
    """Outcome of one apply or check run, in relative-posix-path terms."""

    written: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    drift: list[str] = field(default_factory=list)


def build_outputs(clustered: ClusteredCorpus) -> dict[str, str]:
    """Derive the desired-outputs map for every fully generated target.

    The shared Copilot surface is excluded here — its desired content depends
    on the hand-authored prose already on disk, so it is merged per run by
    :func:`merge_copilot_shared`.
    """

    outputs: dict[str, str] = {}
    for domain, records in sorted(clustered.domains.items()):
        outputs[f".github/instructions/{domain}.instructions.md"] = render_copilot_domain(
            domain, records
        )
        outputs[f".claude/rules/{domain}.md"] = render_claude_domain(domain, records)
    if clustered.universal:
        outputs[".claude/rules/universal.md"] = render_claude_universal(clustered.universal)
    return outputs


def merge_copilot_shared(root: Path, clustered: ClusteredCorpus) -> str | None:
    """Compute the desired full content of `.github/copilot-instructions.md`.

    Replaces the sentinel-delimited region, preserving hand-authored prose
    outside it; creates the file as just the block when absent. Returns None
    when there are no universal rules and either no file exists or the
    existing file carries no sentinel region — a fully hand-authored file is
    left untouched rather than gaining an empty sentinel pair.

    Raises:
        EmitError: if exactly one sentinel is present — the region is damaged
            and regenerating could destroy hand-authored content.
    """

    target = root / COPILOT_SHARED_SURFACE
    block = render_copilot_universal_block(clustered.universal) if clustered.universal else None
    if not target.exists():
        return block
    text = target.read_bytes().decode("utf-8")
    lines = text.split("\n")
    begin_indices = [i for i, line in enumerate(lines) if line.strip() == SENTINEL_BEGIN]
    end_indices = [i for i, line in enumerate(lines) if line.strip() == SENTINEL_END]
    if len(begin_indices) != len(end_indices) or len(begin_indices) > 1:
        raise EmitError(
            f"{COPILOT_SHARED_SURFACE}: sentinel pair is damaged "
            f"({len(begin_indices)} begin / {len(end_indices)} end markers)"
        )
    if block is None:
        if not begin_indices:
            return None
        block = f"{SENTINEL_BEGIN}\n{SENTINEL_END}\n"
    block_lines = block.rstrip("\n").split("\n")
    if not begin_indices:
        merged = text.rstrip("\n").split("\n") + [""] + block_lines
    else:
        begin, end = begin_indices[0], end_indices[0]
        if end < begin:
            raise EmitError(f"{COPILOT_SHARED_SURFACE}: end sentinel precedes begin sentinel")
        merged = lines[:begin] + block_lines + lines[end + 1 :]
    result = "\n".join(merged)
    return result if result.endswith("\n") else result + "\n"


def _desired_map(root: Path, clustered: ClusteredCorpus) -> dict[str, str]:
    """Full desired state: generated targets plus the merged shared surface."""

    outputs = build_outputs(clustered)
    shared = merge_copilot_shared(root, clustered)
    if shared is not None:
        outputs[COPILOT_SHARED_SURFACE] = shared
    return outputs


def _orphans(root: Path, outputs: dict[str, str]) -> list[str]:
    """Notice-bearing files in the owned directories that left the desired map.

    Files without the exact generated notice are hand-authored and are never
    touched (ADR-0006 grants deletion authority over notice-bearing files only).
    """

    found: list[str] = []
    for sweep_dir in SWEEP_DIRS:
        directory = root / sweep_dir
        if not directory.is_dir():
            continue
        for candidate in sorted(directory.iterdir()):
            if not candidate.is_file():
                continue
            rel = f"{sweep_dir}/{candidate.name}"
            if rel in outputs:
                continue
            if GENERATED_NOTICE in candidate.read_bytes().decode("utf-8", errors="replace"):
                found.append(rel)
    return found


def apply(root: Path, clustered: ClusteredCorpus) -> EmitResult:
    """Write the desired state: create, update in place, sweep orphans."""

    outputs = _desired_map(root, clustered)
    result = EmitResult()
    for rel in sorted(outputs):
        target = root / rel
        desired = outputs[rel].encode("utf-8")
        if target.exists() and target.read_bytes() == desired:
            result.unchanged.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(desired)
        result.written.append(rel)
    for rel in _orphans(root, outputs):
        (root / rel).unlink()
        result.deleted.append(rel)
    return result


def check(root: Path, clustered: ClusteredCorpus) -> EmitResult:
    """Pure recompute-and-diff: report drift, write nothing.

    Drift is any target whose bytes differ from a fresh projection (or which
    is missing), plus any orphaned notice-bearing file awaiting deletion.
    """

    outputs = _desired_map(root, clustered)
    result = EmitResult()
    for rel in sorted(outputs):
        target = root / rel
        if target.exists() and target.read_bytes() == outputs[rel].encode("utf-8"):
            result.unchanged.append(rel)
        else:
            result.drift.append(rel)
    result.drift.extend(_orphans(root, outputs))
    return result
