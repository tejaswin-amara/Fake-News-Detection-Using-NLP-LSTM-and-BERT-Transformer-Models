"""Small, auditable model-governance state machine for CO6/M6.

The handout asks for model packaging and production-style ML engineering. This
module makes promotion explicit and prevents a drift signal from silently
changing production state.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ModelState(StrEnum):
    TRAINED = "trained"
    VALIDATED = "validated"
    APPROVED = "approved"
    STAGED = "staged"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ROLLED_BACK = "rolled_back"


_ALLOWED: dict[ModelState, set[ModelState]] = {
    ModelState.TRAINED: {ModelState.VALIDATED},
    ModelState.VALIDATED: {ModelState.APPROVED},
    ModelState.APPROVED: {ModelState.STAGED},
    ModelState.STAGED: {ModelState.PRODUCTION},
    ModelState.PRODUCTION: {ModelState.DEPRECATED, ModelState.ROLLED_BACK},
    ModelState.DEPRECATED: set(),
    ModelState.ROLLED_BACK: set(),
}


@dataclass(frozen=True)
class ModelRecord:
    model_id: str
    version: str
    git_revision: str
    dataset_revision: str
    artifact_sha256: str
    state: ModelState
    approved_by: str | None = None
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def transition(record: ModelRecord, target: ModelState, *, actor: str | None = None) -> ModelRecord:
    """Perform one legal lifecycle transition.

    Production promotion and rollback require an explicit actor. A drift report
    alone can never call this function successfully because it has no authority
    to supply production approval.
    """
    if target not in _ALLOWED[record.state]:
        raise ValueError(f"Illegal model transition: {record.state} -> {target}")
    if target in {ModelState.APPROVED, ModelState.PRODUCTION, ModelState.ROLLED_BACK} and not actor:
        raise PermissionError(f"Transition to {target} requires an explicit human actor")
    return ModelRecord(
        model_id=record.model_id,
        version=record.version,
        git_revision=record.git_revision,
        dataset_revision=record.dataset_revision,
        artifact_sha256=record.artifact_sha256,
        state=target,
        approved_by=actor if target in {ModelState.APPROVED, ModelState.PRODUCTION, ModelState.ROLLED_BACK} else record.approved_by,
        updated_at=datetime.now(UTC).isoformat(),
    )


def initial_record(
    model_id: str,
    version: str,
    git_revision: str,
    dataset_revision: str,
    artifact_sha256: str,
) -> ModelRecord:
    if not all([model_id, version, git_revision, dataset_revision, artifact_sha256]):
        raise ValueError("Model records require non-empty identity and integrity fields")
    return ModelRecord(
        model_id=model_id,
        version=version,
        git_revision=git_revision,
        dataset_revision=dataset_revision,
        artifact_sha256=artifact_sha256,
        state=ModelState.TRAINED,
        updated_at=datetime.now(UTC).isoformat(),
    )
