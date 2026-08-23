from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PREPROCESSOR_PATH = (
    PROJECT_ROOT
    / "preprocessing/artifacts/"
    "ton_iot_network_preprocessor.joblib"
)

MODEL_PATH = PROJECT_ROOT / "results/risk_scorer.joblib"

EXCLUDED_COLUMNS = {
    "label",
    "type",
    "_row_fingerprint",
}


def load_artifacts():
    preprocessor_artifact = joblib.load(PREPROCESSOR_PATH)
    risk_artifact = joblib.load(MODEL_PATH)

    return (
        preprocessor_artifact["preprocessor"],
        risk_artifact["model"],
        risk_artifact["risk_min"],
        risk_artifact["risk_max"],
    )


def calculate_risk(row: pd.DataFrame) -> float:
    (
        preprocessor,
        model,
        risk_min,
        risk_max,
    ) = load_artifacts()

    feature_columns = [
        column
        for column in row.columns
        if column not in EXCLUDED_COLUMNS
    ]

    X = preprocessor.transform(row[feature_columns])

    decision_score = float(model.decision_function(X)[0])

    raw_risk = -decision_score

    normalized_risk = (
        (raw_risk - risk_min)
        / (risk_max - risk_min)
    )

    return float(max(0.0, min(1.0, normalized_risk)))


if __name__ == "__main__":
    calibration_path = (
        PROJECT_ROOT
        / "data/splits/ton_iot_network/calibration.csv"
    )

    sample = pd.read_csv(calibration_path, nrows=1)

    risk = calculate_risk(sample)

    print("=" * 80)
    print("RISK INFERENCE TEST")
    print("=" * 80)
    print("Input rows:", len(sample))
    print("Risk score:", risk)
    print("Risk range valid:", 0.0 <= risk <= 1.0)
