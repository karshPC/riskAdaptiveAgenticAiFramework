from agents.memory import RiskMemory


def test_sqlite_memory_persistence():

    memory = RiskMemory()

    src_ip = "10.10.10.10"

    memory.record(
        src_ip,
        0.9,
        "BLOCK",
    )

    history = memory.get_history(src_ip)

    assert len(history) >= 1
    assert history[-1]["action"] == "BLOCK"
    assert history[-1]["risk_score"] == 0.9
