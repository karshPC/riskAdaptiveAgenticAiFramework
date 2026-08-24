import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ingestion.schema import NetworkEvent
from orchestration.graph import risk_graph


INPUT_FILE = ROOT / "experiments/data/network_events.json"
OUTPUT_FILE = ROOT / "experiments/results/evaluation_results.json"


def evaluate():
    events = json.loads(INPUT_FILE.read_text())

    results = []

    for event_data in events:
        event = NetworkEvent(
            src_ip=event_data.get("src_ip"),
            dst_ip=event_data.get("dst_ip"),
            protocol=event_data.get("protocol"),
            attack_type=event_data.get("attack_type"),
        )

        start = time.time()

        result = risk_graph.invoke(
            {
                "event": event
            }
        )

        latency = time.time() - start

        results.append(
            {
                "input": event_data,
                "risk_score": result.get("risk_score"),
                "action": result.get("action"),
                "severity": result.get("severity"),
                "response_action": result.get("response_action"),
                "explanation": result.get("explanation"),
                "latency_seconds": latency,
            }
        )

    OUTPUT_FILE.write_text(
        json.dumps(results, indent=4)
    )

    print(f"Evaluated {len(results)} events")


if __name__ == "__main__":
    evaluate()
