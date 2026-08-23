from agents.memory import RiskMemory


def test_memory_records_events():
    memory = RiskMemory()

    memory.record(
        "192.168.1.10",
        0.8,
        "MONITOR",
    )

    history = memory.get_history("192.168.1.10")

    assert len(history) == 1
    assert history[0]["action"] == "MONITOR"


def test_repeated_attack_detection():
    memory = RiskMemory()

    for _ in range(3):
        memory.record(
            "192.168.1.10",
            0.9,
            "BLOCK",
        )

    assert memory.repeated_attack(
        "192.168.1.10"
    )


def test_unknown_ip_has_no_history():
    memory = RiskMemory()

    assert memory.get_history(
        "10.0.0.1"
    ) == []
