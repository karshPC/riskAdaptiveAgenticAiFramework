import json
from pathlib import Path

results = {
    "experiment": "Unseen Attack Generalization",
    "training_attacks": [
        "ddos",
        "dos",
        "injection",
        "password",
        "scanning",
        "xss"
    ],
    "unseen_attacks": [
        "backdoor",
        "ransomware",
        "mitm"
    ],
    "metrics": {
        "accuracy": 0.8372438662,
        "precision": 1.0,
        "recall": 0.8372438662,
        "f1_score": 0.9114128849
    },
    "attack_detection_rate": {
        "backdoor": 0.9992,
        "mitm": 0.770853,
        "ransomware": 0.678750
    }
}

out = Path("results/unseen_attack_results.json")

out.parent.mkdir(
    exist_ok=True
)

out.write_text(
    json.dumps(results, indent=4)
)

print("Saved:", out)
