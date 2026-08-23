from __future__ import annotations

from typing import Any, Optional, TypedDict


class RiskAgentState(TypedDict, total=False):
    event: Any

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
    explanation: str

    memory_reason: str
    severity: str
    escalation_reason: str
