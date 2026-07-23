"""Emitter tests: idempotency, sentinel merge, notice-gated sweep, drift check."""

from pathlib import Path

import pytest

from app.projection.emit import (
    EmitError,
    apply,
    check,
    merge_copilot_shared,
)
from app.projection.frontmatter import AdrRecord
from app.projection.model import ClusteredCorpus
from app.projection.render import GENERATED_NOTICE, SENTINEL_BEGIN, SENTINEL_END


def _record(adr_id: str, *, domain: str = "demo", scope: tuple[str, ...] = ("docs/**",)) -> AdrRecord:
    """Build a synthetic record for emitter fixtures."""

    return AdrRecord(
        id=adr_id,
        title=f"Title {adr_id}",
        status="accepted",
        date="2026-01-01",
        domain=domain,
        scope=scope,
        rule=f"Rule from {adr_id}.",
        projection=("instructions",),
        path=Path(f"docs/adrs/{adr_id.lower()}.md"),
    )


def _corpus() -> ClusteredCorpus:
    """One domain plus one universal rule — enough to hit every target kind."""

    return ClusteredCorpus(
        domains={"demo": [_record("ADR-0001")]},
        universal=[_record("ADR-0002", scope=("repo",))],
    )


def test_create_when_absent(tmp_path: Path) -> None:
    """A fresh root gains all four targets."""

    result = apply(tmp_path, _corpus())
    assert sorted(result.written) == [
        ".claude/rules/demo.md",
        ".claude/rules/universal.md",
        ".github/copilot-instructions.md",
        ".github/instructions/demo.instructions.md",
    ]
    assert result.deleted == []


def test_second_run_is_byte_identical_noop(tmp_path: Path) -> None:
    """Re-applying the same corpus writes nothing and changes no bytes."""

    apply(tmp_path, _corpus())
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = apply(tmp_path, _corpus())
    assert result.written == [] and result.deleted == []
    assert len(result.unchanged) == 4
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def test_update_in_place_when_rule_changes(tmp_path: Path) -> None:
    """Editing a rule rewrites both existing per-domain files in place."""

    apply(tmp_path, _corpus())
    changed = _corpus()
    changed.domains["demo"] = [
        AdrRecord(
            id="ADR-0001",
            title="Title ADR-0001",
            status="accepted",
            date="2026-01-01",
            domain="demo",
            scope=("docs/**",),
            rule="Amended rule.",
            projection=("instructions",),
            path=Path("docs/adrs/adr-0001.md"),
        )
    ]
    result = apply(tmp_path, changed)
    assert sorted(result.written) == [
        ".claude/rules/demo.md",
        ".github/instructions/demo.instructions.md",
    ]
    assert "Amended rule." in (tmp_path / ".claude/rules/demo.md").read_text(encoding="utf-8")


def test_hand_authored_file_survives_sweep(tmp_path: Path) -> None:
    """A notice-less file in an owned directory is never deleted."""

    manual = tmp_path / ".github/instructions/manual.instructions.md"
    manual.parent.mkdir(parents=True)
    manual.write_text("hand-authored\n", encoding="utf-8")
    result = apply(tmp_path, _corpus())
    assert manual.exists()
    assert result.deleted == []


def test_orphaned_generated_file_is_deleted(tmp_path: Path) -> None:
    """Dropping a domain's last record deletes both its generated files only."""

    apply(tmp_path, _corpus())
    emptied = ClusteredCorpus(domains={}, universal=_corpus().universal)
    result = apply(tmp_path, emptied)
    assert sorted(result.deleted) == [
        ".claude/rules/demo.md",
        ".github/instructions/demo.instructions.md",
    ]
    assert (tmp_path / ".claude/rules/universal.md").exists()


def test_sentinel_merge_preserves_hand_authored_prose(tmp_path: Path) -> None:
    """Prose outside the sentinel region survives regeneration byte-for-byte."""

    shared = tmp_path / ".github/copilot-instructions.md"
    shared.parent.mkdir(parents=True)
    shared.write_text(
        f"# My project\n\nintro prose\n\n{SENTINEL_BEGIN}\nstale\n{SENTINEL_END}\n\noutro prose\n",
        encoding="utf-8",
    )
    apply(tmp_path, _corpus())
    text = shared.read_text(encoding="utf-8")
    assert text.startswith("# My project\n\nintro prose\n")
    assert text.endswith("\noutro prose\n")
    assert "stale" not in text
    assert "Rule from ADR-0002." in text


def test_no_universal_rules_leaves_sentinel_less_shared_file_untouched(tmp_path: Path) -> None:
    """With no universal rules, a hand-authored shared file gains no sentinel pair."""

    shared = tmp_path / ".github/copilot-instructions.md"
    shared.parent.mkdir(parents=True)
    shared.write_text("# My project\n\nhand-authored only\n", encoding="utf-8")
    corpus = ClusteredCorpus(domains={"demo": [_record("ADR-0001")]}, universal=[])
    assert merge_copilot_shared(tmp_path, corpus) is None
    apply(tmp_path, corpus)
    assert shared.read_text(encoding="utf-8") == "# My project\n\nhand-authored only\n"


def test_no_universal_rules_empties_existing_sentinel_region(tmp_path: Path) -> None:
    """With no universal rules, an existing sentinel region is emptied, prose kept."""

    shared = tmp_path / ".github/copilot-instructions.md"
    shared.parent.mkdir(parents=True)
    shared.write_text(
        f"prose\n\n{SENTINEL_BEGIN}\nstale\n{SENTINEL_END}\n", encoding="utf-8"
    )
    corpus = ClusteredCorpus(domains={"demo": [_record("ADR-0001")]}, universal=[])
    apply(tmp_path, corpus)
    text = shared.read_text(encoding="utf-8")
    assert "stale" not in text
    assert text.startswith("prose\n")
    assert SENTINEL_BEGIN in text and SENTINEL_END in text


def test_single_sentinel_is_refused(tmp_path: Path) -> None:
    """A damaged sentinel region aborts rather than risking prose loss."""

    shared = tmp_path / ".github/copilot-instructions.md"
    shared.parent.mkdir(parents=True)
    shared.write_text(f"prose\n{SENTINEL_BEGIN}\nblock\n", encoding="utf-8")
    with pytest.raises(EmitError, match="sentinel"):
        merge_copilot_shared(tmp_path, _corpus())


def test_check_detects_hand_edit_and_orphan(tmp_path: Path) -> None:
    """Check mode reports edited bytes and orphaned generated files, writes nothing."""

    apply(tmp_path, _corpus())
    target = tmp_path / ".claude/rules/demo.md"
    target.write_bytes(target.read_bytes() + b"sneaky edit\n")
    orphan = tmp_path / ".claude/rules/gone.md"
    orphan.write_text(f"{GENERATED_NOTICE}\nold\n", encoding="utf-8")
    result = check(tmp_path, _corpus())
    assert ".claude/rules/demo.md" in result.drift
    assert ".claude/rules/gone.md" in result.drift
    assert b"sneaky edit" in target.read_bytes()
    assert orphan.exists()


def test_check_is_clean_after_apply(tmp_path: Path) -> None:
    """A fresh apply always passes its own drift check."""

    apply(tmp_path, _corpus())
    result = check(tmp_path, _corpus())
    assert result.drift == []
    assert len(result.unchanged) == 4
