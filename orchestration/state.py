from __future__ import annotations

from typing import Any, Optional, TypedDict


class RiskAgentState(TypedDict, total=False):
    event: Any

    risk_score: float
    risk_level: str
    ml_score: float
    rule_score: float
    rule_level: str
    ml_weight: float
    rule_weight: float
    memory_boost: float
    threat_boost: float

    attack_type: Optional[str]
    src_ip: Optional[str]
    dst_ip: Optional[str]
    proto: Optional[str]
    service: Optional[str]

    previous_action: Optional[str]
    asset_criticality: Optional[str]

    # Ablation control
    mode: Optional[str]

    action: str
    reason: str
    explanation: str
    llm_narrative: str
    llm_narrative_status: str
    llm_narrative_model: str

    memory_reason: str
    severity: str
    escalation_reason: str

    response_action: str
    agent_observation: dict
    agent_tool_trace: list
    agent_planner: str
    agent_proposed_action: str
    agent_reason: str
    agent_steps: int
    agent_proposal_accepted: bool
    human_approval_required: bool
    guardian_reason: str
