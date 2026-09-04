from experiments.evaluate_agentic_workflow import SCENARIOS
from agents.incident_response_agent import PolicyBoundedIncidentAgent, SafetyGuardian


def test_every_scenario_has_a_policy_compliant_validated_action():
    agent = PolicyBoundedIncidentAgent()
    guardian = SafetyGuardian()

    for scenario in SCENARIOS:
        investigation = agent.investigate(scenario["state"])
        validated = guardian.validate({**scenario["state"], **investigation})
        assert validated["action"] == scenario["expected_action"]
