from agents.memory import RiskMemory
from memory.database import get_connection


def clear_memory():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM risk_events"
    )

    conn.commit()
    conn.close()


def test_memory_records_events():

    clear_memory()

    memory = RiskMemory()

    memory.record(
        "192.168.1.10",
        0.8,
        "MONITOR",
    )

    history = memory.get_history(
        "192.168.1.10"
    )

    assert len(history) == 1
    assert history[0]["action"] == "MONITOR"


def test_repeated_attack_detection():

    clear_memory()

    memory = RiskMemory()

    src_ip = "10.0.0.5"

    memory.record(src_ip, 0.5, "MONITOR")
    memory.record(src_ip, 0.5, "MONITOR")
    memory.record(src_ip, 0.5, "MONITOR")

    assert memory.repeated_attack(src_ip)
