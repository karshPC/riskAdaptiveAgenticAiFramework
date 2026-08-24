from pydantic import BaseModel
from typing import Optional


class NetworkEventRequest(BaseModel):
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    protocol: Optional[str] = None
    attack_type: Optional[str] = None


class RiskResponse(BaseModel):
    risk_score: float
    action: str
    severity: str
    explanation: str
