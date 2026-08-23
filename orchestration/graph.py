from __future__ import annotations

from pathlib import Path
import sys

from langgraph.graph import END, StateGraph

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.state import RiskAgentState
from orchestration.nodes import risk_assessment_node


def decision_node(state: RiskAgentState):
    score = state["risk_score"]

    if score >= 0.80:
        action = "BLOCK"
    elif score >= 0.60:
        action = "RESTRICT"
    elif score >= 0.30:
        action = "MONITOR"
    else:
        action = "ALLOW"

    return {
        "action": action,
        "reason": f"Risk score {score:.4f} processed by decision node.",
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

    graph.set_entry_point("risk_assessment")

    graph.add_edge(
        "risk_assessment",
        "decision",
    )

    graph.add_edge(
        "decision",
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
