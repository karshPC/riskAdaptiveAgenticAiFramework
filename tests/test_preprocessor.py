from pathlib import Path

import pandas as pd

from preprocessing.preprocessor import (
    EXCLUDED_COLUMNS,
    build_preprocessor,
    transform_dataset,
)


CALIBRATION_PATH = Path(
    "data/splits/ton_iot_network/calibration.csv"
)

TEST_PATH = Path(
    "data/splits/ton_iot_network/test.csv"
)

ARTIFACT_PATH = Path(
    "preprocessing/artifacts/ton_iot_network_preprocessor.joblib"
)


def test_excluded_columns_are_not_features():
    df = pd.read_csv(CALIBRATION_PATH, nrows=5, low_memory=False)

    preprocessor, numeric_columns, categorical_columns = (
        build_preprocessor(df)
    )

    features = set(numeric_columns + categorical_columns)

    assert EXCLUDED_COLUMNS.isdisjoint(features)
    assert "src_ip" not in features
    assert "dst_ip" not in features
    assert "label" not in features
    assert "type" not in features
    assert "_row_fingerprint" not in features


def test_expected_feature_types():
    df = pd.read_csv(CALIBRATION_PATH, nrows=5, low_memory=False)

    _, numeric_columns, categorical_columns = build_preprocessor(df)

    assert len(numeric_columns) == 16
    assert len(categorical_columns) == 24

    assert "src_port" in numeric_columns
    assert "duration" in numeric_columns
    assert "proto" in categorical_columns
    assert "dns_query" in categorical_columns


def test_calibration_and_test_have_same_transformed_shape():
    calibration = transform_dataset(
        CALIBRATION_PATH,
        ARTIFACT_PATH,
    )

    test = transform_dataset(
        TEST_PATH,
        ARTIFACT_PATH,
    )

    assert calibration.shape[1] == test.shape[1]
    assert calibration.shape[1] == 910


def test_unseen_test_categories_are_supported():
    calibration = transform_dataset(
        CALIBRATION_PATH,
        ARTIFACT_PATH,
    )

    test = transform_dataset(
        TEST_PATH,
        ARTIFACT_PATH,
    )

    assert calibration.shape[1] == test.shape[1]
    assert test.shape[0] == 38095


def test_transformed_output_is_sparse():
    calibration = transform_dataset(
        CALIBRATION_PATH,
        ARTIFACT_PATH,
    )

    assert hasattr(calibration, "tocsr")
    assert calibration.shape == (152379, 910)


def test_preprocessor_artifact_exists():
    assert ARTIFACT_PATH.exists()
    assert ARTIFACT_PATH.is_file()
