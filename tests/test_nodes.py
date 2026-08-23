import pandas as pd

from orchestration.nodes import risk_assessment_node


def test_real_risk_assessment_node():
    event = pd.read_csv(
        "data/splits/ton_iot_network/calibration.csv",
        nrows=1,
    )

    result = risk_assessment_node(
        {
            "event": event
        }
    )

    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }
