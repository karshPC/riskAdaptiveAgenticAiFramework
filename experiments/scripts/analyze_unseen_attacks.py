import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import classification_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEST_PATH = (
    PROJECT_ROOT /
    "data/splits/ton_iot_network/attack_unseen_test.csv"
)

MODEL_PATH = (
    PROJECT_ROOT /
    "results/rf_ids_model.joblib"
)


DROP_COLUMNS = {
    "label",
    "type",
    "_row_fingerprint",
    "src_ip",
    "dst_ip",

    "dns_query",
    "dns_qclass",
    "dns_qtype",
    "dns_rcode",
    "dns_AA",
    "dns_RD",
    "dns_RA",
    "dns_rejected",

    "ssl_version",
    "ssl_cipher",
    "ssl_resumed",
    "ssl_established",
    "ssl_subject",
    "ssl_issuer",

    "http_method",
    "http_uri",
    "http_version",
    "http_user_agent",
    "http_trans_depth",
    "http_request_body_len",
    "http_response_body_len",
    "http_status_code",

    "weird_name",
    "weird_addl",
    "weird_notice"
}


def prepare(df):

    X = df.drop(
        columns=list(DROP_COLUMNS),
        errors="ignore"
    )

    X = pd.get_dummies(
        X,
        dummy_na=True
    )

    return X


df = pd.read_csv(
    TEST_PATH,
    low_memory=False
)

model_data = joblib.load(
    MODEL_PATH
)

model = model_data["model"]
features = model_data["features"]


X = prepare(df)

X = X.reindex(
    columns=features,
    fill_value=0
)


pred = model.predict(X)


from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

y_true = df["label"]

print("\nUNSEEN ATTACK DETECTION RESULTS")

print("Accuracy:", accuracy_score(y_true, pred))
print("Precision:", precision_score(y_true, pred, zero_division=0))
print("Recall:", recall_score(y_true, pred, zero_division=0))
print("F1:", f1_score(y_true, pred, zero_division=0))


print("\nATTACK TYPE DISTRIBUTION")
print(df["type"].value_counts())

print("\nATTACK DETECTION BY TYPE")

result = pd.DataFrame({
    "type": df["type"],
    "prediction": pred
})

print(
    result.groupby("type")["prediction"]
    .mean()
)
