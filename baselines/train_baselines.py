from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.ensemble import RandomForestClassifier

from preprocessing.preprocessor import transform_dataset


CALIBRATION_PATH = Path(
    "data/splits/ton_iot_network/calibration.csv"
)

TEST_PATH = Path(
    "data/splits/ton_iot_network/test.csv"
)

PREPROCESSOR_PATH = Path(
    "preprocessing/artifacts/ton_iot_network_preprocessor.joblib"
)

RESULTS_DIR = Path("results/baselines")


def load_labels(path: Path) -> pd.Series:
    return pd.read_csv(
        path,
        usecols=["label"],
    )["label"]


def evaluate_model(model, X_test, y_test) -> dict:
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    return {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(y_test, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, predictions, zero_division=0)
        ),
        "f1": float(
            f1_score(y_test, predictions, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y_test, probabilities)
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions,
        ).tolist(),
        "classification_report": classification_report(
            y_test,
            predictions,
            zero_division=0,
        ),
    }


def main() -> None:
    print("Loading transformed calibration data...")
    X_calibration = transform_dataset(
        CALIBRATION_PATH,
        PREPROCESSOR_PATH,
    )

    print("Loading transformed test data...")
    X_test = transform_dataset(
        TEST_PATH,
        PREPROCESSOR_PATH,
    )

    y_calibration = load_labels(CALIBRATION_PATH)
    y_test = load_labels(TEST_PATH)

    print()
    print("Calibration:", X_calibration.shape)
    print("Test:", X_test.shape)

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        ),
    }

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_results = {}

    for name, model in models.items():
        print()
        print("=" * 80)
        print(f"TRAINING: {name}")
        print("=" * 80)

        model.fit(
            X_calibration,
            y_calibration,
        )

        results = evaluate_model(
            model,
            X_test,
            y_test,
        )

        all_results[name] = results

        print(
            f"Accuracy : {results['accuracy']:.4f}"
        )
        print(
            f"Precision: {results['precision']:.4f}"
        )
        print(
            f"Recall   : {results['recall']:.4f}"
        )
        print(
            f"F1       : {results['f1']:.4f}"
        )
        print(
            f"ROC-AUC  : {results['roc_auc']:.4f}"
        )

        print("\nConfusion matrix:")
        print(results["confusion_matrix"])

        model_path = RESULTS_DIR / f"{name}.joblib"

        joblib.dump(
            model,
            model_path,
        )

        print("\nModel saved:", model_path)

    results_path = RESULTS_DIR / "metrics.json"

    results_path.write_text(
        json.dumps(
            all_results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("BASELINE COMPLETE")
    print("=" * 80)
    print("Results:", results_path)


if __name__ == "__main__":
    main()
