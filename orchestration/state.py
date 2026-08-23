from __future__ import annotations

from typing import Optional, TypedDict


class RiskAgentState(TypedDict, total=False):
    risk_score: float
    risk_level: str

    attack_type: Optional[str]
    src_ip: Optional[str]
    dst_ip: Optional[str]
    proto: Optional[str]
    service: Optional[str]

    previous_action: Optional[str]

    action: str
    reason: str
