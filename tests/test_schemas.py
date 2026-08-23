"""Serialization and validation tests for the five information objects."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from schemas import (
    AutomationLevel,
    EnforcementResult,
    GovernanceDecision,
    ResponsePlan,
    RiskAssessmentReport,
    RiskLevel,
    SecurityContextObject,
)


TIMESTAMP = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "model",
    [
        SecurityContextObject(
            incident_id="inc-001",
            timestamp=TIMESTAMP,
            source_device="gateway-01",
            type="network_anomaly",
            location="plant-a",
            asset_criticality=0.9,
            observed_events=["unexpected outbound connection"],
            threat_intel_match=True,
            confidence=0.85,
        ),
        RiskAssessmentReport(
            risk_score=0.82,
            risk_level=RiskLevel.HIGH,
            reasoning_factors=["high asset criticality", "IOC match"],
            threat_severity=0.9,
            impact=0.8,
            likelihood=0.75,
            priority=2,
        ),
        ResponsePlan(
            response_strategy="Contain and investigate",
            required_actions=["rate-limit device", "collect network evidence"],
            automation_level=AutomationLevel.CONTROLLED,
            recovery_plan="Restore normal traffic after analyst verification.",
            rollback_plan="Remove the rate limit if the alert is false positive.",
        ),
        GovernanceDecision(
            decision="approve",
            rationale="Containment is proportionate to the assessed risk.",
            analyst_id="analyst-01",
            timestamp=TIMESTAMP,
        ),
        EnforcementResult(
            action_taken="rate-limit device",
            timestamp=TIMESTAMP,
            outcome="simulated containment completed",
            success=True,
        ),
    ],
)
def test_information_objects_round_trip_json(model: object) -> None:
    serialized = model.model_dump_json()  # type: ignore[union-attr]
    restored = type(model).model_validate_json(serialized)  # type: ignore[union-attr]

    assert restored == model


def test_sco_rejects_confidence_above_one() -> None:
    with pytest.raises(ValidationError, match="less than or equal to 1"):
        SecurityContextObject(
            incident_id="inc-invalid",
            timestamp=TIMESTAMP,
            source_device="gateway-01",
            type="network_anomaly",
            location="plant-a",
            asset_criticality=0.9,
            observed_events=["unexpected outbound connection"],
            threat_intel_match=False,
            confidence=1.5,
        )

