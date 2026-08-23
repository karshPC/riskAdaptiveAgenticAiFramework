from agents.escalation import escalation_agent


def test_block_creates_critical_escalation():

    result = escalation_agent(
        {
            "action": "BLOCK",
            "memory_reason": "Repeated attack detected."
        }
    )

    assert result["severity"] == "CRITICAL"
    assert "Repeated attack" in result["escalation_reason"]
