"""End-to-end pipeline tests over a synthetic tmp repo, driven through the CLI."""

import ast
import sys
from pathlib import Path

from app.projection.__main__ import main

PROJECTION_SRC = Path("src/app/projection")


def _adr(adr_id: str, domain: str, scope: str, rule: str, status: str = "accepted") -> str:
    """Author one synthetic ADR file body."""

    return (
        f"---\nid: {adr_id}\ntitle: Title {adr_id}\nstatus: {status}\ndate: 2026-01-01\n"
        f"domain: {domain}\nprojection: instructions\nscope: {scope}\nrule: \"{rule}\"\n---\n\nBody.\n"
    )


def _seed_repo(tmp_path: Path) -> Path:
    """Create a synthetic repo: two domain ADRs plus one universal ADR."""

    adr_dir = tmp_path / "docs" / "adrs"
    adr_dir.mkdir(parents=True)
    (adr_dir / "adr-0001-a.md").write_text(
        _adr("ADR-0001", "alpha", "src/**", "Alpha rule."), encoding="utf-8"
    )
    (adr_dir / "adr-0002-b.md").write_text(
        _adr("ADR-0002", "beta", "docs/**", "Beta rule."), encoding="utf-8"
    )
    (adr_dir / "adr-0003-u.md").write_text(
        _adr("ADR-0003", "core", "repo", "Universal rule."), encoding="utf-8"
    )
    return tmp_path


def test_end_to_end_generate_update_delete(tmp_path: Path, capsys) -> None:
    """Full lifecycle: generate both trees, edit a rule, retire a domain."""

    root = _seed_repo(tmp_path)
    manual = root / ".github" / "instructions" / "manual.instructions.md"
    manual.parent.mkdir(parents=True)
    manual.write_text("hand-authored\n", encoding="utf-8")

    assert main(["--root", str(root)]) == 0
    for rel in (
        ".github/instructions/alpha.instructions.md",
        ".github/instructions/beta.instructions.md",
        ".claude/rules/alpha.md",
        ".claude/rules/beta.md",
        ".claude/rules/universal.md",
        ".github/copilot-instructions.md",
    ):
        assert (root / rel).exists(), rel
    assert main(["--root", str(root), "--check"]) == 0

    (root / "docs/adrs/adr-0001-a.md").write_text(
        _adr("ADR-0001", "alpha", "src/**", "Alpha rule v2."), encoding="utf-8"
    )
    assert main(["--root", str(root), "--check"]) == 1
    assert main(["--root", str(root)]) == 0
    for rel in (".github/instructions/alpha.instructions.md", ".claude/rules/alpha.md"):
        assert "Alpha rule v2." in (root / rel).read_text(encoding="utf-8")

    (root / "docs/adrs/adr-0002-b.md").write_text(
        _adr("ADR-0002", "beta", "docs/**", "Beta rule.", status="superseded"), encoding="utf-8"
    )
    assert main(["--root", str(root)]) == 0
    assert not (root / ".github/instructions/beta.instructions.md").exists()
    assert not (root / ".claude/rules/beta.md").exists()
    assert manual.read_text(encoding="utf-8") == "hand-authored\n"
    assert main(["--root", str(root), "--check"]) == 0
    capsys.readouterr()


def test_malformed_corpus_fails_with_named_file(tmp_path: Path, capsys) -> None:
    """A malformed ADR aborts the run with exit 1 and the filename on stderr."""

    root = _seed_repo(tmp_path)
    (root / "docs/adrs/adr-0009-bad.md").write_text("---\nid: nope\n---\n", encoding="utf-8")
    assert main(["--root", str(root)]) == 1
    assert "adr-0009-bad.md" in capsys.readouterr().err


def test_projection_package_is_stdlib_only() -> None:
    """No module in the projection package imports outside the stdlib or app itself."""

    for module_path in sorted(PROJECTION_SRC.glob("*.py")):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            roots = []
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots = [node.module.split(".")[0]]
            for root_name in roots:
                assert root_name == "app" or root_name in sys.stdlib_module_names, (
                    f"{module_path.name} imports non-stdlib module {root_name!r}"
                )
