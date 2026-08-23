from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.risk import RiskContext
from agents.decision_engine import DECISIONS


def decide_from_context(context: RiskContext) -> dict:
    action = DECISIONS[context.risk_level]

    reason = (
        f"Risk score {context.risk_score:.4f} classified as "
        f"{context.risk_level}."
    )

    return {
        "risk_score": context.risk_score,
        "risk_level": context.risk_level,
        "action": action,
        "reason": reason,
    }


if __name__ == "__main__":
    context = RiskContext(
        risk_score=0.75,
        risk_level="HIGH",
        attack_type="scanning",
        src_ip="192.168.1.10",
        dst_ip="10.0.0.5",
        proto="tcp",
        service="http",
        previous_action="MONITOR",
    )

    result = decide_from_context(context)

    print("=" * 80)
    print("CONTEXT DECISION ENGINE TEST")
    print("=" * 80)
    print(result)
