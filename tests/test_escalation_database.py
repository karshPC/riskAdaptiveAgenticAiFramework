from memory.escalation_database import EscalationDatabase


def test_escalation_persistence():

    db = EscalationDatabase()

    db.record(
        "192.168.1.50",
        0.95,
        "BLOCK",
        "CRITICAL",
        "Repeated attack detected.",
    )

    history = db.get_all()

    assert len(history) >= 1

    latest = history[-1]

    assert latest["action"] == "BLOCK"
    assert latest["severity"] == "CRITICAL"
    assert latest["risk_score"] == 0.95
