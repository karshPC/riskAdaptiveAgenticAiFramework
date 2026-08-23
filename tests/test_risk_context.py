import pytest
from pydantic import ValidationError

from schemas.risk import RiskContext


def test_valid_risk_context():
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

    assert context.risk_score == 0.75
    assert context.risk_level == "HIGH"
    assert context.attack_type == "scanning"


def test_risk_score_cannot_be_below_zero():
    with pytest.raises(ValidationError):
        RiskContext(
            risk_score=-0.01,
            risk_level="LOW",
        )


def test_risk_score_cannot_exceed_one():
    with pytest.raises(ValidationError):
        RiskContext(
            risk_score=1.01,
            risk_level="CRITICAL",
        )


def test_optional_context_fields():
    context = RiskContext(
        risk_score=0.20,
        risk_level="LOW",
    )

    assert context.attack_type is None
    assert context.src_ip is None
    assert context.dst_ip is None
    assert context.previous_action is None
