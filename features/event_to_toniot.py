from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import sys

import pandas as pd
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.schema import NetworkEvent
from ingestion.normalizer import normalize_event


PREPROCESSOR_PATH = (
    PROJECT_ROOT
    / "preprocessing/artifacts/"
    "ton_iot_network_preprocessor.joblib"
)


def load_expected_columns():

    artifact = joblib.load(PREPROCESSOR_PATH)

    preprocessor = artifact["preprocessor"]

    return list(preprocessor.feature_names_in_)


def build_ton_iot_features(event: NetworkEvent) -> pd.DataFrame:

    normalized = normalize_event(event)

    expected_columns = load_expected_columns()

    output = pd.DataFrame(
        0,
        index=[0],
        columns=expected_columns,
    )

    for column in normalized.columns:

        if column in output.columns:
            output[column] = normalized[column]

    return output


if __name__ == "__main__":

    sample = NetworkEvent(
        src_ip="192.168.1.10",
        dst_ip="10.0.0.5",
        src_port=5000,
        dst_port=80,
        proto="tcp",
        service="http",
        duration=2.5,
        src_bytes=1200,
        dst_bytes=400,
        attack_type="scanning",
    )

    df = build_ton_iot_features(sample)

    print("=" * 80)
    print("TON-IOT FEATURE BUILDER TEST")
    print("=" * 80)
    print("Raw feature shape:", df.shape)
    print("Missing values:", df.isna().sum().sum())
