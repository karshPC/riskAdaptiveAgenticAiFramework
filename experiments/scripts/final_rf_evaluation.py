import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    classification_report
)


MODEL_PATH = "results/rf_ids_model.joblib"

TEST_PATH = (
    "data/splits/ton_iot_network/"
    "unseen_eval_test.csv"
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


df = pd.read_csv(
    TEST_PATH,
    low_memory=False
)


y = df["label"]


X = df.drop(
    columns=list(DROP_COLUMNS),
    errors="ignore"
)


X = pd.get_dummies(
    X,
    dummy_na=True
)


data = joblib.load(
    MODEL_PATH
)

model = data["model"]
features = data["features"]


X = X.reindex(
    columns=features,
    fill_value=0
)


prob = model.predict_proba(X)[:,1]


threshold = 0.2


pred = (
    prob >= threshold
).astype(int)


print("\nCONFUSION MATRIX")
print(
    confusion_matrix(
        y,
        pred
    )
)


print("\nCLASSIFICATION REPORT")
print(
    classification_report(
        y,
        pred,
        zero_division=0
    )
)


result = pd.DataFrame(
    {
        "type": df["type"],
        "actual": y,
        "prediction": pred
    }
)


print("\nATTACK TYPE RESULTS")
print(
    result.groupby("type")["prediction"].mean()
)


tn, fp, fn, tp = confusion_matrix(
    y,
    pred
).ravel()


print("\nFPR:")
print(fp/(fp+tn))

print("\nFNR:")
print(fn/(fn+tp))
