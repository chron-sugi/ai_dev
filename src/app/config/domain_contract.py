"""Typed loading and validation for primary YAML domain contracts."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")]
KebabName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
HttpPath = Annotated[str, StringConstraints(pattern=r"^/")]


class StrictModel(BaseModel):
    """Base model that rejects undeclared contract fields."""

    model_config = ConfigDict(extra="forbid")


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that also rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeySafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    """Construct a mapping while refusing ambiguous duplicate keys."""

    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable key",
                key_node.start_mark,
            ) from error
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class AdrReference(StrictModel):
    """Optional provenance linking a contract decision to an ADR."""

    id: Annotated[str, StringConstraints(pattern=r"^ADR-[0-9]{4}$")]
    path: NonEmpty


class Approval(StrictModel):
    """Actor and time that approved a scaffoldable contract."""

    actor: Literal["human", "agent"]
    name: NonEmpty
    approved_at: datetime


class Rule(StrictModel):
    """Atomic current rule owned by the contract."""

    id: Annotated[str, StringConstraints(pattern=r"^R-[0-9]{3}$")]
    statement: NonEmpty
    adr: Annotated[str, StringConstraints(pattern=r"^ADR-[0-9]{4}$")] | None = None


class RejectedAlternative(StrictModel):
    """Rejected choice and the reason it lost."""

    choice: NonEmpty
    reason: NonEmpty


class UnresolvedGap(StrictModel):
    """Known missing decision that prevents contract approval."""

    field: NonEmpty
    description: NonEmpty


class TypedField(StrictModel):
    """Named typed field used in Python model declarations."""

    name: Identifier
    type: NonEmpty
    required: bool = True
    default: str | None = None
    description: NonEmpty


class ModelDeclaration(StrictModel):
    """Python model that the scaffold must declare exactly."""

    name: Identifier
    fields: list[TypedField] = Field(default_factory=list)
    description: NonEmpty


class ErrorDeclaration(StrictModel):
    """Python domain error declaration."""

    name: Identifier
    base: Identifier = "Exception"
    description: NonEmpty


class EnumDeclaration(StrictModel):
    """Enum vocabulary generated in the backend models module."""

    name: Identifier
    base: Literal["StrEnum", "Enum", "IntEnum"]
    members: Annotated[dict[Identifier, NonEmpty], Field(min_length=1)]
    description: NonEmpty


class TypeAliasDeclaration(StrictModel):
    """Named domain type alias."""

    name: Identifier
    value: NonEmpty
    description: NonEmpty


class DomainTypes(StrictModel):
    """Shared domain vocabulary declared independently of a component."""

    models: list[ModelDeclaration] = Field(default_factory=list)
    enums: list[EnumDeclaration] = Field(default_factory=list)
    errors: list[ErrorDeclaration] = Field(default_factory=list)
    aliases: list[TypeAliasDeclaration] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_type_names(self) -> DomainTypes:
        """Reject duplicate names across every domain type category."""

        declarations = [*self.models, *self.enums, *self.errors, *self.aliases]
        _require_unique(declarations, "name", "types")
        return self


class Invariant(StrictModel):
    """Checkable domain truth that implementations must preserve."""

    id: Annotated[str, StringConstraints(pattern=r"^I-[0-9]{3}$")]
    statement: NonEmpty
    applies_to: list[NonEmpty] = Field(default_factory=list)
    enforcement: NonEmpty | None = None


class PythonSymbol(StrictModel):
    """Exact symbol declaration for a Python public or internal surface."""

    name: Identifier
    kind: Literal["function", "class", "constant", "protocol", "type_alias"]
    signature: NonEmpty
    description: NonEmpty


class DependencyEdge(StrictModel):
    """Explicitly granted dependency edge to another domain."""

    target: KebabName
    reason: NonEmpty
    adr: Annotated[str, StringConstraints(pattern=r"^ADR-[0-9]{4}$")] | None = None


class Persistence(StrictModel):
    """Persistent state that activates tables.py and store.py."""

    tables: Annotated[list[Identifier], Field(min_length=1)]
    description: NonEmpty


class Service(StrictModel):
    """Service operations that activate service.py."""

    operations: Annotated[list[PythonSymbol], Field(min_length=1)]


class Tunable(StrictModel):
    """Environment-sourced domain setting."""

    name: Identifier
    type: NonEmpty
    env: Annotated[str, StringConstraints(pattern=r"^[A-Z][A-Z0-9_]*$")]
    description: NonEmpty
    default: str | None = None


class PythonConfig(StrictModel):
    """Tunables that activate a domain config.py module."""

    tunables: Annotated[list[Tunable], Field(min_length=1)]


class Job(StrictModel):
    """Non-HTTP entry point that activates jobs.py."""

    name: Identifier
    signature: NonEmpty
    trigger: NonEmpty
    description: NonEmpty


class Jobs(StrictModel):
    """Declared non-HTTP entry points."""

    entries: Annotated[list[Job], Field(min_length=1)]


class TestingSurface(StrictModel):
    """Testing exports that activate testing.py."""

    exports: Annotated[list[PythonSymbol], Field(min_length=1)]


class DependencyProvider(StrictModel):
    """FastAPI dependency provider owned by a domain adapter."""

    name: Identifier
    signature: NonEmpty
    description: NonEmpty


class BackendHttpProvider(StrictModel):
    """Root HTTP provider declarations for the package-local FastAPI adapter."""

    endpoint_ids: Annotated[list[NonEmpty], Field(min_length=1)]
    dependency_providers: list[DependencyProvider] = Field(default_factory=list)


class BackendComponent(StrictModel):
    """Complete declarations consumed by the Python backend scaffold."""

    package: Identifier
    public_api: Annotated[list[PythonSymbol], Field(min_length=1)]
    persistence: Persistence | None = None
    service: Service | None = None
    config: PythonConfig | None = None
    jobs: Jobs | None = None
    testing: TestingSurface | None = None

    @model_validator(mode="after")
    def unique_names(self) -> BackendComponent:
        """Reject duplicate declarations within each backend namespace."""

        _require_unique(self.public_api, "name", "backend.public_api")
        if self.service:
            _require_unique(
                self.service.operations, "name", "backend.service.operations"
            )
        if self.config:
            _require_unique(self.config.tunables, "name", "backend.config.tunables")
            _require_unique(self.config.tunables, "env", "backend.config.tunables env")
            expected_prefix = f"{self.package.upper()}_"
            for tunable in self.config.tunables:
                if not tunable.env.startswith(expected_prefix):
                    raise ValueError(
                        f"backend config env {tunable.env!r} must start with "
                        f"{expected_prefix!r}"
                    )
        if self.jobs:
            _require_unique(self.jobs.entries, "name", "backend.jobs.entries")
        if self.testing:
            _require_unique(self.testing.exports, "name", "backend.testing.exports")
        return self


class HttpEndpoint(StrictModel):
    """Shared HTTP interface used by backend and frontend components."""

    id: Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")]
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: HttpPath
    operation: Identifier
    request_type: Identifier | None = None
    response_type: Identifier
    status_code: Annotated[int, Field(ge=100, le=599)]
    errors: list[NonEmpty] = Field(default_factory=list)
    auth: NonEmpty | None = None


class HttpInterface(StrictModel):
    """Canonical endpoint declarations shared across component seams."""

    schemas: Annotated[list[ModelDeclaration], Field(min_length=1)]
    endpoints: Annotated[list[HttpEndpoint], Field(min_length=1)]
    backend: BackendHttpProvider | None = None

    @model_validator(mode="after")
    def unique_endpoints(self) -> HttpInterface:
        """Require stable unique IDs and method/path pairs."""

        _require_unique(self.endpoints, "id", "http.endpoints")
        _require_unique(self.schemas, "name", "http.schemas")
        pairs = [(endpoint.method, endpoint.path) for endpoint in self.endpoints]
        if len(pairs) != len(set(pairs)):
            raise ValueError("http.endpoints contains duplicate method/path pairs")
        schema_names = {schema.name for schema in self.schemas}
        referenced_types = {
            type_name
            for endpoint in self.endpoints
            for type_name in (endpoint.request_type, endpoint.response_type)
            if type_name
        }
        missing_types = referenced_types - schema_names
        if missing_types:
            raise ValueError(
                f"http endpoints reference undeclared schemas: {sorted(missing_types)}"
            )
        if self.backend:
            _require_unique(
                self.backend.endpoint_ids, None, "http.backend.endpoint_ids"
            )
            _require_unique(
                self.backend.dependency_providers,
                "name",
                "http.backend.dependency_providers",
            )
        return self


class FrontendExport(StrictModel):
    """Exact TypeScript export exposed by a slice public API."""

    name: Identifier
    kind: Literal["component", "function", "type", "constant", "hook"]
    from_segment: Literal["ui", "api", "model", "lib"]
    signature: NonEmpty
    description: NonEmpty


class UiComponent(StrictModel):
    """UI component declaration."""

    name: Identifier
    props_type: NonEmpty
    description: NonEmpty


class UiSegment(StrictModel):
    """Declarations that activate a frontend ui segment."""

    components: Annotated[list[UiComponent], Field(min_length=1)]


class FrontendApiFunction(StrictModel):
    """Client function wrapping a generated API operation."""

    name: Identifier
    endpoint_id: NonEmpty
    signature: NonEmpty
    description: NonEmpty


class FrontendApiSegment(StrictModel):
    """Declarations that activate a frontend api segment."""

    endpoint_ids: Annotated[list[NonEmpty], Field(min_length=1)]
    functions: Annotated[list[FrontendApiFunction], Field(min_length=1)]

    @model_validator(mode="after")
    def unique_api_names(self) -> FrontendApiSegment:
        """Require unique endpoint references and wrapper functions."""

        _require_unique(self.endpoint_ids, None, "frontend.segments.api.endpoint_ids")
        _require_unique(self.functions, "name", "frontend.segments.api.functions")
        for function in self.functions:
            if function.endpoint_id not in self.endpoint_ids:
                raise ValueError(
                    f"frontend api function {function.name!r} references an endpoint "
                    "not listed in its segment"
                )
        wrapped_ids = {function.endpoint_id for function in self.functions}
        if wrapped_ids != set(self.endpoint_ids) or len(self.functions) != len(
            self.endpoint_ids
        ):
            raise ValueError(
                "every frontend api endpoint requires exactly one wrapper function"
            )
        return self


class StateDeclaration(StrictModel):
    """Frontend state that outlives a single component."""

    name: Identifier
    type: NonEmpty
    description: NonEmpty


class ModelSegment(StrictModel):
    """Declarations that activate a frontend model segment."""

    state: Annotated[list[StateDeclaration], Field(min_length=1)]


class HelperDeclaration(StrictModel):
    """Slice-specific helper shared by at least two modules."""

    name: Identifier
    signature: NonEmpty
    consumers: Annotated[list[NonEmpty], Field(min_length=2)]
    description: NonEmpty


class LibSegment(StrictModel):
    """Declarations that activate a frontend lib segment."""

    helpers: Annotated[list[HelperDeclaration], Field(min_length=1)]


class FrontendSegments(StrictModel):
    """Explicit optional FSD segments; presence means create."""

    ui: UiSegment | None = None
    api: FrontendApiSegment | None = None
    model: ModelSegment | None = None
    lib: LibSegment | None = None

    @model_validator(mode="after")
    def at_least_one_segment(self) -> FrontendSegments:
        """Reject a frontend slice with no declared structure."""

        if not any((self.ui, self.api, self.model, self.lib)):
            raise ValueError("frontend.segments must activate at least one segment")
        return self


class FrontendRoute(StrictModel):
    """Page route registration declaration."""

    path: HttpPath
    export: Identifier


class LayerPlacement(StrictModel):
    """Reason and consumers supporting the selected FSD layer."""

    reason: NonEmpty
    consumers: list[NonEmpty] = Field(default_factory=list)


class CrossSliceEdge(StrictModel):
    """Explicit FSD @x edge granted by the contract."""

    target: NonEmpty
    exports: Annotated[list[Identifier], Field(min_length=1)]
    reason: NonEmpty
    adr: Annotated[str, StringConstraints(pattern=r"^ADR-[0-9]{4}$")] | None = None


class DomainDependencies(StrictModel):
    """All explicitly granted backend and frontend dependency edges."""

    backend: list[DependencyEdge] = Field(default_factory=list)
    frontend: list[CrossSliceEdge] = Field(default_factory=list)


class FrontendComponent(StrictModel):
    """Complete declarations consumed by the FSD slice scaffold."""

    slice: KebabName
    layer: Literal["pages", "widgets", "features", "entities"]
    placement: LayerPlacement
    public_api: Annotated[list[FrontendExport], Field(min_length=1)]
    segments: FrontendSegments
    route: FrontendRoute | None = None
    backend_package: Identifier | None = None

    @model_validator(mode="after")
    def validate_frontend_shape(self) -> FrontendComponent:
        """Validate public exports, segment presence, and route placement."""

        _require_unique(self.public_api, "name", "frontend.public_api")
        for export in self.public_api:
            if getattr(self.segments, export.from_segment) is None:
                raise ValueError(
                    f"frontend export {export.name!r} references omitted "
                    f"segment {export.from_segment!r}"
                )
        if self.route and self.layer != "pages":
            raise ValueError("frontend.route is valid only for a pages slice")
        if self.layer != "pages" and len(set(self.placement.consumers)) < 2:
            raise ValueError(
                "non-page frontend layers require at least two named consumers"
            )
        if self.route and self.route.export not in {
            item.name for item in self.public_api
        }:
            raise ValueError("frontend.route.export must name a public_api export")
        if self.backend_package and self.segments.api is None:
            raise ValueError("frontend.backend_package requires frontend.segments.api")
        return self


class DomainContract(StrictModel):
    """Primary executable specification for a documented domain."""

    schema_version: Literal[2]
    domain: KebabName
    status: Literal["draft", "approved"]
    summary: NonEmpty
    rules: Annotated[list[Rule], Field(min_length=1)]
    rejected_alternatives: Annotated[list[RejectedAlternative], Field(min_length=1)]
    adr_provenance: list[AdrReference] = Field(default_factory=list)
    unresolved_gaps: list[UnresolvedGap] = Field(default_factory=list)
    approval: Approval | None = None
    types: DomainTypes = Field(default_factory=DomainTypes)
    invariants: list[Invariant] = Field(default_factory=list)
    dependencies: DomainDependencies = Field(default_factory=DomainDependencies)
    http: HttpInterface | None = None
    backend: BackendComponent | None = None
    frontend: FrontendComponent | None = None

    @model_validator(mode="after")
    def validate_contract(self) -> DomainContract:
        """Enforce lifecycle, uniqueness, and cross-component references."""

        _require_unique(self.rules, "id", "rules")
        _require_unique(self.invariants, "id", "invariants")
        _require_unique(self.adr_provenance, "id", "adr_provenance")
        _require_unique(self.dependencies.backend, "target", "dependencies.backend")
        _require_unique(self.dependencies.frontend, "target", "dependencies.frontend")
        provenance_ids = {item.id for item in self.adr_provenance}
        for rule in self.rules:
            if rule.adr and rule.adr not in provenance_ids:
                raise ValueError(f"rule {rule.id!r} references missing ADR provenance")

        if self.status == "approved":
            if self.approval is None:
                raise ValueError("approved contracts require approval metadata")
            if self.unresolved_gaps:
                raise ValueError("approved contracts cannot contain unresolved gaps")
        elif self.approval is not None:
            raise ValueError("draft contracts cannot contain approval metadata")

        endpoint_ids = {item.id for item in self.http.endpoints} if self.http else set()
        backend_ids = (
            set(self.http.backend.endpoint_ids)
            if self.http and self.http.backend
            else set()
        )
        frontend_api = self.frontend.segments.api if self.frontend else None
        frontend_ids = set(frontend_api.endpoint_ids) if frontend_api else set()
        referenced_ids = backend_ids | frontend_ids
        missing = referenced_ids - endpoint_ids
        if missing:
            raise ValueError(
                f"component endpoint references are undeclared: {sorted(missing)}"
            )
        if self.http and not referenced_ids:
            raise ValueError(
                "http is present but no component provides or consumes its endpoints"
            )
        if self.http and self.http.backend and not self.backend:
            raise ValueError("http.backend requires the root backend component")
        if self.backend and self.frontend and self.frontend.backend_package:
            if self.frontend.backend_package != self.backend.package:
                raise ValueError("frontend.backend_package must match backend.package")
            if self.frontend.slice.replace("-", "_") != self.backend.package:
                raise ValueError("paired frontend.slice must match backend.package")
            unprovided = frontend_ids - backend_ids
            if unprovided:
                raise ValueError(
                    "paired frontend endpoints are not provided by http.backend: "
                    f"{sorted(unprovided)}"
                )
        if self.backend and self.http and self.http.backend:
            operation_names = {symbol.name for symbol in self.backend.public_api}
            if self.backend.service:
                operation_names.update(
                    symbol.name for symbol in self.backend.service.operations
                )
            provided_operations = {
                endpoint.operation
                for endpoint in self.http.endpoints
                if endpoint.id in backend_ids
            }
            missing_operations = provided_operations - operation_names
            if missing_operations:
                raise ValueError(
                    "http.backend endpoints reference undeclared backend operations: "
                    f"{sorted(missing_operations)}"
                )
            declared_errors = {error.name for error in self.types.errors}
            provided_errors = {
                error
                for endpoint in self.http.endpoints
                if endpoint.id in backend_ids
                for error in endpoint.errors
            }
            missing_errors = provided_errors - declared_errors
            if missing_errors:
                raise ValueError(
                    "http.backend endpoints reference undeclared types.errors: "
                    f"{sorted(missing_errors)}"
                )
        return self


def _require_unique(items: list[Any], attribute: str | None, label: str) -> None:
    """Raise when a list contains duplicate scalar or attribute values."""

    values = [getattr(item, attribute) if attribute else item for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} contains duplicate values")


def load_domain_contract(path: str | Path) -> DomainContract:
    """Safely parse and validate a YAML domain contract from disk."""

    contract_path = Path(path)
    with contract_path.open(encoding="utf-8") as stream:
        document = yaml.load(stream, Loader=UniqueKeySafeLoader)
    if not isinstance(document, dict):
        raise ValueError("domain contract YAML must contain one mapping document")
    return DomainContract.model_validate(document)


def validate_domain_contract(path: str | Path) -> DomainContract:
    """Validate a YAML contract and return its typed representation."""

    return load_domain_contract(path)


def is_scaffoldable(contract: DomainContract) -> bool:
    """Return whether a validated contract is approved for scaffolding."""

    return contract.status == "approved" and not contract.unresolved_gaps


def domain_contract_json_schema() -> dict[str, Any]:
    """Return the canonical JSON Schema generated by Pydantic."""

    return DomainContract.model_json_schema()
