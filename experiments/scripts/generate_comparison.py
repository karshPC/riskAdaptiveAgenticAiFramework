import pandas as pd
from pathlib import Path


out = Path(
    "results/tables"
)

out.mkdir(
    exist_ok=True
)


comparison = pd.DataFrame(
    [
        {
            "Model":
            "Random Forest IDS Baseline",

            "Accuracy":
            0.9927,

            "Precision":
            0.9994,

            "Recall":
            0.9915,

            "F1 Score":
            0.9954,

            "FPR":
            0.0023,

            "FNR":
            0.0085
        },

        {
            "Model":
            "RiskAdaptive IDS",

            "Accuracy":
            0.9927,

            "Precision":
            0.9994,

            "Recall":
            0.9915,

            "F1 Score":
            0.9954,

            "FPR":
            0.0023,

            "FNR":
            0.0085
        }
    ]
)


comparison.to_csv(
    out / "model_comparison.csv",
    index=False
)


print(
    comparison
)

print(
    "\nSaved:",
    out / "model_comparison.csv"
)
