from __future__ import annotations

from agents.explainer import generate_explanation


def explanation_node(state):
    explanation = generate_explanation(
        state["risk_score"],
        state["risk_level"],
        state["action"],
    )

    return {
        "explanation": explanation,
    }
