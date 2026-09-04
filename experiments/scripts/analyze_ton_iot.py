import json
from collections import defaultdict
from pathlib import Path


INPUT = Path("experiments/results/ton_iot_results.json")
OUTPUT = Path("experiments/results/ton_iot_attack_analysis.json")


def main():

    data = json.loads(INPUT.read_text())

    attacks = defaultdict(list)

    for item in data["results"]:
        attacks[item["attack_type"]].append(item)

    analysis = {}

    for attack, samples in attacks.items():

        total = len(samples)

        correct = sum(
            1
            for x in samples
            if x["prediction"] == x["actual"]
        )

        avg_risk = sum(
            x["risk_score"]
            for x in samples
        ) / total

        avg_latency = sum(
            x["latency"]
            for x in samples
        ) / total

        analysis[attack] = {
            "samples": total,
            "correct": correct,
            "detection_rate": round(correct / total, 4),
            "average_risk_score": round(avg_risk, 4),
            "average_latency_seconds": round(avg_latency, 6)
        }

    OUTPUT.write_text(
        json.dumps(
            analysis,
            indent=4
        )
    )

    print(json.dumps(analysis, indent=4))


if __name__ == "__main__":
    main()
