from __future__ import annotations

from agents.memory import memory


def memory_update_node(state):
    src_ip = state.get("src_ip")

    if src_ip is None:
        return {
            "previous_action": None,
        }

    memory.record(
        src_ip,
        state["risk_score"],
        state["action"],
    )

    repeated = memory.repeated_attack(src_ip)

    return {
        "previous_action": state["action"],
        "reason": (
            "Repeated attack detected."
            if repeated
            else "Event stored in risk memory."
        ),
    }
