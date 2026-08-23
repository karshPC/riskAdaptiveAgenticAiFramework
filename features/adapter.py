from __future__ import annotations

from pathlib import Path
import sys

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.schema import NetworkEvent
from features.event_to_toniot import build_ton_iot_features


PREPROCESSOR_PATH = (
    PROJECT_ROOT
    / "preprocessing/artifacts/"
    "ton_iot_network_preprocessor.joblib"
)


def load_preprocessor():

    artifact = joblib.load(PREPROCESSOR_PATH)

    return artifact["preprocessor"]


def adapt_event(event: NetworkEvent):

    raw_features = build_ton_iot_features(event)

    preprocessor = load_preprocessor()

    transformed = preprocessor.transform(raw_features)

    return transformed


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

    features = adapt_event(sample)

    print("=" * 80)
    print("FEATURE ADAPTER TEST")
    print("=" * 80)
    print("Feature shape:", features.shape)
