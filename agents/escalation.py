from __future__ import annotations

from memory.escalation_database import escalation_db


def escalation_agent(state):

    action = state.get("action")

    memory_reason = state.get(
        "memory_reason",
        ""
    )

    risk_score = state.get(
        "risk_score",
        0.0
    )

    src_ip = state.get(
        "src_ip",
        "unknown"
    )

    if action == "BLOCK":
        severity = "CRITICAL"
    elif action == "RESTRICT":
        severity = "HIGH"
    else:
        severity = "LOW"

    escalation_reason = (
        f"Escalation generated. {memory_reason}"
    )

    escalation_db.record(
        src_ip,
        risk_score,
        action,
        severity,
        escalation_reason,
    )

    return {
        "severity": severity,
        "escalation_reason": escalation_reason,
    }
