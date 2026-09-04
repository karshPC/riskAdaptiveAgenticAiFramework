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
    ml_score: float | None = None,
    rule_score: float | None = None,
    ml_weight: float | None = None,
    rule_weight: float | None = None,
    memory_boost: float = 0.0,
    threat_boost: float = 0.0,
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

    audit_lines = []
    if ml_score is not None:
        audit_lines.append(f"ML score: {ml_score:.4f}")
    if rule_score is not None:
        audit_lines.append(f"Rule-derived score: {rule_score:.4f}")
    if ml_weight is not None and rule_weight is not None:
        audit_lines.append(
            f"Fusion weights: ML={ml_weight:.2f}, rule={rule_weight:.2f}"
        )
    audit_lines.append(f"Memory boost: {memory_boost:.4f}")
    audit_lines.append(f"Threat-intelligence boost: {threat_boost:.4f}")

    return (
        f"{risk_level.title()} risk detected with score {risk_score:.4f}.\n\n"
        "Security Decision Explanation\n\n"
        f"Risk Score: {risk_score:.4f}\n"
        f"Risk Level: {risk_level}\n"
        f"Decision: {action}\n"
        f"Severity: {severity}\n\n"
        "Audit signals:\n"
        + "\n".join(f"- {item}" for item in audit_lines)
        + "\n\n"
        "Reasoning:\n"
        f"{reason_text}\n\n"
        f"Response: {response_action}"
    )
