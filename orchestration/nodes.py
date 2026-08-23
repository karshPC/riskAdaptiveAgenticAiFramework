from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.inference import run_inference


def risk_assessment_node(state):
    event = state["event"]

    result = run_inference(event)

    return {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
    }
