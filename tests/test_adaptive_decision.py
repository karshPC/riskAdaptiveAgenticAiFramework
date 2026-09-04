import pytest

from orchestration.graph import decision_node
from agents.memory import memory


def test_repeated_attack_increases_risk():

    src_ip = "192.168.100.10"

    memory.record(src_ip, 0.5, "MONITOR")
    memory.record(src_ip, 0.5, "MONITOR")
    memory.record(src_ip, 0.5, "MONITOR")

    result = decision_node(
        {
            "risk_score": 0.65,
            "src_ip": src_ip,
            "mode": "Hybrid_Memory_Threat",
        }
    )

    assert result["risk_score"] == pytest.approx(0.85)
    assert result["action"] == "BLOCK"
