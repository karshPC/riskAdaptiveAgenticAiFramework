from ingestion.schema import NetworkEvent


def test_network_event_schema():
    event = NetworkEvent(
        src_ip="192.168.1.10",
        dst_ip="10.0.0.5",
        src_port=443,
        dst_port=80,
        proto="tcp",
        service="http",
    )

    assert event.src_ip == "192.168.1.10"
    assert event.proto == "tcp"
    assert event.dst_port == 80


def test_network_event_optional_fields():
    event = NetworkEvent()

    assert event.src_ip is None
    assert event.attack_type is None
