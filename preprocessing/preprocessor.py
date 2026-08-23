from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


EXCLUDED_COLUMNS = {
    "label",
    "type",
    "_row_fingerprint",
    "src_ip",
    "dst_ip",
}


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    if df.empty:
        raise ValueError(f"Dataset is empty: {path}")

    return df


def build_preprocessor(
    calibration: pd.DataFrame,
) -> tuple[ColumnTransformer, list[str], list[str]]:
    feature_columns = [
        column
        for column in calibration.columns
        if column not in EXCLUDED_COLUMNS
    ]

    numeric_columns = [
        column
        for column in feature_columns
        if pd.api.types.is_numeric_dtype(calibration[column])
    ]

    categorical_columns = [
        column
        for column in feature_columns
        if column not in numeric_columns
    ]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
    )

    return preprocessor, numeric_columns, categorical_columns


def fit_preprocessor(
    calibration_path: Path,
    artifact_path: Path,
) -> dict:
    calibration = load_dataset(calibration_path)

    preprocessor, numeric_columns, categorical_columns = (
        build_preprocessor(calibration)
    )

    X_calibration = calibration.drop(
        columns=list(EXCLUDED_COLUMNS),
        errors="ignore",
    )

    preprocessor.fit(X_calibration)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "preprocessor": preprocessor,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "excluded_columns": sorted(EXCLUDED_COLUMNS),
        },
        artifact_path,
    )

    return {
        "calibration_rows": len(calibration),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
    }


def transform_dataset(
    dataset_path: Path,
    artifact_path: Path,
):
    artifact = joblib.load(artifact_path)
    preprocessor = artifact["preprocessor"]

    df = load_dataset(dataset_path)

    X = df.drop(
        columns=list(EXCLUDED_COLUMNS),
        errors="ignore",
    )

    return preprocessor.transform(X)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fit the risk-adaptive feature preprocessing pipeline."
    )

    parser.add_argument(
        "--calibration",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--artifact",
        type=Path,
        default=Path(
            "preprocessing/artifacts/ton_iot_network_preprocessor.joblib"
        ),
    )

    args = parser.parse_args()

    result = fit_preprocessor(
        args.calibration,
        args.artifact,
    )

    print("=== PREPROCESSOR FIT COMPLETE ===")
    print(f"Calibration rows: {result['calibration_rows']}")
    print(f"Numeric features: {len(result['numeric_columns'])}")
    print(f"Categorical features: {len(result['categorical_columns'])}")

    print("\nNumeric:")
    print(result["numeric_columns"])

    print("\nCategorical:")
    print(result["categorical_columns"])

    print("\nArtifact:")
    print(args.artifact)


if __name__ == "__main__":
    main()
