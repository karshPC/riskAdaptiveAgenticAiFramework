from ingestion.schema import NetworkEvent
from agents.inference import run_inference


def test_inference_returns_risk_score():
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

    result = run_inference(event)

    assert isinstance(result["risk_score"], float)
    assert 0.0 <= result["risk_score"] <= 1.0


def test_inference_returns_valid_level():
    event = NetworkEvent()

    result = run_inference(event)

    assert result["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }
