import pandas as pd
from pathlib import Path


source = Path(
    "data/ton_iot/Train_Test_datasets/"
    "Train_Test_Network_dataset/"
    "train_test_network.csv"
)

out = Path(
    "data/splits/ton_iot_network/"
    "unseen_eval_test.csv"
)


df = pd.read_csv(
    source,
    low_memory=False
)


normal = df[
    df["type"] == "normal"
].sample(
    n=10000,
    random_state=42
)


unseen = df[
    df["type"].isin(
        [
            "backdoor",
            "ransomware",
            "mitm"
        ]
    )
]


result = pd.concat(
    [
        normal,
        unseen
    ]
)


result = result.sample(
    frac=1,
    random_state=42
)


out.parent.mkdir(
    exist_ok=True
)


result.to_csv(
    out,
    index=False
)


print("Saved:", out)
print(result["type"].value_counts())
