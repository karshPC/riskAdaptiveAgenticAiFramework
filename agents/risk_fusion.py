from __future__ import annotations


def fuse_risk_scores(
    ml_score: float,
    rule_score: float,
    ml_weight: float = 1.0,
) -> float:
    """
    Fuse ML and transparent rule risk.

    The deployed default preserves the detector score (``ml_weight=1.0``).
    The rule score is still supplied and can be logged or enabled by an
    operator through a non-default weight.

    ml_weight:
        Weight assigned to the Random Forest score.

    rule_weight:
        Remaining weight assigned to the rule score.
    """

    if not 0.0 <= ml_weight <= 1.0:
        raise ValueError("ml_weight must be between 0 and 1")

    rule_weight = 1.0 - ml_weight

    score = (
        ml_weight * float(ml_score)
        + rule_weight * float(rule_score)
    )

    return max(0.0, min(1.0, score))


if __name__ == "__main__":
    print(fuse_risk_scores(0.82, 0.35))
