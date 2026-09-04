from __future__ import annotations


ATTACK_SCORES = {
    "scan": 0.75,
    "malware": 0.95,
    "intrusion": 0.90,
    "ddos": 0.85,
    "normal": 0.05,
}


def calculate_risk(event) -> tuple[float, str]:
    attack_type = (event.attack_type or "normal").lower()

    score = ATTACK_SCORES.get(
        attack_type,
        0.40
    )

    if score >= 0.85:
        level = "CRITICAL"
    elif score >= 0.60:
        level = "HIGH"
    elif score >= 0.30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level
