from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.risk_inference import calculate_risk
from agents.risk_levels import classify_risk


def risk_assessment_node(state):
    event = state["event"]

    risk_score = calculate_risk(event)
    risk_level = classify_risk(risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
    }
