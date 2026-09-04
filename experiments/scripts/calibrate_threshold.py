from pathlib import Path
import sys
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.risk_engine import assess_risk


CALIBRATION_DATA = (
    PROJECT_ROOT
    / "data/splits/ton_iot_network/calibration.csv"
)

OUTPUT = (
    PROJECT_ROOT
    / "experiments/results/threshold_calibration.json"
)


def calculate_metrics(results, threshold):

    tp = tn = fp = fn = 0

    for item in results:

        prediction = (
            1
            if item["risk_score"] >= threshold
            else 0
        )

        actual = item["actual"]

        if prediction == 1 and actual == 1:
            tp += 1
        elif prediction == 0 and actual == 0:
            tn += 1
        elif prediction == 1 and actual == 0:
            fp += 1
        elif prediction == 0 and actual == 1:
            fn += 1

    precision = (
        tp / (tp + fp)
        if tp + fp > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn > 0
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0
    )

    accuracy = (
        (tp + tn)
        /
        (tp + tn + fp + fn)
    )

    return {
        "threshold": threshold,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def main():

    df = pd.read_csv(
        CALIBRATION_DATA
    )

    print(
        "Calibration samples:",
        len(df)
    )

    results = []

    for idx, row in df.iterrows():

        if idx % 1000 == 0:
            print(
                f"Processing {idx}/{len(df)}"
            )

        result = assess_risk(
            row.to_frame().T
        )

        results.append(
            {
                "risk_score": result["risk_score"],
                "actual": int(row["label"])
            }
        )


    best = None

    for threshold in [
        x / 100
        for x in range(1, 100)
    ]:

        metrics = calculate_metrics(
            results,
            threshold
        )

        if (
            best is None
            or metrics["f1_score"]
            >
            best["f1_score"]
        ):
            best = metrics


    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            best,
            indent=4
        )
    )


    print("\nBEST THRESHOLD")
    print(
        json.dumps(
            best,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
