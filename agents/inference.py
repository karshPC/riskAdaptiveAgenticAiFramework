from pathlib import Path

import joblib

from features.adapter import adapt_event


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "results/risk_scorer.joblib"
)


_scorer_artifact = None


def get_scorer():
    global _scorer_artifact

    if _scorer_artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Risk scorer model not found. Run fit_risk_scorer first."
            )

        _scorer_artifact = joblib.load(MODEL_PATH)

    return _scorer_artifact


def run_inference(event):
    features = adapt_event(event)

    artifact = get_scorer()

    model = artifact["model"]

    raw_score = float(
        -model.decision_function(features)[0]
    )

    risk_min = artifact["risk_min"]
    risk_max = artifact["risk_max"]

    risk_score = (
        (raw_score - risk_min)
        /
        (risk_max - risk_min)
    )

    risk_score = max(
        0.0,
        min(1.0, risk_score)
    )

    return {
        "risk_score": float(risk_score),
        "risk_level": classify_level(risk_score),
    }


def classify_level(score):
    if score < 0.25:
        return "LOW"
    elif score < 0.50:
        return "MEDIUM"
    elif score < 0.80:
        return "HIGH"
    else:
        return "CRITICAL"
