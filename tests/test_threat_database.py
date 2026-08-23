from memory.threat_database import threat_db


def test_threat_lookup():

    threat_db.add_threat(
        "192.168.1.100",
        "HIGH",
        "LOCAL_FEED",
        0.95,
    )

    result = threat_db.lookup(
        "192.168.1.100"
    )

    assert result["threat_level"] == "HIGH"
    assert result["confidence"] == 0.95
