from agents.response import response_agent


def test_block_response():
    result = response_agent(
        {
            "action": "BLOCK"
        }
    )

    assert "Firewall block" in result["response_action"]


def test_monitor_response():
    result = response_agent(
        {
            "action": "MONITOR"
        }
    )

    assert "monitoring" in result["response_action"]
