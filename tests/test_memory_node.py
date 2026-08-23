from orchestration.memory_node import memory_update_node


def test_memory_node_stores_event():
    result = memory_update_node(
        {
            "src_ip": "192.168.1.50",
            "risk_score": 0.9,
            "action": "BLOCK",
        }
    )

    assert result["previous_action"] == "BLOCK"


def test_memory_node_handles_missing_ip():
    result = memory_update_node(
        {
            "risk_score": 0.4,
            "action": "MONITOR",
        }
    )

    assert result["previous_action"] is None
