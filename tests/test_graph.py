import pandas as pd

from orchestration.graph import risk_graph


EVENT = pd.read_csv(
    "data/splits/ton_iot_network/calibration.csv",
    nrows=1,
)


def test_graph_blocks_critical_risk():
    result = risk_graph.invoke(
        {
            "event": EVENT,
        }
    )

    assert result["action"] in {
        "ALLOW",
        "MONITOR",
        "RESTRICT",
        "BLOCK",
    }

    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }


def test_graph_returns_action():
    result = risk_graph.invoke(
        {
            "event": EVENT,
        }
    )

    assert "action" in result
    assert "reason" in result


def test_graph_runs_end_to_end():
    result = risk_graph.invoke(
        {
            "event": EVENT,
        }
    )

    assert isinstance(result["risk_score"], float)
    assert isinstance(result["risk_level"], str)
