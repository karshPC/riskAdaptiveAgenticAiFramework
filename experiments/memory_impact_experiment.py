from __future__ import annotations

from agents.memory import memory
from agents.memory_reasoner import MemoryReasoner


TEST_IP = "192.0.2.250"


def clear_test_history():
    from memory.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM risk_events WHERE src_ip = ?",
        (TEST_IP,),
    )

    conn.commit()
    conn.close()


def main():
    print("=" * 80)
    print("RISKADAPTIVE MEMORY IMPACT EXPERIMENT")
    print("=" * 80)

    reasoner = MemoryReasoner()

    # Start with no historical events.
    clear_test_history()

    print("\n1. WITHOUT HISTORICAL MEMORY")
    baseline = reasoner.analyze(TEST_IP)
    print(baseline)

    # Add three previous high-risk events.
    memory.record(TEST_IP, 0.85, "BLOCK")
    memory.record(TEST_IP, 0.80, "BLOCK")
    memory.record(TEST_IP, 0.75, "BLOCK")

    print("\n2. WITH HISTORICAL MEMORY")
    historical = reasoner.analyze(TEST_IP)
    print(historical)

    print("\n" + "=" * 80)
    print("MEMORY IMPACT")
    print("=" * 80)

    print("Baseline risk boost:", baseline.get("risk_boost"))
    print("Historical risk boost:", historical.get("risk_boost"))
    print("Historical events:", len(memory.get_history(TEST_IP)))

    print("\nRisk boost change:",
          historical.get("risk_boost", 0.0)
          - baseline.get("risk_boost", 0.0))

    # Cleanup experiment data.
    clear_test_history()

    print("\nExperiment memory cleaned up.")
    print("=" * 80)


if __name__ == "__main__":
    main()
