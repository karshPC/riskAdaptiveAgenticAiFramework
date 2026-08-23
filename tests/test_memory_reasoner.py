import pytest

from agents.memory_reasoner import memory_reasoner
from agents.memory import memory


def test_memory_reasoning_detects_repeat_attack():

    src_ip = "172.16.0.10"

    memory.record(
        src_ip,
        0.8,
        "BLOCK",
    )

    memory.record(
        src_ip,
        0.8,
        "BLOCK",
    )

    memory.record(
        src_ip,
        0.8,
        "BLOCK",
    )

    result = memory_reasoner.analyze(src_ip)

    assert result["risk_boost"] == pytest.approx(0.30)
    assert "Repeated attack" in result["reason"]
