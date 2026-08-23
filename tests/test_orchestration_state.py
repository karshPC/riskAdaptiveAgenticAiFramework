from orchestration.state import RiskAgentState


def test_risk_agent_state_accepts_complete_context():
    state: RiskAgentState = {
        "risk_score": 0.75,
        "risk_level": "HIGH",
        "attack_type": "scanning",
        "src_ip": "192.168.1.10",
        "dst_ip": "10.0.0.5",
        "proto": "tcp",
        "service": "http",
        "previous_action": "MONITOR",
        "action": "RESTRICT",
        "reason": "Risk score 0.7500 classified as HIGH.",
    }

    assert state["risk_score"] == 0.75
    assert state["risk_level"] == "HIGH"
    assert state["action"] == "RESTRICT"


def test_risk_agent_state_allows_partial_workflow_state():
    state: RiskAgentState = {
        "risk_score": 0.20,
        "risk_level": "LOW",
    }

    assert state["risk_score"] == 0.20
    assert state["risk_level"] == "LOW"
    assert "action" not in state
