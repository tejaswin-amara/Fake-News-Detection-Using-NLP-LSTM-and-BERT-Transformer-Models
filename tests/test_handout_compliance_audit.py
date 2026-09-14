from pathlib import Path

from scripts.handout_compliance_audit import audit


def test_all_handout_implementation_surfaces_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    result = audit(root)
    assert result["implementation_gate_passed"] is True
    assert result["fail_count"] == 0
    assert result["pass_count"] == len(result["requirements"])
