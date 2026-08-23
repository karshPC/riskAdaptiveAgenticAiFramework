from __future__ import annotations

from agents.explainer import generate_explanation


def explanation_node(state):

    explanation = generate_explanation(
        state.get("risk_score", 0.0),
        state.get("risk_level", "UNKNOWN"),
        state.get("action", "UNKNOWN"),
        state.get("memory_reason", ""),
        state.get("threat_reason", ""),
        state.get("severity", ""),
        state.get("escalation_reason", ""),
        state.get("response_action", ""),
    )

    return {
        "explanation": explanation,
    }
