import pandas as pd
import pytest

from agents.risk_engine import assess_risk
from agents.risk_fusion import fuse_risk_scores
from agents.risk_levels import classify_risk


CALIBRATION_PATH = (
    "data/splits/ton_iot_network/calibration.csv"
)


def test_risk_engine_returns_valid_result():
    sample = pd.read_csv(CALIBRATION_PATH, nrows=1)

    result = assess_risk(sample)

    assert "risk_score" in result
    assert "risk_level" in result

    assert 0.0 <= result["risk_score"] <= 1.0

    assert result["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }
    assert result["ml_weight"] == 1.0
    assert result["rule_weight"] == 0.0
    assert "rule_score" in result


def test_default_fusion_preserves_ml_score_but_accepts_auditable_rule_score():
    assert fuse_risk_scores(0.82, 0.35) == pytest.approx(0.82)
    assert fuse_risk_scores(0.82, 0.35, ml_weight=0.6) == pytest.approx(0.632)


def test_risk_level_boundaries():
    assert classify_risk(0.0) == "LOW"
    assert classify_risk(0.29) == "LOW"
    assert classify_risk(0.30) == "MEDIUM"
    assert classify_risk(0.59) == "MEDIUM"
    assert classify_risk(0.60) == "HIGH"
    assert classify_risk(0.79) == "HIGH"
    assert classify_risk(0.80) == "CRITICAL"
    assert classify_risk(1.0) == "CRITICAL"


def test_risk_level_rejects_invalid_scores():
    with pytest.raises(ValueError):
        classify_risk(-0.01)

    with pytest.raises(ValueError):
        classify_risk(1.01)
