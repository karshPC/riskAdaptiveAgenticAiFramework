import pandas as pd
from pathlib import Path


df = pd.read_csv(
    "results/riskadaptive_output.csv"
)


out = Path(
    "results/tables"
)

out.mkdir(
    exist_ok=True
)


# Attack detection table

attack_table = (
    df.groupby("attack_type")
    .agg(
        samples=("attack_type","count"),
        detection_rate=("prediction","mean"),
        avg_risk=("risk_score","mean")
    )
)


attack_table["detection_rate"] = (
    attack_table["detection_rate"] * 100
).round(2)


attack_table["avg_risk"] = (
    attack_table["avg_risk"]
).round(2)


attack_table.to_csv(
    out / "attack_results.csv"
)


# Severity table

severity_table = (
    df["severity"]
    .value_counts()
    .reset_index()
)


severity_table.columns = [
    "severity",
    "samples"
]


severity_table.to_csv(
    out / "severity_results.csv",
    index=False
)


print("Tables generated")
