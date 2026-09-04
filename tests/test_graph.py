import pandas as pd

from orchestration.graph import risk_graph
from orchestration.graph import decision_node


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


def test_default_decision_mode_is_context_inert():
    result = decision_node({"risk_score": 0.55})

    assert result["risk_score"] == 0.55
    assert result["memory_boost"] == 0.0
    assert result["threat_boost"] == 0.0


def test_contextual_mode_records_applied_boosts(monkeypatch):
    monkeypatch.setattr(
        "orchestration.graph.memory_reasoner.analyze",
        lambda _: {"risk_boost": 0.20, "reason": "Repeated activity."},
    )
    monkeypatch.setattr(
        "orchestration.graph.threat_intelligence_agent.analyze",
        lambda _: {"threat_boost": 0.15, "threat_reason": "Known threat."},
    )

    result = decision_node(
        {"risk_score": 0.55, "src_ip": "192.0.2.1", "mode": "Hybrid_Memory_Threat"}
    )

    assert result["risk_score"] == 0.90
    assert result["risk_level"] == "CRITICAL"
    assert result["memory_boost"] == 0.20
    assert result["threat_boost"] == 0.15
