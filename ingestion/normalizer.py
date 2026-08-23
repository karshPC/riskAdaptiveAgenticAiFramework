from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.schema import NetworkEvent


NUMERIC_FIELDS = {
    "duration",
    "src_bytes",
    "dst_bytes",
    "src_port",
    "dst_port",
}


def normalize_event(event: NetworkEvent) -> pd.DataFrame:
    """
    Convert NetworkEvent into dataframe format
    compatible with downstream feature processing.
    """

    data: Dict[str, Any] = event.model_dump()

    normalized = {}

    for key, value in data.items():

        if key in NUMERIC_FIELDS:
            if value is None:
                normalized[key] = 0
            else:
                normalized[key] = value

        else:
            if value is None:
                normalized[key] = "unknown"
            else:
                normalized[key] = value

    return pd.DataFrame([normalized])


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

    df = normalize_event(sample)

    print("=" * 80)
    print("EVENT NORMALIZATION TEST")
    print("=" * 80)
    print(df)
    print()
    print("Shape:", df.shape)
