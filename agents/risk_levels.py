from __future__ import annotations


def classify_risk(risk_score: float) -> str:
    if not 0.0 <= risk_score <= 1.0:
        raise ValueError("risk_score must be between 0.0 and 1.0")

    if risk_score < 0.30:
        return "LOW"

    if risk_score < 0.60:
        return "MEDIUM"

    if risk_score < 0.80:
        return "HIGH"

    return "CRITICAL"


if __name__ == "__main__":
    test_scores = [0.0, 0.29, 0.30, 0.59, 0.60, 0.79, 0.80, 1.0]

    print("=" * 80)
    print("RISK LEVEL CLASSIFICATION TEST")
    print("=" * 80)

    for score in test_scores:
        print(f"{score:.2f} -> {classify_risk(score)}")
