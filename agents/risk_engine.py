from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.risk_inference import calculate_risk as ml_risk
from agents.risk_model import calculate_risk as rule_risk
from agents.risk_fusion import fuse_risk_scores
from agents.risk_levels import classify_risk


class EventAdapter:
    def __init__(self, row):
        self.src_bytes = row.get("src_bytes", 0)
        self.dst_bytes = row.get("dst_bytes", 0)

        self.src_pkts = row.get("src_pkts", 0)
        self.dst_pkts = row.get("dst_pkts", 0)

        self.duration = row.get("duration", 0)

        self.conn_state = row.get(
            "conn_state",
            "",
        )

        self.service = row.get(
            "service",
            "",
        )

        self.dst_port = row.get(
            "dst_port",
            0,
        )


def assess_risk(
    row: pd.DataFrame,
    ml_weight: float = 1.0,
) -> dict:

    if len(row) != 1:
        raise ValueError(
            "assess_risk expects exactly one input row"
        )

    ml_score = ml_risk(row)

    event = EventAdapter(
        row.iloc[0].to_dict()
    )

    rule_score, rule_level = rule_risk(event)

    # Always calculate the transparent rule signal, even when its default
    # fusion weight is zero, so the result remains available for audit.
    risk_score = fuse_risk_scores(
        ml_score,
        rule_score,
        ml_weight=ml_weight,
    )

    risk_level = classify_risk(
        risk_score
    )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "ml_score": ml_score,
        "rule_score": rule_score,
        "rule_level": rule_level,
        "ml_weight": ml_weight,
        "rule_weight": 1.0 - ml_weight,
    }


if __name__ == "__main__":

    calibration_path = (
        PROJECT_ROOT
        / "data/splits/ton_iot_network/calibration.csv"
    )

    sample = pd.read_csv(
        calibration_path,
        nrows=1,
    )

    result = assess_risk(sample)

    print("=" * 80)
    print("RISK ENGINE TEST")
    print("=" * 80)
    print(result)
