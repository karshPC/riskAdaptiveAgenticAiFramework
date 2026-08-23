from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.risk_inference import calculate_risk
from agents.risk_levels import classify_risk

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def assess_risk(row: pd.DataFrame) -> dict:
    if len(row) != 1:
        raise ValueError("assess_risk expects exactly one input row")

    risk_score = calculate_risk(row)
    risk_level = classify_risk(risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
    }


if __name__ == "__main__":
    calibration_path = (
        PROJECT_ROOT
        / "data/splits/ton_iot_network/calibration.csv"
    )

    sample = pd.read_csv(calibration_path, nrows=1)

    result = assess_risk(sample)

    print("=" * 80)
    print("RISK ENGINE TEST")
    print("=" * 80)
    print("Risk score:", result["risk_score"])
    print("Risk level:", result["risk_level"])
