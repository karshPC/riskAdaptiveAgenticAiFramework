from pathlib import Path
import json


INPUT_FILE = Path("experiments/data/raw_events.json")
OUTPUT_FILE = Path("experiments/data/network_events.json")


def prepare_dataset():
    if not INPUT_FILE.exists():
        sample_events = [
            {
                "src_ip": "10.0.0.99",
                "dst_ip": "10.0.0.1",
                "protocol": "TCP",
                "attack_type": "scan",
                "label": "attack",
            },
            {
                "src_ip": "10.0.0.20",
                "dst_ip": "10.0.0.1",
                "protocol": "TCP",
                "attack_type": "normal",
                "label": "benign",
            },
        ]

        INPUT_FILE.write_text(
            json.dumps(sample_events, indent=4)
        )

    data = json.loads(INPUT_FILE.read_text())

    OUTPUT_FILE.write_text(
        json.dumps(data, indent=4)
    )

    print(f"Prepared {len(data)} network events")


if __name__ == "__main__":
    prepare_dataset()
