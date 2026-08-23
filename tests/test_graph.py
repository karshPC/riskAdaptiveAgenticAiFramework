from orchestration.graph import risk_graph


def test_graph_blocks_critical_risk():
    result = risk_graph.invoke(
        {
            "risk_score": 0.90,
            "risk_level": "CRITICAL",
            "attack_type": "scanning",
        }
    )

    assert result["action"] == "BLOCK"
    assert result["risk_level"] == "CRITICAL"


def test_graph_allows_low_risk():
    result = risk_graph.invoke(
        {
            "risk_score": 0.10,
            "risk_level": "LOW",
        }
    )

    assert result["action"] == "ALLOW"
    assert result["risk_level"] == "LOW"


def test_graph_monitors_medium_risk():
    result = risk_graph.invoke(
        {
            "risk_score": 0.45,
            "risk_level": "MEDIUM",
        }
    )

    assert result["action"] == "MONITOR"
