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


def evaluate_prediction(result):
    action = result.get("action")

    if action in ["BLOCK", "RESTRICT", "MONITOR"]:
        return "attack"

    return "benign"


def calculate_metrics(results):

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for item in results:

        actual = item["input"]["label"]
        predicted = item["prediction"]

        if actual == "attack" and predicted == "attack":
            tp += 1

        elif actual == "benign" and predicted == "benign":
            tn += 1

        elif actual == "benign" and predicted == "attack":
            fp += 1

        elif actual == "attack" and predicted == "benign":
            fn += 1


    total = tp + tn + fp + fn

    accuracy = (
        (tp + tn) / total
        if total
        else 0
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn)
        else 0
    )


    return {
        "confusion_matrix": {
            "TP": tp,
            "TN": tn,
            "FP": fp,
            "FN": fn,
        },
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": false_positive_rate,
    }



def evaluate():

    events = json.loads(
        INPUT_FILE.read_text()
    )

    results = []

    latencies = []


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

        latencies.append(latency)


        results.append(
            {
                "input": event_data,
                "prediction": evaluate_prediction(result),
                "risk_score": result.get("risk_score"),
                "action": result.get("action"),
                "severity": result.get("severity"),
                "response_action": result.get("response_action"),
                "explanation": result.get("explanation"),
                "latency_seconds": latency,
            }
        )


    metrics = calculate_metrics(results)

    output = {
        "metrics": metrics,
        "average_latency_seconds": sum(latencies) / len(latencies),
        "samples": results,
    }


    OUTPUT_FILE.write_text(
        json.dumps(output, indent=4)
    )


    print(json.dumps(metrics, indent=4))
    print(
        "Average latency:",
        output["average_latency_seconds"]
    )



if __name__ == "__main__":
    evaluate()
