from __future__ import annotations

import json
import time
from pathlib import Path
import sys

import joblib
import numpy as np
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

DATA_PATH = PROJECT_ROOT / "data/splits/ton_iot_network/test.csv"
MODEL_PATH = PROJECT_ROOT / "results/rf_ids_model.joblib"
RESULTS_DIR = PROJECT_ROOT / "experiments/results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_rf_scores(df):
    print("Loading Random Forest artifact...")

    artifact = joblib.load(MODEL_PATH)

    model = artifact["model"]
    features = artifact["features"]

    excluded = {
        "label",
        "type",
        "_row_fingerprint",
        "src_ip",
        "dst_ip",
    }

    X = df.drop(
        columns=list(excluded),
        errors="ignore",
    )

    print("Encoding test features...")

    X = pd.get_dummies(
        X,
        dummy_na=True,
    )

    X = X.reindex(
        columns=features,
        fill_value=0,
    )

    print("Running Random Forest once on entire test set...")

    scores = model.predict_proba(X)[:, 1]

    return np.asarray(scores, dtype=float)


def rule_scores(df):
    """
    Vectorized implementation of the transparent rule layer.

    This mirrors the project's rule-risk inputs while avoiding
    Python-level processing of every row.
    """

    score = np.zeros(len(df), dtype=float)

    def numeric(name):
        if name not in df.columns:
            return np.zeros(len(df))

        return pd.to_numeric(
            df[name],
            errors="coerce",
        ).fillna(0).to_numpy(dtype=float)

    src_bytes = numeric("src_bytes")
    dst_bytes = numeric("dst_bytes")
    src_pkts = numeric("src_pkts")
    dst_pkts = numeric("dst_pkts")
    duration = numeric("duration")
    dst_port = numeric("dst_port")

    # Large traffic volume.
    score += np.where(
        (src_bytes + dst_bytes) > 1_000_000,
        0.15,
        0.0,
    )

    # Packet imbalance.
    packet_total = src_pkts + dst_pkts + 1.0
    imbalance = np.abs(src_pkts - dst_pkts) / packet_total

    score += np.where(
        imbalance > 0.90,
        0.10,
        0.0,
    )

    # Very short high-volume connections.
    score += np.where(
        (duration < 1.0)
        & ((src_pkts + dst_pkts) > 100),
        0.10,
        0.0,
    )

    # Common sensitive ports.
    sensitive_ports = {
        21,
        22,
        23,
        25,
        53,
        80,
        110,
        139,
        143,
        443,
        445,
        1433,
        3306,
        3389,
        8080,
    }

    score += np.where(
        np.isin(dst_port, list(sensitive_ports)),
        0.05,
        0.0,
    )

    return np.clip(score, 0.0, 1.0)


def metrics(y_true, scores, threshold=0.30):
    y_pred = (
        np.asarray(scores) >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "fpr": float(
            fp / (fp + tn)
            if fp + tn
            else 0.0
        ),
        "fnr": float(
            fn / (fn + tp)
            if fn + tp
            else 0.0
        ),
    }


def main():
    start = time.time()

    print("=" * 80)
    print("FAST RISKADAPTIVE SUPERVISOR EXPERIMENTS")
    print("=" * 80)

    print("\nLoading test dataset...")

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False,
    )

    print(
        f"Test samples: {len(df)}"
    )

    y_true = (
        pd.to_numeric(
            df["label"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
        .to_numpy()
    )

    # ---------------------------------------------------------
    # Calculate ML and rule scores ONCE.
    # ---------------------------------------------------------

    t0 = time.time()

    ml = load_rf_scores(df)

    print(
        f"RF scoring complete in "
        f"{time.time() - t0:.2f}s"
    )

    t0 = time.time()

    rules = rule_scores(df)

    print(
        f"Rule scoring complete in "
        f"{time.time() - t0:.2f}s"
    )

    # ---------------------------------------------------------
    # Weight sensitivity.
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("FUSION WEIGHT SENSITIVITY")
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

    for w in weights:

        fused = (
            w * ml
            + (1.0 - w) * rules
        )

        result = metrics(
            y_true,
            fused,
        )

        result.update(
            {
                "ml_weight": w,
                "rule_weight": 1.0 - w,
            }
        )

        weight_results.append(result)

        print(
            f"ML={w:.2f} "
            f"Rule={1-w:.2f} | "
            f"Accuracy={result['accuracy']:.6f} | "
            f"Precision={result['precision']:.6f} | "
            f"Recall={result['recall']:.6f} | "
            f"F1={result['f1']:.6f} | "
            f"FPR={result['fpr']:.6f} | "
            f"FNR={result['fnr']:.6f}"
        )

    weight_path = (
        RESULTS_DIR
        / "fast_fusion_weight_sensitivity.json"
    )

    weight_path.write_text(
        json.dumps(
            weight_results,
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # Core ablation.
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("CORE ABLATION")
    print("=" * 80)

    ablation = []

    # Rule only
    rule_result = metrics(
        y_true,
        rules,
    )

    rule_result["configuration"] = (
        "Rule only"
    )

    ablation.append(rule_result)

    print(
        "Rule only: "
        f"F1={rule_result['f1']:.6f}"
    )

    # RF only
    rf_result = metrics(
        y_true,
        ml,
    )

    rf_result["configuration"] = (
        "Random Forest only"
    )

    ablation.append(rf_result)

    print(
        "Random Forest only: "
        f"F1={rf_result['f1']:.6f}"
    )

    # RF + Rule
    fused = (
        0.60 * ml
        + 0.40 * rules
    )

    hybrid_result = metrics(
        y_true,
        fused,
    )

    hybrid_result["configuration"] = (
        "Random Forest + Rule fusion"
    )

    ablation.append(hybrid_result)

    print(
        "RF + Rule: "
        f"F1={hybrid_result['f1']:.6f}"
    )

    # ---------------------------------------------------------
    # Save base ablation.
    # ---------------------------------------------------------

    ablation_path = (
        RESULTS_DIR
        / "fast_core_ablation.json"
    )

    ablation_path.write_text(
        json.dumps(
            ablation,
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # Summary.
    # ---------------------------------------------------------

    summary_path = (
        RESULTS_DIR
        / "fast_supervisor_summary.txt"
    )

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "RiskAdaptive Supervisor Experiments\n"
        )
        f.write("=" * 80 + "\n\n")

        f.write(
            "FUSION WEIGHT SENSITIVITY\n"
        )
        f.write("-" * 80 + "\n")

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
            "\nABLATION\n"
        )
        f.write("-" * 80 + "\n")

        for r in ablation:

            f.write(
                f"\n{r['configuration']}\n"
            )

            for key, value in r.items():

                if key != "configuration":

                    f.write(
                        f"  {key}: {value}\n"
                    )

    elapsed = time.time() - start

    print("\n" + "=" * 80)
    print("FAST EXPERIMENT COMPLETE")
    print("=" * 80)

    print(
        f"Total time: {elapsed:.2f} seconds"
    )

    print(
        f"\nSaved:\n"
        f"{weight_path}\n"
        f"{ablation_path}\n"
        f"{summary_path}"
    )


if __name__ == "__main__":
    main()
