"""Guard the contract-driven scaffolder protocol and domain prompts."""

from pathlib import Path


def test_scaffolder_requires_contract_and_rejects_legacy_adr_input() -> None:
    """The standing protocol uses contract approval rather than ADR status."""

    text = Path("src/assets/agents/scaffolder.agents.md").read_text(encoding="utf-8")
    assert "`CONTRACT`" in text
    assert "Do not accept `ADR_ID`" in text
    assert "status` is not `approved`" in text
    assert "`unresolved_gaps` is non-empty" in text


def test_combined_protocol_orders_backend_seam_frontend() -> None:
    """Combined work projects generated seam artifacts before frontend work."""

    text = Path("src/assets/agents/scaffolder.agents.md").read_text(encoding="utf-8")
    backend_at = text.index("Scaffold and verify the backend")
    seam_at = text.index("OpenAPI export and client type-generation")
    frontend_at = text.index("Scaffold and verify frontend")
    assert backend_at < seam_at < frontend_at
    assert "one `.velocai/<TASK_ID>/scaffold-report.md`" in text


def test_domain_prompts_are_presence_driven() -> None:
    """Both domain prompts consume YAML blocks rather than ADR inference."""

    python = Path("src/assets/prompts/scaffold-python-domain-package.md").read_text(
        encoding="utf-8"
    )
    frontend = Path("src/assets/prompts/scaffold-fsd-frontend-slice.md").read_text(
        encoding="utf-8"
    )
    assert "Resolve each only from optional block presence" in python
    assert "Resolve structure only from block presence" in frontend
    assert "ADR-declared" not in python
    assert "ADR-declared" not in frontend
