import pandas as pd
import joblib
from pathlib import Path


MODEL_PATH = Path(
    "results/rf_ids_model.joblib"
)

DATA_PATH = Path(
    "data/splits/ton_iot_network/unseen_eval_test.csv"
)


DROP_COLUMNS = [
    "label",
    "type"
]


print("Loading model")

saved = joblib.load(
    MODEL_PATH
)

model = saved["model"]
features = saved["features"]


print("Loading dataset")

df = pd.read_csv(
    DATA_PATH,
    low_memory=False
)


print("Preparing features")


X = df.drop(
    columns=DROP_COLUMNS,
    errors="ignore"
)


X = pd.get_dummies(
    X,
    dummy_na=True
)


X = X.reindex(
    columns=features,
    fill_value=0
)


print(
    "Features:",
    X.shape[1]
)


print("Generating predictions")


prob = model.predict_proba(
    X
)[:,1]


pred = (
    prob >= 0.3
).astype(int)


result = pd.DataFrame(
    {
        "attack_type": df["type"],
        "probability": prob,
        "prediction": pred
    }
)


result.to_csv(
    "results/riskadaptive_output.csv",
    index=False
)


print("Saved results/riskadaptive_output.csv")

print("\nDetection rate")
print(
    result.groupby("attack_type")["prediction"].mean()
)
