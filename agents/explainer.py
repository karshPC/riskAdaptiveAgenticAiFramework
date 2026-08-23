from __future__ import annotations


def generate_explanation(
    risk_score: float,
    risk_level: str,
    action: str,
    memory_reason: str = "",
    threat_reason: str = "",
    severity: str = "",
    escalation_reason: str = "",
    response_action: str = "",
) -> str:

    reasons = []

    if memory_reason:
        reasons.append(f"Memory analysis: {memory_reason}")

    if threat_reason:
        reasons.append(f"Threat intelligence: {threat_reason}")

    if escalation_reason:
        reasons.append(f"Escalation: {escalation_reason}")

    reason_text = "\n".join(
        f"- {item}" for item in reasons
    )

    return (
        f"{risk_level.title()} risk detected with score {risk_score:.4f}.\n\n"
        "Security Decision Explanation\n\n"
        f"Risk Score: {risk_score:.4f}\n"
        f"Risk Level: {risk_level}\n"
        f"Decision: {action}\n"
        f"Severity: {severity}\n\n"
        "Reasoning:\n"
        f"{reason_text}\n\n"
        f"Response: {response_action}"
    )
