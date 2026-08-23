from ingestion.schema import NetworkEvent
from ingestion.normalizer import normalize_event


def test_normalizer_creates_dataframe():

    event = NetworkEvent(
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

    df = normalize_event(event)

    assert df.shape[0] == 1
    assert df.loc[0, "src_ip"] == "192.168.1.10"
    assert df.loc[0, "dst_port"] == 80


def test_normalizer_handles_missing_values():

    event = NetworkEvent()

    df = normalize_event(event)

    assert df.loc[0, "src_ip"] == "unknown"
    assert df.loc[0, "duration"] == 0
