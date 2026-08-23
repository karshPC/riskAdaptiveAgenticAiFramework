from agents.threat_intelligence import threat_intelligence_agent
from memory.threat_database import threat_db


def test_high_threat_ip_increases_risk():

    threat_db.add_threat(
        "10.10.10.10",
        "HIGH",
        "LOCAL_FEED",
        0.95,
    )

    result = threat_intelligence_agent.analyze(
        "10.10.10.10"
    )

    assert result["threat_boost"] == 0.30
    assert "HIGH threat" in result["threat_reason"]
