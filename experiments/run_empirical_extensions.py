"""Reproducible empirical extensions for the RiskAdaptive detector.

This script keeps all evaluations separate from the frozen held-out result. It
uses leakage-safe fold-local preprocessing for cross-validation and records
when an out-of-time or cross-modality transfer test is not technically valid.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocessor import (
    EXCLUDED_COLUMNS,
    build_preprocessor,
)


SPLIT_DIR = PROJECT_ROOT / "data/splits/ton_iot_network"
RAW_NETWORK = PROJECT_ROOT / (
    "data/ton_iot/Train_Test_datasets/Train_Test_Network_dataset/"
    "train_test_network.csv"
)
RESULTS_PATH = PROJECT_ROOT / "experiments/results/empirical_extensions.json"
THRESHOLD_FIGURE_PATH = PROJECT_ROOT / "experiments/results/cost_sensitive_threshold.png"
BASELINES_PATH = PROJECT_ROOT / "results/baselines/metrics.json"
MULTICLASS_PATH = PROJECT_ROOT / "results/baselines/multiclass_random_forest.joblib"


def metrics(y_true: pd.Series, predicted: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, predicted)),
        "precision": float(precision_score(y_true, predicted, zero_division=0)),
        "recall": float(recall_score(y_true, predicted, zero_division=0)),
        "f1": float(f1_score(y_true, predicted, zero_division=0)),
    }


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=list(EXCLUDED_COLUMNS), errors="ignore")


def rf_configuration() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )


def cross_validate(df: pd.DataFrame, folds: int = 5) -> dict:
    """Run stratified CV with preprocessing fitted inside each fold."""
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    y = df["label"].astype(int)
    X = feature_frame(df)
    fold_metrics: list[dict[str, float]] = []

    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y), start=1):
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]
        preprocessor, _, _ = build_preprocessor(train_df)
        X_train = preprocessor.fit_transform(feature_frame(train_df))
        X_test = preprocessor.transform(feature_frame(test_df))
        model = rf_configuration()
        model.fit(X_train, train_df["label"])
        fold_result = metrics(test_df["label"], model.predict(X_test))
        fold_result["fold"] = fold
        fold_metrics.append(fold_result)

    summary: dict[str, dict[str, float]] = {}
    for name in ("accuracy", "precision", "recall", "f1"):
        values = np.array([item[name] for item in fold_metrics], dtype=float)
        summary[name] = {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)),
        }
    return {"folds": folds, "seed": 42, "fold_metrics": fold_metrics, "summary": summary}


def fit_isolation_forest(
    calibration: pd.DataFrame,
    test: pd.DataFrame,
) -> dict:
    """Fit a normal-only Isolation Forest and tune its score cut-off on calibration."""
    preprocessor, _, _ = build_preprocessor(calibration)
    X_calibration = preprocessor.fit_transform(feature_frame(calibration))
    X_test = preprocessor.transform(feature_frame(test))
    normal_mask = calibration["label"].eq(0).to_numpy()
    model = IsolationForest(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_calibration[normal_mask])
    calibration_scores = -model.score_samples(X_calibration)
    test_scores = -model.score_samples(X_test)
    candidate_thresholds = np.unique(np.quantile(calibration_scores, np.linspace(0.01, 0.99, 199)))
    best_threshold = max(
        candidate_thresholds,
        key=lambda threshold: f1_score(
            calibration["label"], calibration_scores >= threshold, zero_division=0
        ),
    )
    prediction = (test_scores >= best_threshold).astype(int)
    return {
        "training": "normal-only calibration subset",
        "n_estimators": 200,
        "threshold_tuned_on_calibration": float(best_threshold),
        "metrics": metrics(test["label"], prediction),
    }


def threshold_cost_analysis(
    y_true: pd.Series,
    probabilities: np.ndarray,
    false_block_cost: int = 5,
    false_allow_cost: int = 1,
) -> dict:
    rows = []
    for threshold in np.arange(0.01, 1.00, 0.01):
        predicted = probabilities >= threshold
        false_blocks = int(((y_true == 0) & predicted).sum())
        false_allows = int(((y_true == 1) & ~predicted).sum())
        rows.append({
            "threshold": round(float(threshold), 2),
            "false_blocks": false_blocks,
            "false_allows": false_allows,
            "cost": false_blocks * false_block_cost + false_allows * false_allow_cost,
        })
    optimum = min(rows, key=lambda item: item["cost"])
    return {
        "cost_matrix": {"false_block": false_block_cost, "false_allow": false_allow_cost},
        "optimum": optimum,
        "curve": rows,
        "scope": "binary alert threshold only, not a claim of operational response cost calibration",
    }


def save_threshold_figure(analysis: dict) -> None:
    curve = analysis["curve"]
    fig, axis = plt.subplots(figsize=(7.0, 3.8))
    axis.plot(
        [item["threshold"] for item in curve],
        [item["cost"] for item in curve],
        color="#007f9e",
        linewidth=2,
    )
    optimum = analysis["optimum"]
    axis.scatter([optimum["threshold"]], [optimum["cost"]], color="#d95f02", zorder=3)
    axis.annotate(
        f"minimum: t={optimum['threshold']:.2f}, cost={optimum['cost']}",
        xy=(optimum["threshold"], optimum["cost"]),
        xytext=(0.35, max(item["cost"] for item in curve) * 0.7),
        arrowprops={"arrowstyle": "->", "color": "#555555"},
    )
    axis.set_xlabel("Binary alert threshold")
    axis.set_ylabel("Weighted error cost")
    axis.set_title("Held-out threshold cost analysis, false Block = 5, false Allow = 1")
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(THRESHOLD_FIGURE_PATH, dpi=220)
    plt.close(fig)


def robustness_audit(
    calibration: pd.DataFrame,
    test: pd.DataFrame,
    model: RandomForestClassifier,
    preprocessor,
) -> dict:
    """Test bounded raw feature changes, clipped to observed benign ranges."""
    candidates = ["duration", "src_pkts", "dst_pkts", "src_bytes", "dst_bytes"]
    available = [name for name in candidates if name in test.columns]
    malicious = test.loc[test["label"].eq(1)].copy()
    baseline_scores = model.predict_proba(preprocessor.transform(feature_frame(malicious)))[:, 1]
    baseline_detected = baseline_scores >= 0.5
    benign = calibration.loc[calibration["label"].eq(0)]
    scenarios = []
    for feature in available:
        low = float(benign[feature].min())
        high = float(benign[feature].max())
        for delta in (-0.2, -0.1, 0.1, 0.2):
            altered = malicious.copy()
            altered[feature] = (altered[feature].astype(float) * (1 + delta)).clip(low, high)
            scores = model.predict_proba(preprocessor.transform(feature_frame(altered)))[:, 1]
            detected = scores >= 0.5
            scenarios.append({
                "feature": feature,
                "relative_change": delta,
                "benign_clip_range": [low, high],
                "baseline_detected": int(baseline_detected.sum()),
                "detected_after_perturbation": int(detected.sum()),
                "detected_to_missed_flips": int((baseline_detected & ~detected).sum()),
            })
    return {
        "sample": "all held-out malicious records",
        "threshold": 0.5,
        "scenarios": scenarios,
        "interpretation": "bounded feature-sensitivity audit, not an attack-realism or certified-robustness claim",
    }


def multiclass_evaluation(calibration: pd.DataFrame, test: pd.DataFrame) -> dict:
    preprocessor, _, _ = build_preprocessor(calibration)
    X_calibration = preprocessor.fit_transform(feature_frame(calibration))
    X_test = preprocessor.transform(feature_frame(test))
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1, class_weight="balanced")
    model.fit(X_calibration, calibration["type"])
    predicted = model.predict(X_test)
    rows = []
    for category in sorted(test["type"].unique()):
        truth = test["type"].eq(category)
        pred = predicted == category
        rows.append({
            "category": str(category),
            "support": int(truth.sum()),
            **metrics(truth.astype(int), pred.astype(int)),
        })
    joblib.dump({"model": model, "preprocessor": preprocessor}, MULTICLASS_PATH)
    return {"model": "200-tree multiclass Random Forest", "categories": rows}


def generalization_feasibility(raw_network: pd.DataFrame) -> dict:
    windows_path = PROJECT_ROOT / "data/ton_iot/Train_Test_datasets/Train_Test_Windows_dataset/Train_Test_Windows_10.csv"
    windows_columns = pd.read_csv(windows_path, nrows=1).columns.tolist()
    network_features = set(feature_frame(raw_network).columns)
    overlap = sorted(network_features.intersection(windows_columns))
    timestamp_columns = [column for column in raw_network.columns if "time" in column.lower()]
    return {
        "out_of_time_split": {
            "status": "not_run",
            "reason": "The network CSV has no timestamp-like column.",
            "timestamp_columns": timestamp_columns,
        },
        "windows_transfer": {
            "status": "not_run",
            "reason": "The deployed network feature schema is incompatible with Windows telemetry.",
            "shared_raw_feature_columns": overlap,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--skip-cv", action="store_true")
    args = parser.parse_args()

    calibration = pd.read_csv(SPLIT_DIR / "calibration.csv", low_memory=False)
    test = pd.read_csv(SPLIT_DIR / "test.csv", low_memory=False)
    raw_network = pd.read_csv(RAW_NETWORK, low_memory=False)
    preprocessor, _, _ = build_preprocessor(calibration)
    X_calibration = preprocessor.fit_transform(feature_frame(calibration))
    X_test = preprocessor.transform(feature_frame(test))
    binary_rf = rf_configuration()
    binary_rf.fit(X_calibration, calibration["label"])
    probabilities = binary_rf.predict_proba(X_test)[:, 1]

    cost_analysis = threshold_cost_analysis(test["label"], probabilities)
    save_threshold_figure(cost_analysis)
    payload = {
        "dataset": "TON_IoT network",
        "frozen_split": {"calibration_rows": len(calibration), "test_rows": len(test), "seed": 42},
        "binary_random_forest": metrics(test["label"], binary_rf.predict(X_test)),
        "isolation_forest": fit_isolation_forest(calibration, test),
        "cost_sensitive_threshold": cost_analysis,
        "robustness": robustness_audit(calibration, test, binary_rf, preprocessor),
        "multiclass": multiclass_evaluation(calibration, test),
        "generalization_feasibility": generalization_feasibility(raw_network),
    }
    if not args.skip_cv:
        payload["stratified_cross_validation"] = cross_validate(raw_network, args.folds)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved {RESULTS_PATH}")


if __name__ == "__main__":
    main()
