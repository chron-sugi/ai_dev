"""Tests for strict YAML domain-contract loading and validation."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.config import DomainContract, is_scaffoldable, load_domain_contract
from app.config.generate_schema import DEFAULT_SCHEMA_PATH, rendered_schema


def approved_base() -> dict[str, object]:
    """Return a minimal approved generic contract."""

    return {
        "schema_version": 2,
        "domain": "example-domain",
        "status": "approved",
        "summary": "Example domain contract.",
        "rules": [{"id": "R-001", "statement": "Keep the example deterministic."}],
        "rejected_alternatives": [
            {"choice": "Implicit behavior", "reason": "It cannot be validated."}
        ],
        "adr_provenance": [],
        "unresolved_gaps": [],
        "types": {"models": [], "enums": [], "errors": [], "aliases": []},
        "invariants": [],
        "dependencies": {"backend": [], "frontend": []},
        "approval": {
            "actor": "agent",
            "name": "contract-reviewer",
            "approved_at": "2026-07-22T12:00:00-04:00",
        },
    }


def backend_component() -> dict[str, object]:
    """Return a complete pure-Python backend component declaration."""

    return {
        "package": "example_domain",
        "public_api": [
            {
                "name": "get_example",
                "kind": "function",
                "signature": "get_example(example_id: str) -> Example",
                "description": "Return an example.",
            }
        ],
    }


def http_interface() -> dict[str, object]:
    """Return one shared HTTP schema and endpoint."""

    return {
        "schemas": [
            {
                "name": "ExampleResponse",
                "description": "Example response.",
                "fields": [
                    {
                        "name": "example_id",
                        "type": "str",
                        "description": "Stable identifier.",
                    }
                ],
            }
        ],
        "endpoints": [
            {
                "id": "example.get",
                "method": "GET",
                "path": "/examples/{example_id}",
                "operation": "get_example",
                "response_type": "ExampleResponse",
                "status_code": 200,
                "errors": [],
            }
        ],
    }


def frontend_component(*, with_api: bool = False) -> dict[str, object]:
    """Return a frontend page, optionally consuming the shared endpoint."""

    component: dict[str, object] = {
        "slice": "example-domain",
        "layer": "pages",
        "placement": {
            "reason": "Pages-first placement owns route composition.",
            "consumers": [],
        },
        "public_api": [
            {
                "name": "ExamplePage",
                "kind": "component",
                "from_segment": "ui",
                "signature": "function ExamplePage(): JSX.Element",
                "description": "Render the page.",
            }
        ],
        "segments": {
            "ui": {
                "components": [
                    {
                        "name": "ExamplePage",
                        "props_type": "ExamplePageProps",
                        "description": "Example page component.",
                    }
                ]
            }
        },
        "route": {"path": "/examples/:exampleId", "export": "ExamplePage"},
    }
    if with_api:
        component["backend_package"] = "example_domain"
        component["segments"]["api"] = {  # type: ignore[index]
            "endpoint_ids": ["example.get"],
            "functions": [
                {
                    "name": "getExample",
                    "endpoint_id": "example.get",
                    "signature": "getExample(exampleId: string): Promise<ExampleResponse>",
                    "description": "Call the generated client.",
                }
            ],
        }
    return component


@pytest.mark.parametrize(
    "components",
    [
        {},
        {"backend": backend_component()},
        {"frontend": frontend_component()},
    ],
    ids=["generic", "backend-only", "frontend-only"],
)
def test_approved_component_combinations_are_scaffoldable(
    components: dict[str, object],
) -> None:
    """Omitted component blocks are intentional and valid."""

    document = approved_base() | components
    assert is_scaffoldable(DomainContract.model_validate(document))


def test_python_fastapi_contract_is_valid() -> None:
    """A Python HTTP adapter resolves endpoint IDs through the root interface."""

    document = approved_base()
    document["http"] = http_interface()
    document["http"]["backend"] = {  # type: ignore[index]
        "endpoint_ids": ["example.get"],
        "dependency_providers": [],
    }
    document["backend"] = backend_component()
    contract = DomainContract.model_validate(document)
    assert contract.backend and contract.http and contract.http.backend


def test_combined_contract_pairs_backend_and_frontend() -> None:
    """A combined seam uses endpoint IDs provided by the paired Python package."""

    document = approved_base()
    document["http"] = http_interface()
    document["http"]["backend"] = {  # type: ignore[index]
        "endpoint_ids": ["example.get"],
        "dependency_providers": [],
    }
    document["backend"] = backend_component()
    document["frontend"] = frontend_component(with_api=True)
    assert is_scaffoldable(DomainContract.model_validate(document))


def test_draft_with_gaps_validates_but_is_not_scaffoldable() -> None:
    """Draft gap recording remains valid without granting execution authority."""

    document = approved_base()
    document["status"] = "draft"
    document["approval"] = None
    document["unresolved_gaps"] = [
        {"field": "backend.public_api", "description": "Signatures need review."}
    ]
    assert not is_scaffoldable(DomainContract.model_validate(document))


def test_approved_contract_rejects_gaps() -> None:
    """Approval cannot coexist with unresolved decisions."""

    document = approved_base()
    document["unresolved_gaps"] = [
        {"field": "frontend.layer", "description": "Placement is undecided."}
    ]
    with pytest.raises(ValidationError, match="cannot contain unresolved gaps"):
        DomainContract.model_validate(document)


def test_unknown_and_missing_component_fields_fail() -> None:
    """Strict models reject schema drift and incomplete activated blocks."""

    unknown = approved_base() | {"surprise": True}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        DomainContract.model_validate(unknown)

    incomplete = approved_base() | {"backend": {"package": "example_domain"}}
    with pytest.raises(ValidationError, match="public_api"):
        DomainContract.model_validate(incomplete)


def test_duplicate_identifiers_fail() -> None:
    """Stable rule, symbol, and endpoint identifiers must be unique."""

    document = approved_base()
    document["rules"] = [
        {"id": "R-001", "statement": "First rule."},
        {"id": "R-001", "statement": "Duplicate rule."},
    ]
    with pytest.raises(ValidationError, match="rules contains duplicate values"):
        DomainContract.model_validate(document)


def test_root_types_invariants_and_dependencies_are_typed() -> None:
    """Shared vocabulary, truths, and edges live at the contract root."""

    document = approved_base()
    document["types"] = {
        "models": [],
        "enums": [
            {
                "name": "ExampleStatus",
                "base": "StrEnum",
                "members": {"pending": "pending", "active": "active"},
                "description": "Example lifecycle state.",
            }
        ],
        "errors": [],
        "aliases": [],
    }
    document["invariants"] = [
        {
            "id": "I-001",
            "statement": "Example status is always declared.",
            "applies_to": ["types.ExampleStatus"],
        }
    ]
    document["dependencies"] = {
        "backend": [
            {
                "target": "identity",
                "reason": "Resolve the current actor through its public API.",
            }
        ],
        "frontend": [],
    }
    contract = DomainContract.model_validate(document)
    assert contract.types.enums[0].base == "StrEnum"
    assert contract.invariants[0].id == "I-001"
    assert contract.dependencies.backend[0].target == "identity"


def test_legacy_python_root_key_is_rejected() -> None:
    """The renamed backend key has no silent compatibility alias."""

    document = approved_base() | {"python": backend_component()}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        DomainContract.model_validate(document)


def test_invalid_endpoint_cross_references_fail() -> None:
    """Components cannot select missing or unprovided paired endpoints."""

    missing = approved_base()
    missing["http"] = http_interface()
    missing["http"]["backend"] = {"endpoint_ids": ["example.missing"]}  # type: ignore[index]
    missing["backend"] = backend_component()
    with pytest.raises(ValidationError, match="endpoint references are undeclared"):
        DomainContract.model_validate(missing)

    unprovided = approved_base()
    interface = http_interface()
    extra = deepcopy(interface["endpoints"][0])  # type: ignore[index]
    extra["id"] = "example.list"
    extra["path"] = "/examples"
    extra["operation"] = "list_examples"
    interface["endpoints"].append(extra)  # type: ignore[union-attr]
    unprovided["http"] = interface
    unprovided["http"]["backend"] = {"endpoint_ids": ["example.get"]}  # type: ignore[index]
    unprovided["backend"] = backend_component()
    frontend = frontend_component(with_api=True)
    frontend["segments"]["api"]["endpoint_ids"] = ["example.list"]  # type: ignore[index]
    frontend["segments"]["api"]["functions"][0]["endpoint_id"] = "example.list"  # type: ignore[index]
    unprovided["frontend"] = frontend
    with pytest.raises(ValidationError, match="not provided by http.backend"):
        DomainContract.model_validate(unprovided)


def test_http_schema_references_must_exist() -> None:
    """Endpoint request and response types are declared, not inferred."""

    document = approved_base()
    interface = http_interface()
    interface["endpoints"][0]["response_type"] = "MissingResponse"  # type: ignore[index]
    document["http"] = interface
    document["frontend"] = frontend_component(with_api=True)
    with pytest.raises(ValidationError, match="undeclared schemas"):
        DomainContract.model_validate(document)


def test_non_page_layer_requires_two_consumers() -> None:
    """Lower-layer extraction needs deterministic consumer evidence."""

    document = approved_base()
    frontend = frontend_component()
    frontend["layer"] = "features"
    frontend.pop("route")
    document["frontend"] = frontend
    with pytest.raises(ValidationError, match="at least two named consumers"):
        DomainContract.model_validate(document)


def test_safe_yaml_loader_rejects_custom_tags(tmp_path: Path) -> None:
    """Custom constructors cannot execute through domain contract loading."""

    path = tmp_path / "CONTRACT.yaml"
    path.write_text(
        "!!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8"
    )
    with pytest.raises(yaml.constructor.ConstructorError):
        load_domain_contract(path)


def test_yaml_loader_rejects_duplicate_mapping_keys(tmp_path: Path) -> None:
    """Duplicate YAML keys cannot silently replace primary contract values."""

    path = tmp_path / "CONTRACT.yaml"
    path.write_text("schema_version: 2\nschema_version: 2\n", encoding="utf-8")
    with pytest.raises(yaml.constructor.ConstructorError, match="duplicate key"):
        load_domain_contract(path)


def test_loads_committed_contracts_and_template() -> None:
    """Migrated contracts remain approved and the authoring template remains draft."""

    roots = Path("docs/domains")
    migrated = list(roots.glob("*/CONTRACT.yaml"))
    assert migrated
    assert all(is_scaffoldable(load_domain_contract(path)) for path in migrated)
    assert not is_scaffoldable(load_domain_contract(roots / "_contract_template.yaml"))


def test_committed_json_schema_has_no_drift() -> None:
    """The checked-in schema is an exact deterministic Pydantic projection."""

    assert DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8") == rendered_schema()
    parsed = json.loads(rendered_schema())
    assert parsed["title"] == "DomainContract"
