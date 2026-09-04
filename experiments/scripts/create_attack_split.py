import pandas as pd
from pathlib import Path


INPUT = Path(
    "data/ton_iot/Train_Test_datasets/Train_Test_Network_dataset/train_test_network.csv"
)

OUT = Path(
    "data/splits/ton_iot_network"
)

OUT.mkdir(
    parents=True,
    exist_ok=True
)


df = pd.read_csv(
    INPUT,
    low_memory=False
)


print("Original:")
print(df["type"].value_counts())


# unseen attacks
unseen = [
    "ransomware",
    "backdoor",
    "mitm"
]


test = df[
    df["type"].isin(unseen)
]


train = df[
    ~df["type"].isin(unseen)
]


train.to_csv(
    OUT / "attack_train.csv",
    index=False
)

test.to_csv(
    OUT / "attack_unseen_test.csv",
    index=False
)


print("\nTRAIN")
print(train["type"].value_counts())


print("\nUNSEEN TEST")
print(test["type"].value_counts())


print("\nSaved")
