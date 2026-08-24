from __future__ import annotations


def fuse_risk_scores(
    ml_score: float,
    rule_score: float,
) -> float:
    """
    Hybrid adaptive risk fusion.

    Combines ML anomaly detection
    with explainable rule-based scoring.
    """

    fused_score = (
        0.6 * ml_score +
        0.4 * rule_score
    )

    return round(
        max(0.0, min(1.0, fused_score)),
        4
    )
