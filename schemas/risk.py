from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RiskContext(BaseModel):
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: str
    attack_type: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    proto: Optional[str] = None
    service: Optional[str] = None
    previous_action: Optional[str] = None
