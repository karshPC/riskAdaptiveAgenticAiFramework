"""Pydantic information objects exchanged by the framework agents.

These models implement the five audit objects described in Table III of the
paper.  They are intentionally provider- and storage-independent so the same
validated records can be passed through LangGraph, persisted locally, and
evaluated offline in later steps.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(StrEnum):
    """Human-readable risk bands derived from a numeric risk score."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutomationLevel(StrEnum):
    """Permitted execution mode for a response plan."""

    AUTOMATIC = "automatic"
    CONTROLLED = "controlled"
    HUMAN_APPROVAL = "human_approval"


class SecurityContextObject(BaseModel):
    """Normalized context assembled from an incoming security event."""

    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(min_length=1)
    timestamp: datetime
    source_device: str = Field(min_length=1)
    type: str = Field(min_length=1)
    location: str = Field(min_length=1)
    asset_criticality: float = Field(ge=0.0, le=1.0)
    observed_events: list[str] = Field(min_length=1)
    threat_intel_match: bool
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence confidence (kappa).")


class RiskAssessmentReport(BaseModel):
    """Risk scoring result and auditable factors used to reach it."""

    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    reasoning_factors: list[str] = Field(min_length=1)
    threat_severity: float = Field(ge=0.0, le=1.0)
    impact: float = Field(ge=0.0, le=1.0)
    likelihood: float = Field(ge=0.0, le=1.0)
    priority: int = Field(ge=1, le=5)


class ResponsePlan(BaseModel):
    """Proposed mitigations and their authorized execution mode."""

    model_config = ConfigDict(extra="forbid")

    response_strategy: str = Field(min_length=1)
    required_actions: list[str] = Field(min_length=1)
    automation_level: AutomationLevel
    recovery_plan: str = Field(min_length=1)
    rollback_plan: str = Field(min_length=1)


class GovernanceDecision(BaseModel):
    """Recorded human governance outcome for an incident response plan."""

    model_config = ConfigDict(extra="forbid")

    decision: Literal["approve", "reject"]
    rationale: str = Field(min_length=1)
    analyst_id: str = Field(min_length=1)
    timestamp: datetime


class EnforcementResult(BaseModel):
    """Immutable record of a completed or simulated enforcement action."""

    model_config = ConfigDict(extra="forbid")

    action_taken: str = Field(min_length=1)
    timestamp: datetime
    outcome: str = Field(min_length=1)
    success: bool

