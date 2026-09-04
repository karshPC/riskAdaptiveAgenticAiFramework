import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score
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


model_data = joblib.load(
    MODEL_PATH
)

model = model_data["model"]
features = model_data["features"]


X = X.reindex(
    columns=features,
    fill_value=0
)


probs = model.predict_proba(X)[:,1]


for threshold in [0.5,0.4,0.3,0.2,0.1]:

    pred = (
        probs >= threshold
    ).astype(int)

    print("\nThreshold:", threshold)

    print(
        "Accuracy:",
        accuracy_score(y,pred)
    )

    print(
        "Precision:",
        precision_score(
            y,
            pred,
            zero_division=0
        )
    )

    print(
        "Recall:",
        recall_score(
            y,
            pred,
            zero_division=0
        )
    )

    print(
        "F1:",
        f1_score(
            y,
            pred,
            zero_division=0
        )
    )
