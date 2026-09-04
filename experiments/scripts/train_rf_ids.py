from pathlib import Path
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_PATH = (
    PROJECT_ROOT /
    "data/splits/ton_iot_network/attack_train.csv"
)

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

    y = df["label"]

    X = df.drop(
        columns=list(DROP_COLUMNS),
        errors="ignore"
    )

    X = pd.get_dummies(
        X,
        dummy_na=True
    )

    return X, y



def main():

    print("Loading datasets")

    train = pd.read_csv(
        TRAIN_PATH,
        low_memory=False
    )

    test = pd.read_csv(
        TEST_PATH,
        low_memory=False
    )


    X_train, y_train = prepare(train)
    X_test, y_test = prepare(test)


    X_test = X_test.reindex(
        columns=X_train.columns,
        fill_value=0
    )


    print(
        "Training samples:",
        len(X_train)
    )

    print(
        "Features:",
        X_train.shape[1]
    )


    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )


    print("Training Random Forest")

    model.fit(
        X_train,
        y_train
    )


    probabilities = model.predict_proba(
        X_test
    )

    threshold = 0.3

    predictions = (
        probabilities[:,1] >= threshold
    ).astype(int)


    print("\nRESULTS")
    print(
        "Accuracy:",
        accuracy_score(
            y_test,
            predictions
        )
    )

    print(
        "Precision:",
        precision_score(
            y_test,
            predictions
        )
    )

    print(
        "Recall:",
        recall_score(
            y_test,
            predictions
        )
    )

    print(
        "F1:",
        f1_score(
            y_test,
            predictions
        )
    )


    print(
        classification_report(
            y_test,
            predictions
        )
    )


    MODEL_PATH.parent.mkdir(
        exist_ok=True
    )


    joblib.dump(
        {
            "model": model,
            "features": list(X_train.columns)
        },
        MODEL_PATH
    )


    print(
        "\nSaved:",
        MODEL_PATH
    )


if __name__ == "__main__":
    main()
