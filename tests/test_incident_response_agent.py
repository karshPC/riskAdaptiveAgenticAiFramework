from agents.incident_response_agent import PolicyBoundedIncidentAgent, SafetyGuardian


def test_low_risk_terminates_without_context_tools():
    result = PolicyBoundedIncidentAgent().investigate({"risk_score": 0.10})

    assert result["agent_planner"] == "deterministic_adaptive"
    assert [entry["tool"] for entry in result["agent_tool_trace"]] == ["evaluate_policy"]
    assert result["agent_proposed_action"] == "ALLOW"


def test_high_risk_uses_contextual_tools_and_requests_approval():
    result = PolicyBoundedIncidentAgent().investigate(
        {"risk_score": 0.85, "src_ip": "198.51.100.17", "asset_criticality": "HIGH"}
    )
    tools = [entry["tool"] for entry in result["agent_tool_trace"]]

    assert "get_source_history" in tools
    assert "query_threat_intelligence" in tools
    assert "request_human_approval" in tools
    assert result["agent_proposed_action"] == "BLOCK"


def test_guardian_replaces_unpermitted_agent_proposal():
    result = SafetyGuardian().validate({"risk_score": 0.10, "agent_proposed_action": "BLOCK"})

    assert result["action"] == "ALLOW"
    assert result["agent_proposal_accepted"] is False
    assert result["human_approval_required"] is False
