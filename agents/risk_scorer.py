from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CALIBRATION_PATH = (
    PROJECT_ROOT
    / "data/splits/ton_iot_network/calibration.csv"
)

PREPROCESSOR_PATH = (
    PROJECT_ROOT
    / "preprocessing/artifacts/"
    "ton_iot_network_preprocessor.joblib"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "results/risk_scorer.joblib"
)


EXCLUDED_COLUMNS = {
    "label",
    "type",
    "_row_fingerprint",
}


def load_calibration():
    calibration = pd.read_csv(CALIBRATION_PATH)

    artifact = joblib.load(PREPROCESSOR_PATH)
    preprocessor = artifact["preprocessor"]

    feature_columns = [
        column
        for column in calibration.columns
        if column not in EXCLUDED_COLUMNS
    ]

    X = calibration[feature_columns]

    return preprocessor.transform(X), preprocessor


def fit_risk_scorer():
    X, _ = load_calibration()

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X)

    calibration_decision_scores = model.decision_function(X)

    # IsolationForest:
    # higher decision score = more normal
    # lower decision score = more anomalous
    #
    # Therefore invert the direction before normalization.
    raw_risk = -calibration_decision_scores

    risk_min = float(raw_risk.min())
    risk_max = float(raw_risk.max())

    if risk_max <= risk_min:
        raise RuntimeError(
            "Risk-score normalization range is invalid."
        )

    artifact = {
        "model": model,
        "risk_min": risk_min,
        "risk_max": risk_max,
    }

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(artifact, MODEL_PATH)

    normalized_calibration_risk = (
        (raw_risk - risk_min)
        / (risk_max - risk_min)
    )

    print("=" * 80)
    print("RISK SCORER FIT COMPLETE")
    print("=" * 80)
    print("Calibration rows:", X.shape[0])
    print("Features:", X.shape[1])
    print("Raw risk min:", risk_min)
    print("Raw risk max:", risk_max)
    print(
        "Normalized calibration risk min:",
        normalized_calibration_risk.min(),
    )
    print(
        "Normalized calibration risk max:",
        normalized_calibration_risk.max(),
    )
    print("Model:", MODEL_PATH)


if __name__ == "__main__":
    fit_risk_scorer()
