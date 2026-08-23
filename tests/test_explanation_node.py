from orchestration.explanation_node import explanation_node


def test_explanation_node_returns_explanation():

    result = explanation_node(
        {
            "risk_score": 0.95,
            "risk_level": "CRITICAL",
            "action": "BLOCK",
        }
    )

    assert "BLOCK" in result["explanation"]
    assert "Critical" in result["explanation"]
