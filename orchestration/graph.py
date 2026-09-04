from __future__ import annotations

from pathlib import Path
import sys

from langgraph.graph import END, StateGraph

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.state import RiskAgentState
from orchestration.nodes import risk_assessment_node
from orchestration.explanation_node import explanation_node
from orchestration.memory_node import memory_update_node
from agents.memory_reasoner import memory_reasoner
from agents.threat_intelligence import threat_intelligence_agent
from agents.escalation import escalation_agent
from agents.response import response_agent
from agents.risk_levels import classify_risk
from agents.incident_response_agent import incident_response_agent, safety_guardian


def decision_node(state: RiskAgentState):
    score = state["risk_score"]

    mode = state.get(
        "mode",
        "ML_only"
    )

    src_ip = state.get("src_ip")

    memory_reason = "Memory disabled."
    threat_reason = "Threat intelligence disabled."
    memory_boost = 0.0
    threat_boost = 0.0

    if mode in [
        "Hybrid_Memory_Threat"
    ]:
        if src_ip:
            memory_result = memory_reasoner.analyze(src_ip)

            memory_boost = memory_result["risk_boost"]
            score += memory_boost
            memory_reason = memory_result["reason"]

            threat_result = threat_intelligence_agent.analyze(src_ip)

            threat_boost = threat_result["threat_boost"]
            score += threat_boost
            threat_reason = threat_result["threat_reason"]

    score = min(score, 1.0)
    risk_level = classify_risk(score)

    if score >= 0.80:
        action = "BLOCK"
    elif score >= 0.60:
        action = "RESTRICT"
    elif score >= 0.30:
        action = "MONITOR"
    else:
        action = "ALLOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "action": action,
        "reason": f"Adaptive risk score {score:.4f} processed by {mode}.",
        "memory_reason": memory_reason,
        "threat_reason": threat_reason,
        "memory_boost": memory_boost,
        "threat_boost": threat_boost,
    }


def agent_investigation_node(state: RiskAgentState):
    return incident_response_agent.investigate(state)


def safety_guardian_node(state: RiskAgentState):
    return safety_guardian.validate(state)


def build_risk_graph():
    graph = StateGraph(RiskAgentState)

    graph.add_node(
        "risk_assessment",
        risk_assessment_node,
    )

    graph.add_node(
        "agent_investigation",
        agent_investigation_node,
    )

    graph.add_node(
        "decision",
        decision_node,
    )

    graph.add_node(
        "safety_guardian",
        safety_guardian_node,
    )

    graph.add_node(
        "memory_update",
        memory_update_node,
    )

    graph.add_node(
        "escalation",
        escalation_agent,
    )

    graph.add_node(
        "response",
        response_agent,
    )

    graph.add_node(
        "explainer",
        explanation_node,
    )

    graph.set_entry_point("risk_assessment")

    graph.add_edge(
        "risk_assessment",
        "agent_investigation",
    )

    graph.add_edge(
        "agent_investigation",
        "decision",
    )

    graph.add_edge(
        "decision",
        "safety_guardian",
    )

    graph.add_edge(
        "safety_guardian",
        "memory_update",
    )

    graph.add_edge(
        "memory_update",
        "escalation",
    )

    graph.add_edge(
        "escalation",
        "response",
    )

    graph.add_edge(
        "response",
        "explainer",
    )

    graph.add_edge(
        "explainer",
        END,
    )

    return graph.compile()


risk_graph = build_risk_graph()


if __name__ == "__main__":
    result = risk_graph.invoke(
        {
            "risk_score": 0.90,
            "risk_level": "CRITICAL",
            "attack_type": "scanning",
        }
    )

    print("=" * 80)
    print("LANGGRAPH RISK WORKFLOW TEST")
    print("=" * 80)
    print(result)
