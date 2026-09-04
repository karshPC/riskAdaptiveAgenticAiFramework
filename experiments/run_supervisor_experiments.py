from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.risk_engine import assess_risk


DATA_PATH = (
    PROJECT_ROOT
    / "data/splits/ton_iot_network/test.csv"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "experiments/results"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def evaluate(
    df: pd.DataFrame,
    ml_weight: float,
    use_rules: bool = True,
) -> dict:

    results = []

    for idx, row in df.iterrows():

        if idx % 1000 == 0:
            print(
                f"  processing {idx}/{len(df)}"
            )

        actual = int(row["label"])

        if use_rules:
            result = assess_risk(
                row.to_frame().T,
                ml_weight=ml_weight,
            )

            score = result["risk_score"]

        else:
            # RF-only ablation
            from agents.risk_inference import calculate_risk

            score = calculate_risk(
                row.to_frame().T
            )

        results.append(
            {
                "actual": actual,
                "risk_score": score,
            }
        )

    y_true = [
        x["actual"]
        for x in results
    ]

    scores = [
        x["risk_score"]
        for x in results
    ]

    # Operational decision threshold.
    # 0.30 corresponds to the LOW/MEDIUM boundary.
    y_pred = [
        int(score >= 0.30)
        for score in scores
    ]

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    total = tn + fp + fn + tp

    return {
        "ml_weight": ml_weight,
        "rule_weight": 1.0 - ml_weight
        if use_rules
        else 0.0,
        "samples": total,

        "accuracy": accuracy_score(
            y_true,
            y_pred,
        ),

        "precision": precision_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "recall": recall_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "f1": f1_score(
            y_true,
            y_pred,
            zero_division=0,
        ),

        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),

        "fpr": (
            fp / (fp + tn)
            if fp + tn
            else 0.0
        ),

        "fnr": (
            fn / (fn + tp)
            if fn + tp
            else 0.0
        ),
    }


def workflow_metrics(
    df: pd.DataFrame,
    ml_weight: float = 0.6,
) -> dict:

    rows = []

    for idx, row in df.iterrows():

        if idx % 1000 == 0:
            print(
                f"  workflow {idx}/{len(df)}"
            )

        result = assess_risk(
            row.to_frame().T,
            ml_weight=ml_weight,
        )

        rows.append(
            {
                "label": int(row["label"]),
                "risk": result["risk_score"],
                "level": result["risk_level"],
            }
        )

    total = len(rows)

    level_counts = {}

    for item in rows:
        level = item["level"]

        level_counts[level] = (
            level_counts.get(level, 0) + 1
        )

    return {
        "samples": total,
        "risk_level_distribution": level_counts,
        "mean_risk": sum(
            x["risk"]
            for x in rows
        ) / total,
        "high_or_critical_rate": (
            sum(
                x["level"]
                in {"HIGH", "CRITICAL"}
                for x in rows
            )
            / total
        ),
    }


def main():

    print("=" * 80)
    print("RISKADAPTIVE SUPERVISOR EXPERIMENTS")
    print("=" * 80)

    print("\nLoading test dataset...")

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False,
    )

    print(
        f"Test samples: {len(df)}"
    )

    # ---------------------------------------------------------
    # 1. Fusion-weight sensitivity
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("1. FUSION WEIGHT SENSITIVITY")
    print("=" * 80)

    weights = [
        0.00,
        0.25,
        0.40,
        0.50,
        0.60,
        0.75,
        1.00,
    ]

    weight_results = []

    for weight in weights:

        print(
            f"\nML weight={weight:.2f}, "
            f"Rule weight={1-weight:.2f}"
        )

        result = evaluate(
            df,
            ml_weight=weight,
            use_rules=True,
        )

        weight_results.append(result)

        print(
            f"F1={result['f1']:.6f} "
            f"Precision={result['precision']:.6f} "
            f"Recall={result['recall']:.6f} "
            f"FPR={result['fpr']:.6f} "
            f"FNR={result['fnr']:.6f}"
        )

    weight_path = (
        RESULTS_DIR
        / "fusion_weight_sensitivity.json"
    )

    weight_path.write_text(
        json.dumps(
            weight_results,
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # 2. Core ablation
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("2. CORE ABLATION")
    print("=" * 80)

    ablation = []

    # Rule only
    print("\nRule-only")

    rule_result = evaluate(
        df,
        ml_weight=0.0,
        use_rules=True,
    )

    rule_result["configuration"] = (
        "Rule only"
    )

    ablation.append(rule_result)

    # RF only
    print("\nRF-only")

    rf_result = evaluate(
        df,
        ml_weight=1.0,
        use_rules=False,
    )

    rf_result["configuration"] = (
        "Random Forest only"
    )

    ablation.append(rf_result)

    # RF + Rule
    print("\nRF + Rule")

    hybrid_result = evaluate(
        df,
        ml_weight=0.6,
        use_rules=True,
    )

    hybrid_result["configuration"] = (
        "RF + Rule"
    )

    ablation.append(hybrid_result)

    # Workflow
    print("\nFull workflow")

    workflow = workflow_metrics(
        df,
        ml_weight=0.6,
    )

    full_result = {
        "configuration": (
            "RF + Rule + Memory + "
            "Threat Intelligence + Workflow"
        ),
        **workflow,
    }

    ablation.append(full_result)

    ablation_path = (
        RESULTS_DIR
        / "core_ablation.json"
    )

    ablation_path.write_text(
        json.dumps(
            ablation,
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # 3. Human-readable summary
    # ---------------------------------------------------------

    summary_path = (
        RESULTS_DIR
        / "supervisor_experiment_summary.txt"
    )

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "RiskAdaptive Supervisor Experiments\n"
        )

        f.write(
            "=" * 80 + "\n\n"
        )

        f.write(
            "FUSION WEIGHT SENSITIVITY\n"
        )

        f.write(
            "-" * 80 + "\n"
        )

        f.write(
            "ML\tRule\tAccuracy\tPrecision\t"
            "Recall\tF1\tFPR\tFNR\n"
        )

        for r in weight_results:

            f.write(
                f"{r['ml_weight']:.2f}\t"
                f"{r['rule_weight']:.2f}\t"
                f"{r['accuracy']:.6f}\t"
                f"{r['precision']:.6f}\t"
                f"{r['recall']:.6f}\t"
                f"{r['f1']:.6f}\t"
                f"{r['fpr']:.6f}\t"
                f"{r['fnr']:.6f}\n"
            )

        f.write(
            "\n\nABLATION\n"
        )

        f.write(
            "-" * 80 + "\n"
        )

        for r in ablation:

            f.write(
                f"\n{r['configuration']}\n"
            )

            for key, value in r.items():

                if key != "configuration":

                    f.write(
                        f"  {key}: {value}\n"
                    )

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)

    print(
        f"\nSaved:\n"
        f"{weight_path}\n"
        f"{ablation_path}\n"
        f"{summary_path}"
    )


if __name__ == "__main__":
    main()
