from __future__ import annotations


def generate_explanation(
    risk_score: float,
    risk_level: str,
    action: str,
) -> str:

    if risk_level == "CRITICAL":
        return (
            f"Critical risk detected with score {risk_score:.4f}. "
            f"Automated action {action} was triggered due to severe anomaly indicators."
        )

    if risk_level == "HIGH":
        return (
            f"High risk detected with score {risk_score:.4f}. "
            f"Action {action} recommended because suspicious activity was identified."
        )

    if risk_level == "MEDIUM":
        return (
            f"Moderate risk detected with score {risk_score:.4f}. "
            f"Action {action} applied for monitoring."
        )

    return (
        f"Low risk detected with score {risk_score:.4f}. "
        f"Action {action} allowed normal operation."
    )
