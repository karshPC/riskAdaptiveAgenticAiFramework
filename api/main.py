"""FastAPI application entry point."""

from fastapi import FastAPI


app = FastAPI(
    title="Risk-Adaptive Agentic AI Framework",
    version="0.1.0",
    description="Research prototype for Edge-IoT threat detection and incident response.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Return a lightweight liveness response with no external dependencies."""
    return {"status": "ok"}

