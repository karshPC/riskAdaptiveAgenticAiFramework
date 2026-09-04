import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ingestion.schema import NetworkEvent
from orchestration.graph import risk_graph


DATASET = ROOT / "experiments/data/network_events.json"
OUTPUT = ROOT / "experiments/results/ablation_results.json"


MODES = [
    "ML_only",
    "Rule_only",
    "Hybrid",
    "Hybrid_Memory_Threat",
]


def evaluate_mode(mode):

    events = json.loads(DATASET.read_text())

    results = []

    for item in events:

        event = NetworkEvent(
            src_ip=item.get("src_ip"),
            dst_ip=item.get("dst_ip"),
            protocol=item.get("protocol"),
            attack_type=item.get("attack_type"),
        )

        start = time.time()

        result = risk_graph.invoke(
            {
                "event": event,
                "mode": mode,
            }
        )

        latency = time.time() - start

        results.append(
            {
                "mode": mode,
                "label": item["label"],
                "prediction": (
                    "attack"
                    if result["risk_score"] >= 0.5
                    else "benign"
                ),
                "risk_score": result["risk_score"],
                "action": result.get("action"),
                "latency_seconds": latency,
            }
        )

    return results


def main():

    output = []

    for mode in MODES:
        output.extend(
            evaluate_mode(mode)
        )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=4
        )
    )

    print(
        f"Generated {len(output)} ablation samples"
    )


if __name__ == "__main__":
    main()
