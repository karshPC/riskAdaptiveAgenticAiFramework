from __future__ import annotations


def escalation_agent(state):

    action = state.get("action")
    memory_reason = state.get(
        "memory_reason",
        ""
    )

    if action == "BLOCK":
        severity = "CRITICAL"
    elif action == "RESTRICT":
        severity = "HIGH"
    else:
        severity = "LOW"

    return {
        "severity": severity,
        "escalation_reason": (
            f"Escalation generated. {memory_reason}"
        ),
    }
