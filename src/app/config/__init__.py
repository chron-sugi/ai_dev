"""Public configuration API for VelocAI."""

from .domain_contract import (
    DomainContract,
    domain_contract_json_schema,
    is_scaffoldable,
    load_domain_contract,
    validate_domain_contract,
)

__all__ = [
    "DomainContract",
    "domain_contract_json_schema",
    "is_scaffoldable",
    "load_domain_contract",
    "validate_domain_contract",
]
