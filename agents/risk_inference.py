from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = PROJECT_ROOT / "results/rf_ids_model.joblib"

EXCLUDED_COLUMNS = {
    "label",
    "type",
    "_row_fingerprint",
    "src_ip",
    "dst_ip",
}


def load_artifact():
    return joblib.load(MODEL_PATH)


def calculate_risk(row: pd.DataFrame) -> float:
    if len(row) != 1:
        raise ValueError("calculate_risk expects exactly one input row")

    artifact = load_artifact()

    model = artifact["model"]
    features = artifact["features"]

    X = row.drop(
        columns=list(EXCLUDED_COLUMNS),
        errors="ignore",
    )

    X = pd.get_dummies(
        X,
        dummy_na=True,
    )

    X = X.reindex(
        columns=features,
        fill_value=0,
    )

    probability = float(
        model.predict_proba(X)[0, 1]
    )

    return max(0.0, min(1.0, probability))


if __name__ == "__main__":
    calibration_path = (
        PROJECT_ROOT
        / "data/splits/ton_iot_network/calibration.csv"
    )

    sample = pd.read_csv(
        calibration_path,
        nrows=1,
    )

    risk = calculate_risk(sample)

    print("=" * 80)
    print("RANDOM FOREST RISK INFERENCE TEST")
    print("=" * 80)
    print("RF probability:", risk)
    print("Valid:", 0.0 <= risk <= 1.0)
