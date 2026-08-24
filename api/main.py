"""FastAPI application entry point."""

from fastapi import FastAPI

from api.schemas import NetworkEventRequest
from ingestion.schema import NetworkEvent
from orchestration.graph import risk_graph


app = FastAPI(
    title="Risk-Adaptive Agentic AI Framework",
    version="0.1.0",
    description="Research prototype for Edge-IoT threat detection and incident response.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", tags=["risk"])
def analyze_event(event: NetworkEventRequest):

    network_event = NetworkEvent(
        src_ip=event.src_ip,
        dst_ip=event.dst_ip,
        protocol=event.protocol,
        attack_type=event.attack_type,
    )

    result = risk_graph.invoke(
        {
            "event": network_event
        }
    )

    return {
        "risk_score": result.get("risk_score"),
        "action": result.get("action"),
        "severity": result.get("severity"),
        "response_action": result.get("response_action"),
        "explanation": result.get("explanation"),
        "memory_reason": result.get("memory_reason"),
        "threat_reason": result.get("threat_reason"),
    }
