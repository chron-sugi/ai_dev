"""Frontmatter parser tests: real-corpus round-trip and fail-loud validation."""

from pathlib import Path

import pytest

from app.projection.frontmatter import AdrRecord, FrontmatterError, parse_adr

ADR_DIR = Path("docs/adrs")


def _write_adr(tmp_path: Path, body: str) -> Path:
    """Write a synthetic ADR file and return its path."""

    path = tmp_path / "adr-9999-synthetic.md"
    path.write_text(body, encoding="utf-8")
    return path


def test_round_trips_entire_real_corpus() -> None:
    """Every committed ADR parses without error into a validated record."""

    paths = sorted(ADR_DIR.glob("adr-*.md"))
    assert len(paths) >= 21
    records = [parse_adr(path) for path in paths]
    for record in records:
        assert isinstance(record, AdrRecord)
        assert record.id.startswith("ADR-")
        assert record.rule
        assert record.scope


def test_adr_0001_path_list_projection_normalizes_to_channels() -> None:
    """ADR-0001's legacy path-list projection maps to instructions + lint."""

    record = parse_adr(ADR_DIR / "adr-0001-python-docstring-policy.md")
    assert record.projection == ("instructions", "lint")


def test_projection_none_yields_empty_channels() -> None:
    """A ``projection: none`` record carries no channels and is never projected."""

    record = parse_adr(ADR_DIR / "adr-0014-research-md-enforcement-layers.md")
    assert record.projection == ()


def test_comma_joined_scope_splits_into_globs() -> None:
    """A comma-joined scope string normalises to one glob per token."""

    record = parse_adr(ADR_DIR / "adr-0008-justfile-is-the-single-pipeline-definition.md")
    assert record.scope == ("justfile", ".github/workflows/**", "scripts/**")


def test_missing_rule_raises_with_filename(tmp_path: Path) -> None:
    """Omitting the rule key fails loudly and names the file."""

    path = _write_adr(
        tmp_path,
        "---\nid: ADR-9999\ntitle: T\nstatus: proposed\ndomain: d\n"
        "projection: instructions\nscope: docs/**\n---\nbody\n",
    )
    with pytest.raises(FrontmatterError, match=path.name):
        parse_adr(path)


def test_non_kebab_domain_raises(tmp_path: Path) -> None:
    """A domain outside kebab-case is an authoring error."""

    path = _write_adr(
        tmp_path,
        "---\nid: ADR-9999\ntitle: T\nstatus: proposed\ndomain: Not_Kebab\n"
        "projection: instructions\nscope: docs/**\nrule: \"r\"\n---\n",
    )
    with pytest.raises(FrontmatterError, match="kebab-case"):
        parse_adr(path)


def test_unknown_status_raises(tmp_path: Path) -> None:
    """A status outside the recognised lifecycle set is an authoring error."""

    path = _write_adr(
        tmp_path,
        "---\nid: ADR-9999\ntitle: T\nstatus: draft\ndomain: d\n"
        "projection: instructions\nscope: docs/**\nrule: \"r\"\n---\n",
    )
    with pytest.raises(FrontmatterError, match="invalid status"):
        parse_adr(path)


def test_unknown_key_raises(tmp_path: Path) -> None:
    """Any frontmatter key outside the schema is an authoring error, not ignored."""

    path = _write_adr(
        tmp_path,
        "---\nid: ADR-9999\ntitle: T\nstatus: proposed\ndomain: d\nowner: me\n"
        "projection: instructions\nscope: docs/**\nrule: \"r\"\n---\n",
    )
    with pytest.raises(FrontmatterError, match="unknown frontmatter key"):
        parse_adr(path)


def test_unmappable_projection_path_raises(tmp_path: Path) -> None:
    """A legacy path entry with no deterministic channel mapping fails loudly."""

    path = _write_adr(
        tmp_path,
        "---\nid: ADR-9999\ntitle: T\nstatus: proposed\ndomain: d\n"
        "projection:\n  - some/random/file.txt\nscope: docs/**\nrule: \"r\"\n---\n",
    )
    with pytest.raises(FrontmatterError, match="unmappable projection entry"):
        parse_adr(path)
