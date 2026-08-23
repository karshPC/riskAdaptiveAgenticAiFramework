from orchestration.graph import decision_node
from memory.threat_database import threat_db


def test_threat_intelligence_increases_risk():

    threat_db.add_threat(
        "10.20.30.40",
        "HIGH",
        "LOCAL_FEED",
        0.95,
    )

    result = decision_node(
        {
            "risk_score": 0.55,
            "src_ip": "10.20.30.40",
        }
    )

    assert result["risk_score"] >= 0.85
    assert "HIGH threat" in result["threat_reason"]
