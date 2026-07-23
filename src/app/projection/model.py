"""Corpus loading and domain clustering for the projection pipeline.

Turns the validated ADR records into the single internal model both renderers
consume: projectable records clustered by declared domain (ADR-0007), with
universal (repo-wide) rules split out for the always-on surfaces. Ordering is
stable everywhere (paths sorted, records sorted by ADR id) because projection
must be a pure, byte-deterministic function of the corpus (ADR-0006).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.projection.frontmatter import AdrRecord, FrontmatterError, parse_adr

#: Lifecycle states whose rules are delivered to agents (plan OQ-1: accepted
#: and proposed project; superseded and deprecated are retired from output).
INCLUDE_STATUSES = frozenset({"accepted", "proposed"})

#: Scope tokens that mean "repo-wide": these rules go to the universal
#: always-on surfaces instead of a path-scoped domain file.
_UNIVERSAL_SCOPES = frozenset({"repo", "**", "**/*"})

#: File name whose globs may never reach any projection output or instruction
#: glob (ADR-0014's rule binds the pipeline itself).
_RESEARCH_BASENAME = "RESEARCH.md"


@dataclass(frozen=True)
class ClusteredCorpus:
    """The projection input model: domain clusters plus split-out rule sets.

    ``domains`` maps kebab-case domain name to its member records sorted by
    ADR id; ``universal`` holds repo-wide records; ``excluded`` holds records
    the pipeline refuses to project with the reason, for CLI reporting.
    """

    domains: dict[str, list[AdrRecord]] = field(default_factory=dict)
    universal: list[AdrRecord] = field(default_factory=list)
    excluded: list[tuple[AdrRecord, str]] = field(default_factory=list)


def load_corpus(adr_dir: Path) -> list[AdrRecord]:
    """Parse every ``adr-*.md`` under ``adr_dir``, sorted by path, fail-loud.

    Raises:
        FrontmatterError: if any record is malformed or two records share an id.
    """

    records = [parse_adr(path) for path in sorted(adr_dir.glob("adr-*.md"))]
    seen: dict[str, Path] = {}
    for record in records:
        if record.id in seen:
            raise FrontmatterError(
                f"duplicate ADR id {record.id}: {seen[record.id].name} and {record.path.name}"
            )
        seen[record.id] = record.path
    return sorted(records, key=lambda record: record.id)


def _is_universal(record: AdrRecord) -> bool:
    """True when any scope token declares the rule repo-wide."""

    return any(token in _UNIVERSAL_SCOPES for token in record.scope)


def _references_research_md(record: AdrRecord) -> bool:
    """True when any scope glob targets the human-only RESEARCH.md class."""

    return any(token.rsplit("/", 1)[-1] == _RESEARCH_BASENAME for token in record.scope)


def cluster(records: list[AdrRecord]) -> ClusteredCorpus:
    """Filter to projectable records and cluster them by declared domain.

    A record projects when its status is in :data:`INCLUDE_STATUSES` and the
    ``instructions`` channel is among its projection channels. Records whose
    scope globs reference RESEARCH.md are excluded regardless: ADR-0014 forbids
    RESEARCH.md in any projection output or instruction glob, and that rule
    binds the pipeline mechanically, not just corpus authors.
    """

    clustered = ClusteredCorpus()
    for record in records:
        if record.status not in INCLUDE_STATUSES or "instructions" not in record.projection:
            continue
        if _references_research_md(record):
            clustered.excluded.append(
                (record, "scope references RESEARCH.md; ADR-0014 forbids it in projection output")
            )
            continue
        if _is_universal(record):
            clustered.universal.append(record)
        else:
            clustered.domains.setdefault(record.domain, []).append(record)
    clustered.universal.sort(key=lambda record: record.id)
    for members in clustered.domains.values():
        members.sort(key=lambda record: record.id)
    return clustered
