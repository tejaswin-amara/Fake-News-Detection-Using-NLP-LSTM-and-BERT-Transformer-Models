import pytest

from src.models.governance import ModelState, initial_record, transition


def record():
    return initial_record("logistic-tfidf", "1.0.0", "abc123", "dataset-1", "a" * 64)


def test_normal_promotion_requires_ordered_states() -> None:
    model = record()
    model = transition(model, ModelState.VALIDATED)
    model = transition(model, ModelState.APPROVED, actor="reviewer")
    model = transition(model, ModelState.STAGED)
    model = transition(model, ModelState.PRODUCTION, actor="release-manager")
    assert model.state is ModelState.PRODUCTION
    assert model.approved_by == "release-manager"


def test_production_cannot_be_promoted_without_human_actor() -> None:
    model = transition(transition(record(), ModelState.VALIDATED), ModelState.APPROVED, actor="reviewer")
    model = transition(model, ModelState.STAGED)
    with pytest.raises(PermissionError):
        transition(model, ModelState.PRODUCTION)


def test_drift_signal_cannot_skip_validation() -> None:
    with pytest.raises(ValueError):
        transition(record(), ModelState.PRODUCTION, actor="automation")


def test_rollback_requires_actor() -> None:
    model = record()
    for state, actor in [
        (ModelState.VALIDATED, None),
        (ModelState.APPROVED, "reviewer"),
        (ModelState.STAGED, None),
        (ModelState.PRODUCTION, "release-manager"),
    ]:
        model = transition(model, state, actor=actor)
    with pytest.raises(PermissionError):
        transition(model, ModelState.ROLLED_BACK)
    assert transition(model, ModelState.ROLLED_BACK, actor="incident-commander").state is ModelState.ROLLED_BACK
