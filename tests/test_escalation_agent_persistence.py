from agents.escalation import escalation_agent
from memory.escalation_database import escalation_db


def test_escalation_agent_persists_block():

    escalation_agent(
        {
            "src_ip": "10.0.0.99",
            "risk_score": 0.95,
            "action": "BLOCK",
            "memory_reason": "Repeated attack detected."
        }
    )

    history = escalation_db.get_all()

    latest = history[-1]

    assert latest["src_ip"] == "10.0.0.99"
    assert latest["action"] == "BLOCK"
    assert latest["severity"] == "CRITICAL"
