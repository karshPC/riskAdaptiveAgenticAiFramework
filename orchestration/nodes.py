from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pandas as pd

from agents.risk_engine import assess_risk


def risk_assessment_node(state):

    event = state["event"]

    # Case 1: Dataset already provides ML feature dataframe
    if isinstance(event, pd.DataFrame):
        result = assess_risk(event)

        return {
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "ml_score": result["ml_score"],
            "rule_score": result["rule_score"],
            "rule_level": result["rule_level"],
            "ml_weight": result["ml_weight"],
            "rule_weight": result["rule_weight"],
        }


    # Case 2: NetworkEvent / API object
    row = pd.DataFrame(
        [
            {
                "src_ip": getattr(event, "src_ip", None),
                "dst_ip": getattr(event, "dst_ip", None),
                "protocol": getattr(
                    event,
                    "protocol",
                    getattr(event, "proto", None)
                ),
                "attack_type": getattr(
                    event,
                    "attack_type",
                    "normal"
                ),
            }
        ]
    )


    # Hybrid engine requires ML feature columns.
    # For lightweight events fallback to rule engine.
    try:
        result = assess_risk(row)

        return {
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "ml_score": result["ml_score"],
            "rule_score": result["rule_score"],
            "rule_level": result["rule_level"],
            "ml_weight": result["ml_weight"],
            "rule_weight": result["rule_weight"],
        }

    except Exception:

        attack_type = getattr(
            event,
            "attack_type",
            "normal"
        )

        from agents.risk_model import calculate_risk

        score, level = calculate_risk(
            type(
                "Event",
                (),
                {
                    "attack_type": attack_type
                }
            )()
        )

        return {
            "risk_score": score,
            "risk_level": level,
        }
