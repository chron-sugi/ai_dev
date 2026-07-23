"""Golden-string renderer tests pinning both frontmatter dialects."""

from pathlib import Path

from app.projection.frontmatter import AdrRecord
from app.projection.render import (
    GENERATED_NOTICE,
    glob_union,
    render_claude_domain,
    render_claude_universal,
    render_copilot_domain,
    render_copilot_universal_block,
)


def _record(adr_id: str, rule: str, scope: tuple[str, ...]) -> AdrRecord:
    """Build a synthetic record for one fixture domain."""

    return AdrRecord(
        id=adr_id,
        title=f"Title {adr_id}",
        status="accepted",
        date="2026-01-01",
        domain="fixture",
        scope=scope,
        rule=rule,
        projection=("instructions",),
        path=Path(f"docs/adrs/{adr_id.lower()}.md"),
    )


FIXTURE = [
    _record("ADR-0001", "Always frobnicate.", ("docs/**", "justfile")),
    _record("ADR-0002", "Never defrobnicate.", ("docs/**", ".velocai/**")),
]

_EXPECTED_BODY = (
    f"{GENERATED_NOTICE}\n"
    "\n"
    "# fixture rules\n"
    "\n"
    "Rules below are projected from ADRs. Before modifying in-scope files, read "
    "the cited ADR in `docs/adrs/`; do not re-litigate accepted decisions.\n"
    "\n"
    "- Always frobnicate. (ADR-0001)\n"
    "- Never defrobnicate. (ADR-0002)\n"
)


def test_glob_union_is_sorted_and_deduplicated() -> None:
    """The union collapses duplicates and sorts deterministically."""

    assert glob_union(FIXTURE) == [".velocai/**", "docs/**", "justfile"]


def test_copilot_domain_golden() -> None:
    """Copilot dialect: applyTo comma-joined string frontmatter, cited bullets."""

    expected = '---\napplyTo: ".velocai/**,docs/**,justfile"\n---\n' + _EXPECTED_BODY
    assert render_copilot_domain("fixture", FIXTURE) == expected


def test_claude_domain_golden() -> None:
    """Claude dialect: paths YAML-list frontmatter, identical generated body."""

    expected = (
        "---\n"
        "paths:\n"
        '  - ".velocai/**"\n'
        '  - "docs/**"\n'
        '  - "justfile"\n'
        "---\n" + _EXPECTED_BODY
    )
    assert render_claude_domain("fixture", FIXTURE) == expected


def test_dialects_share_identical_body_and_glob_set() -> None:
    """The two dialects differ only in frontmatter; body and glob set match."""

    copilot = render_copilot_domain("fixture", FIXTURE)
    claude = render_claude_domain("fixture", FIXTURE)
    assert copilot.split("---\n")[2] == claude.split("---\n")[2]
    apply_to = copilot.split('applyTo: "')[1].split('"')[0].split(",")
    paths = [line.strip()[3:-1] for line in claude.splitlines() if line.startswith('  - "')]
    assert apply_to == paths == glob_union(FIXTURE)


def test_claude_universal_has_no_frontmatter() -> None:
    """The universal Claude rule file starts with the notice, never a fence."""

    rendered = render_claude_universal(FIXTURE)
    assert rendered.startswith(GENERATED_NOTICE)
    assert "paths:" not in rendered


def test_copilot_universal_block_is_sentinel_delimited() -> None:
    """The shared-surface block opens and closes with the exact sentinels."""

    rendered = render_copilot_universal_block(FIXTURE)
    assert rendered.startswith("<!-- velocai:begin generated -->\n")
    assert rendered.endswith("<!-- velocai:end generated -->\n")
    assert GENERATED_NOTICE in rendered
