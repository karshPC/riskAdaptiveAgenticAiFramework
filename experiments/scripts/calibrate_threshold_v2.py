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
    / "experiments/results/threshold_calibration_v2.json"
)


def metrics(results, threshold):

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
        else:
            fn += 1


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
        2 * precision * recall /
        (precision + recall)
        if precision + recall
        else 0
    )

    fpr = (
        fp / (fp + tn)
        if fp + tn
        else 0
    )

    accuracy = (
        (tp + tn) /
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
        "false_positive_rate": fpr
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

        if idx % 5000 == 0:
            print(
                f"Processing {idx}/{len(df)}"
            )

        risk = assess_risk(
            row.to_frame().T
        )

        results.append(
            {
                "risk_score": risk["risk_score"],
                "actual": int(row["label"])
            }
        )


    candidates = []

    for threshold in [
        x / 100
        for x in range(1, 100)
    ]:

        result = metrics(
            results,
            threshold
        )

        # IDS constraint
        if result["false_positive_rate"] <= 0.05:
            candidates.append(result)


    if not candidates:

        print(
            "No threshold found under 5% FPR"
        )
        return


    best = max(
        candidates,
        key=lambda x: x["f1_score"]
    )


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

    print("\nBEST IDS THRESHOLD")
    print(
        json.dumps(
            best,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
