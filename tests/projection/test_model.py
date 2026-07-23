"""Clustering tests: status filtering, universal split, exclusions, duplicates."""

from pathlib import Path

import pytest

from app.projection.frontmatter import AdrRecord, FrontmatterError
from app.projection.model import cluster, load_corpus


def _record(
    adr_id: str,
    *,
    domain: str = "demo",
    status: str = "accepted",
    scope: tuple[str, ...] = ("docs/**",),
    projection: tuple[str, ...] = ("instructions",),
) -> AdrRecord:
    """Build a synthetic in-memory record with sensible defaults."""

    return AdrRecord(
        id=adr_id,
        title=f"Title {adr_id}",
        status=status,
        date="2026-01-01",
        domain=domain,
        scope=scope,
        rule=f"Rule from {adr_id}.",
        projection=projection,
        path=Path(f"docs/adrs/{adr_id.lower()}.md"),
    )


def test_clusters_by_domain_sorted_by_id() -> None:
    """Records land in their declared domain, ordered by ADR id."""

    clustered = cluster(
        [
            _record("ADR-0002", domain="beta"),
            _record("ADR-0001", domain="beta"),
            _record("ADR-0003", domain="alpha"),
        ]
    )
    assert sorted(clustered.domains) == ["alpha", "beta"]
    assert [r.id for r in clustered.domains["beta"]] == ["ADR-0001", "ADR-0002"]


def test_superseded_and_deprecated_are_excluded() -> None:
    """Retired lifecycle states never reach any output cluster."""

    clustered = cluster(
        [
            _record("ADR-0001", status="superseded"),
            _record("ADR-0002", status="deprecated"),
            _record("ADR-0003", status="proposed"),
        ]
    )
    assert [r.id for r in clustered.domains["demo"]] == ["ADR-0003"]


def test_non_instructions_channels_are_excluded() -> None:
    """Only records carrying the instructions channel project to these surfaces."""

    clustered = cluster(
        [
            _record("ADR-0001", projection=("lint",)),
            _record("ADR-0002", projection=()),
            _record("ADR-0003", projection=("instructions", "lint")),
        ]
    )
    assert [r.id for r in clustered.domains["demo"]] == ["ADR-0003"]


def test_repo_wide_scope_splits_to_universal() -> None:
    """Scope tokens repo / ** / **/* route the rule to the universal surface."""

    clustered = cluster(
        [
            _record("ADR-0001", scope=("repo",)),
            _record("ADR-0002", scope=("**",)),
            _record("ADR-0003", scope=("docs/**",)),
        ]
    )
    assert [r.id for r in clustered.universal] == ["ADR-0001", "ADR-0002"]
    assert [r.id for r in clustered.domains["demo"]] == ["ADR-0003"]


def test_research_md_scope_is_excluded_per_adr_0014() -> None:
    """A RESEARCH.md glob never reaches output; the exclusion carries its reason."""

    clustered = cluster([_record("ADR-0001", scope=("**/RESEARCH.md",))])
    assert clustered.domains == {}
    assert clustered.universal == []
    [(record, reason)] = clustered.excluded
    assert record.id == "ADR-0001"
    assert "ADR-0014" in reason


def test_duplicate_adr_id_fails(tmp_path: Path) -> None:
    """Two files claiming one ADR id abort the load with both names."""

    body = (
        "---\nid: ADR-0001\ntitle: T\nstatus: accepted\ndomain: d\n"
        "projection: instructions\nscope: docs/**\nrule: \"r\"\n---\n"
    )
    (tmp_path / "adr-0001-a.md").write_text(body, encoding="utf-8")
    (tmp_path / "adr-0001-b.md").write_text(body, encoding="utf-8")
    with pytest.raises(FrontmatterError, match="duplicate ADR id"):
        load_corpus(tmp_path)


def test_load_corpus_reads_real_repo() -> None:
    """The live corpus loads and clusters without error."""

    records = load_corpus(Path("docs/adrs"))
    clustered = cluster(records)
    assert "adr-pipeline" in clustered.domains
    assert clustered.universal
