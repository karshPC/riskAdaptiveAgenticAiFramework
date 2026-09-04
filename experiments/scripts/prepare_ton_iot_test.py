import pandas as pd
import json
from pathlib import Path


INPUT = Path(
    "data/splits/ton_iot_network/test.csv"
)

OUTPUT = Path(
    "experiments/data/ton_iot_test_eval.json"
)


def main():

    df = pd.read_csv(INPUT)


    print("Original samples:", len(df))

    print("\nLabel distribution:")
    print(df["label"].value_counts())


    results = []


    for _, row in df.iterrows():

        results.append(
            {
                "src_ip": row["src_ip"],

                "dst_ip": row["dst_ip"],

                "src_port":
                    int(row["src_port"])
                    if not pd.isna(row["src_port"])
                    else None,

                "dst_port":
                    int(row["dst_port"])
                    if not pd.isna(row["dst_port"])
                    else None,


                "protocol":
                    row["proto"],


                "service":
                    row["service"],


                "duration":
                    float(row["duration"]),


                "src_bytes":
                    int(row["src_bytes"]),


                "dst_bytes":
                    int(row["dst_bytes"]),


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
        f"Generated {len(results)} official TON_IoT test samples"
    )


if __name__ == "__main__":
    main()
