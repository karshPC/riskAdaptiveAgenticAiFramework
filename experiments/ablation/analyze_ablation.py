import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "experiments/results/ablation_results.json"


def calculate_metrics(samples):

    tp = tn = fp = fn = 0

    for item in samples:

        actual = item["label"]
        pred = item["prediction"]

        if actual == "attack" and pred == "attack":
            tp += 1

        elif actual == "benign" and pred == "benign":
            tn += 1

        elif actual == "benign" and pred == "attack":
            fp += 1

        elif actual == "attack" and pred == "benign":
            fn += 1

    total = tp + tn + fp + fn

    accuracy = (tp + tn) / total if total else 0

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    avg_latency = sum(
        x["latency_seconds"]
        for x in samples
    ) / len(samples)

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "average_latency_seconds": round(avg_latency, 4),
    }


def main():

    data = json.loads(INPUT.read_text())

    modes = {}

    for item in data:
        modes.setdefault(
            item["mode"],
            []
        ).append(item)


    results = {}

    for mode, samples in modes.items():
        results[mode] = calculate_metrics(samples)


    output = ROOT / "experiments/results/ablation_metrics.json"

    output.write_text(
        json.dumps(
            results,
            indent=4
        )
    )


    print(
        json.dumps(
            results,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
