from __future__ import annotations

from agents.explainer import generate_explanation
from agents.llm_explainer import gemini_narrative_explainer


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
        state.get("ml_score"),
        state.get("rule_score"),
        state.get("ml_weight"),
        state.get("rule_weight"),
        state.get("memory_boost", 0.0),
        state.get("threat_boost", 0.0),
    )
    narrative = gemini_narrative_explainer.narrate(state)

    return {
        "explanation": explanation,
        "llm_narrative": narrative.narrative,
        "llm_narrative_status": narrative.status,
        "llm_narrative_model": narrative.model,
    }
