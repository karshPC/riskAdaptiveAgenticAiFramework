import pytest

from agents.context_decision_engine import decide_from_context
from schemas.risk import RiskContext


@pytest.mark.parametrize(
    "score, level, expected_action",
    [
        (0.10, "LOW", "ALLOW"),
        (0.45, "MEDIUM", "MONITOR"),
        (0.70, "HIGH", "RESTRICT"),
        (0.90, "CRITICAL", "BLOCK"),
    ],
)
def test_context_decision_mapping(score, level, expected_action):
    context = RiskContext(
        risk_score=score,
        risk_level=level,
    )

    result = decide_from_context(context)

    assert result["risk_score"] == score
    assert result["risk_level"] == level
    assert result["action"] == expected_action


def test_context_decision_preserves_context():
    context = RiskContext(
        risk_score=0.75,
        risk_level="HIGH",
        attack_type="scanning",
        src_ip="192.168.1.10",
        dst_ip="10.0.0.5",
        proto="tcp",
        service="http",
        previous_action="MONITOR",
    )

    result = decide_from_context(context)

    assert result["action"] == "RESTRICT"
    assert "0.7500" in result["reason"]
    assert "HIGH" in result["reason"]


def test_context_decision_returns_reason():
    context = RiskContext(
        risk_score=0.90,
        risk_level="CRITICAL",
    )

    result = decide_from_context(context)

    assert result["action"] == "BLOCK"
    assert result["reason"] == (
        "Risk score 0.9000 classified as CRITICAL."
    )
