from __future__ import annotations


def response_agent(state):
    action = state.get("action")

    if action == "BLOCK":
        response = "Firewall block rule generated."

    elif action == "RESTRICT":
        response = "Traffic rate limit applied."

    elif action == "MONITOR":
        response = "Enhanced monitoring enabled."

    else:
        response = "No response action required."

    return {
        "response_action": response,
    }
