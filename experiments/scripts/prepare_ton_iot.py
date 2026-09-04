import pandas as pd
import json
from pathlib import Path


INPUT = Path(
    "data/ton_iot/Train_Test_datasets/Train_Test_Network_dataset/train_test_network.csv"
)

OUTPUT = Path(
    "experiments/data/ton_iot_eval.json"
)


def main():

    df = pd.read_csv(INPUT)

    attacks = df[df["label"] == 1].sample(
        500,
        random_state=42
    )

    benign = df[df["label"] == 0].sample(
        500,
        random_state=42
    )

    data = pd.concat(
        [
            attacks,
            benign
        ]
    ).sample(
        frac=1,
        random_state=42
    )


    results = []

    for _, row in data.iterrows():

        results.append(
            {
                "src_ip": row["src_ip"],
                "dst_ip": row["dst_ip"],
                "src_port": int(row["src_port"])
                if not pd.isna(row["src_port"])
                else None,

                "dst_port": int(row["dst_port"])
                if not pd.isna(row["dst_port"])
                else None,

                "protocol": row["proto"],

                "service": row["service"],

                "duration": float(row["duration"]),

                "src_bytes": int(row["src_bytes"]),

                "dst_bytes": int(row["dst_bytes"]),

                "attack_type":
                    row["type"],

                "label":
                    "attack"
                    if row["label"] == 1
                    else "benign"
            }
        )


    OUTPUT.write_text(
        json.dumps(
            results,
            indent=4
        )
    )

    print(
        f"Generated {len(results)} TON_IoT samples"
    )


if __name__ == "__main__":
    main()
