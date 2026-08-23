import pytest

from agents.decision_engine import make_decision


def test_low_risk_allows():
    result = make_decision(0.10)

    assert result["risk_level"] == "LOW"
    assert result["action"] == "ALLOW"


def test_medium_risk_monitors():
    result = make_decision(0.45)

    assert result["risk_level"] == "MEDIUM"
    assert result["action"] == "MONITOR"


def test_high_risk_restricts():
    result = make_decision(0.70)

    assert result["risk_level"] == "HIGH"
    assert result["action"] == "RESTRICT"


def test_critical_risk_blocks():
    result = make_decision(0.90)

    assert result["risk_level"] == "CRITICAL"
    assert result["action"] == "BLOCK"


def test_invalid_risk_is_rejected():
    with pytest.raises(ValueError):
        make_decision(-0.1)

    with pytest.raises(ValueError):
        make_decision(1.1)
