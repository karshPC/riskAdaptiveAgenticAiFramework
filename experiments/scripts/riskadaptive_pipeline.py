import pandas as pd
import joblib
from pathlib import Path
from risk_engine import calculate_risk


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


risk_results = []

for i in range(len(df)):

    risk = calculate_risk(
        attack_probability=float(prob[i]),
        attack_type=df["type"].iloc[i],
        confidence=float(prob[i])
    )

    risk_results.append(risk)


risk_df = pd.DataFrame(risk_results)


result = pd.DataFrame(
    {
        "attack_type": df["type"],
        "probability": prob,
        "prediction": pred,
        "risk_score": risk_df["risk_score"],
        "severity": risk_df["severity"],
        "action": risk_df["action"]
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
