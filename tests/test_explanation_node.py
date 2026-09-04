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
    assert result["llm_narrative_status"] in {
        "disabled_no_api_key",
        "generated",
    } or result["llm_narrative_status"].startswith("unavailable:")
