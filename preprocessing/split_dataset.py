from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


RANDOM_SEED = 42
TEST_SIZE = 0.20
CALIBRATION_SIZE = 0.20


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def make_row_fingerprint(df: pd.DataFrame) -> pd.Series:
    normalized = df.fillna("<NA>").astype(str)

    return pd.util.hash_pandas_object(
        normalized,
        index=False,
    ).astype("uint64")


def prepare_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    if "label" not in df.columns:
        raise ValueError(
            f"Dataset must contain a 'label' column: {path}"
        )

    if "type" not in df.columns:
        raise ValueError(
            f"Dataset must contain a 'type' column: {path}"
        )

    if df.empty:
        raise ValueError(f"Dataset is empty: {path}")

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count:
        df = df.drop_duplicates().reset_index(drop=True)

    df["_row_fingerprint"] = make_row_fingerprint(df)

    return df


def split_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create a calibration/test split stratified by attack type.

    The test set is isolated first and is never used to construct
    the calibration set.
    """

    stratify_labels = df["type"].astype(str)

    calibration, test = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=stratify_labels,
    )

    return (
        calibration.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def leakage_report(
    calibration: pd.DataFrame,
    test: pd.DataFrame,
) -> dict:

    calibration_rows = set(
        calibration["_row_fingerprint"].astype("uint64")
    )

    test_rows = set(
        test["_row_fingerprint"].astype("uint64")
    )

    overlapping_rows = calibration_rows.intersection(test_rows)

    return {
        "overlapping_row_fingerprints": len(overlapping_rows),
        "calibration_rows": len(calibration),
        "test_rows": len(test),
    }


def distribution(df: pd.DataFrame) -> dict:
    return {
        str(key): int(value)
        for key, value in df["type"].value_counts().items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create leakage-checked TON-IoT calibration/test splits."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/splits/ton_iot_network"),
    )

    args = parser.parse_args()

    source = args.input.resolve()

    print(f"Loading: {source}")

    df = prepare_dataset(source)

    original_rows = len(df)

    calibration, test = split_dataset(df)

    report = leakage_report(calibration, test)

    if report["overlapping_row_fingerprints"] != 0:
        raise RuntimeError(
            "LEAKAGE DETECTED: calibration/test rows overlap."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    calibration_path = args.output_dir / "calibration.csv"
    test_path = args.output_dir / "test.csv"
    metadata_path = args.output_dir / "metadata.json"

    calibration.to_csv(calibration_path, index=False)
    test.to_csv(test_path, index=False)

    metadata = {
        "dataset": "TON_IoT",
        "source_file": str(source),
        "source_sha256": file_sha256(source),
        "random_seed": RANDOM_SEED,
        "test_size": TEST_SIZE,
        "calibration_size_requested": CALIBRATION_SIZE,
        "original_rows": original_rows,
        "rows_after_deduplication": len(df),
        "calibration_rows": len(calibration),
        "test_rows": len(test),
        "duplicates_removed": original_rows - len(df),
        "stratification_column": "type",
        "label_column": "label",
        "leakage_report": report,
        "calibration_distribution": distribution(calibration),
        "test_distribution": distribution(test),
    }

    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print("\n=== SPLIT COMPLETE ===")
    print(f"Calibration rows: {len(calibration)}")
    print(f"Test rows:        {len(test)}")
    print(f"Duplicates removed: {original_rows - len(df)}")
    print(
        "Overlapping rows:",
        report["overlapping_row_fingerprints"],
    )

    print("\nCalibration distribution:")
    print(calibration["type"].value_counts().to_string())

    print("\nTest distribution:")
    print(test["type"].value_counts().to_string())

    print("\nGenerated:")
    print(calibration_path)
    print(test_path)
    print(metadata_path)


if __name__ == "__main__":
    main()
