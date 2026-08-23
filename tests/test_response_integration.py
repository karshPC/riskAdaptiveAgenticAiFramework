from orchestration.graph import risk_graph
from ingestion.schema import NetworkEvent


def test_block_generates_response():

    event = NetworkEvent(
        src_ip="10.0.0.99",
        dst_ip="10.0.0.1",
        protocol="TCP",
        attack_type="scan",
    )

    result = risk_graph.invoke(
        {
            "event": event
        }
    )

    assert "response_action" in result
