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


def decision_node(state: RiskAgentState):
    score = state["risk_score"]

    src_ip = state.get("src_ip")

    memory_reason = "No memory history found."
    threat_reason = "No threat intelligence match found."

    if src_ip:
        memory_result = memory_reasoner.analyze(src_ip)

        score += memory_result["risk_boost"]
        memory_reason = memory_result["reason"]

        threat_result = threat_intelligence_agent.analyze(src_ip)

        score += threat_result["threat_boost"]
        threat_reason = threat_result["threat_reason"]

    score = min(score, 1.0)

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
        "action": action,
        "reason": f"Adaptive risk score {score:.4f} processed by decision node.",
        "memory_reason": memory_reason,
        "threat_reason": threat_reason,
    }


def build_risk_graph():
    graph = StateGraph(RiskAgentState)

    graph.add_node(
        "risk_assessment",
        risk_assessment_node,
    )

    graph.add_node(
        "decision",
        decision_node,
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
        "explainer",
        explanation_node,
    )

    graph.set_entry_point("risk_assessment")

    graph.add_edge(
        "risk_assessment",
        "decision",
    )

    graph.add_edge(
        "decision",
        "memory_update",
    )

    graph.add_edge(
        "memory_update",
        "escalation",
    )

    graph.add_edge(
        "escalation",
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
