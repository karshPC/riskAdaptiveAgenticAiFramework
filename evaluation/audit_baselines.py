from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CALIBRATION_PATH = (
    PROJECT_ROOT
    / "data/splits/ton_iot_network/calibration.csv"
)

TEST_PATH = (
    PROJECT_ROOT
    / "data/splits/ton_iot_network/test.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "results/baselines/random_forest.joblib"
)

PREPROCESSOR_PATH = (
    PROJECT_ROOT
    / "preprocessing/artifacts/"
    "ton_iot_network_preprocessor.joblib"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "results/baselines/robustness_audit.json"
)


EXCLUDED_COLUMNS = {
    "label",
    "type",
    "_row_fingerprint",
}


def main() -> None:
    calibration = pd.read_csv(CALIBRATION_PATH)
    test = pd.read_csv(TEST_PATH)

    model = joblib.load(MODEL_PATH)
    artifact = joblib.load(PREPROCESSOR_PATH)

    preprocessor = artifact["preprocessor"]

    # Exact row overlap.
    calibration_fingerprints = set(
        calibration["_row_fingerprint"].astype("uint64")
    )
    test_fingerprints = set(
        test["_row_fingerprint"].astype("uint64")
    )

    exact_overlap = calibration_fingerprints.intersection(
        test_fingerprints
    )

    # Feature-only duplicates within each split.
    feature_columns = [
        column
        for column in calibration.columns
        if column not in EXCLUDED_COLUMNS
    ]

    calibration_feature_duplicates = int(
        calibration.duplicated(
            subset=feature_columns
        ).sum()
    )

    test_feature_duplicates = int(
        test.duplicated(
            subset=feature_columns
        ).sum()
    )

    # Feature-only overlap across splits.
    calibration_features = calibration[
        feature_columns
    ].astype(str)

    test_features = test[
        feature_columns
    ].astype(str)

    calibration_hashes = set(
        pd.util.hash_pandas_object(
            calibration_features,
            index=False,
        ).astype("uint64")
    )

    test_hashes = set(
        pd.util.hash_pandas_object(
            test_features,
            index=False,
        ).astype("uint64")
    )

    feature_overlap = calibration_hashes.intersection(
        test_hashes
    )

    # Model evaluation.
    X_test = test[feature_columns]
    y_test = test["label"]

    X_test_transformed = preprocessor.transform(X_test)
    predictions = model.predict(X_test_transformed)

    attack_type_metrics = {}

    audit_frame = test[["type", "label"]].copy()
    audit_frame["prediction"] = predictions

    for attack_type, group in audit_frame.groupby("type"):
        attack_type_metrics[str(attack_type)] = {
            "rows": int(len(group)),
            "accuracy": float(
                accuracy_score(
                    group["label"],
                    group["prediction"],
                )
            ),
        }

    metrics = {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "confusion_matrix": (
            confusion_matrix(
                y_test,
                predictions,
            ).tolist()
        ),
        "classification_report": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
    }

    result = {
        "dataset": "TON-IoT network",
        "calibration_rows": int(len(calibration)),
        "test_rows": int(len(test)),
        "exact_row_overlap": len(exact_overlap),
        "calibration_feature_duplicates": (
            calibration_feature_duplicates
        ),
        "test_feature_duplicates": (
            test_feature_duplicates
        ),
        "cross_split_feature_overlap": len(
            feature_overlap
        ),
        "metrics": metrics,
        "attack_type_metrics": attack_type_metrics,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("=" * 80)
    print("BASELINE ROBUSTNESS AUDIT")
    print("=" * 80)

    print(
        "Exact row overlap:",
        len(exact_overlap),
    )
    print(
        "Calibration feature duplicates:",
        calibration_feature_duplicates,
    )
    print(
        "Test feature duplicates:",
        test_feature_duplicates,
    )
    print(
        "Cross-split feature overlap:",
        len(feature_overlap),
    )

    print("\nMetrics:")
    print(
        f"Accuracy : {metrics['accuracy']:.4f}"
    )
    print(
        f"Precision: {metrics['precision']:.4f}"
    )
    print(
        f"Recall   : {metrics['recall']:.4f}"
    )
    print(
        f"F1       : {metrics['f1']:.4f}"
    )

    print("\nPer attack type:")
    for attack_type, values in attack_type_metrics.items():
        print(
            f"{attack_type:15} "
            f"rows={values['rows']:5d} "
            f"accuracy={values['accuracy']:.4f}"
        )

    print("\nGenerated:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
