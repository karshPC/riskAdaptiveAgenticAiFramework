from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.risk_levels import classify_risk


DECISIONS = {
    "LOW": "ALLOW",
    "MEDIUM": "MONITOR",
    "HIGH": "RESTRICT",
    "CRITICAL": "BLOCK",
}


def make_decision(risk_score: float) -> dict:
    risk_level = classify_risk(risk_score)
    action = DECISIONS[risk_level]

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "action": action,
    }


if __name__ == "__main__":
    test_scores = [0.10, 0.45, 0.70, 0.90]

    print("=" * 80)
    print("ADAPTIVE DECISION ENGINE TEST")
    print("=" * 80)

    for score in test_scores:
        result = make_decision(score)

        print(
            f"score={result['risk_score']:.2f} "
            f"level={result['risk_level']:8} "
            f"action={result['action']}"
        )
