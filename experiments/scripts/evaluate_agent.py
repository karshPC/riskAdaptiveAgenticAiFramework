import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT)
)


from ingestion.schema import NetworkEvent
from orchestration.graph import risk_graph


INPUT_FILE = (
    ROOT /
    "experiments/data/ton_iot_test_eval.json"
)

OUTPUT_FILE = (
    ROOT /
    "experiments/results/ton_iot_results.json"
)

CHECKPOINT_FILE = (
    ROOT /
    "experiments/results/ton_iot_results_partial.json"
)



def evaluate():

    events = json.loads(
        INPUT_FILE.read_text()
    )


    results = []

    TP = TN = FP = FN = 0

    total_latency = 0


    total = len(events)


    for idx, event_data in enumerate(events):


        if idx % 1000 == 0:
            print(
                f"Processing {idx}/{total}"
            )


        event = NetworkEvent(

            src_ip=event_data.get("src_ip"),

            dst_ip=event_data.get("dst_ip"),

            src_port=event_data.get("src_port"),

            dst_port=event_data.get("dst_port"),

            proto=event_data.get("protocol"),

            service=event_data.get("service"),

            duration=event_data.get("duration"),

            src_bytes=event_data.get("src_bytes"),

            dst_bytes=event_data.get("dst_bytes"),

            attack_type=event_data.get("attack_type"),

        )


        start = time.time()


        result = risk_graph.invoke(
            {
                "event": event
            }
        )


        latency = time.time() - start

        total_latency += latency


        prediction = (
            "attack"
            if result.get("action") != "ALLOW"
            else "benign"
        )


        actual = event_data["label"]


        if prediction == "attack" and actual == "attack":
            TP += 1

        elif prediction == "benign" and actual == "benign":
            TN += 1

        elif prediction == "attack":
            FP += 1

        else:
            FN += 1



        results.append(
            {
                "prediction": prediction,

                "actual": actual,

                "attack_type":
                    event_data.get("attack_type"),

                "risk_score":
                    result.get("risk_score"),

                "action":
                    result.get("action"),

                "latency":
                    latency
            }
        )


        if idx % 1000 == 0:

            CHECKPOINT_FILE.write_text(
                json.dumps(
                    results,
                    indent=4
                )
            )



    accuracy = (TP+TN)/(TP+TN+FP+FN)

    precision = TP/(TP+FP) if TP+FP else 0

    recall = TP/(TP+FN) if TP+FN else 0

    f1 = (
        2*precision*recall/
        (precision+recall)
        if precision+recall
        else 0
    )


    output = {

        "dataset":
            "TON_IoT Official Test Split",

        "samples":
            total,

        "metrics":
        {
            "TP": TP,
            "TN": TN,
            "FP": FP,
            "FN": FN,

            "accuracy":
                accuracy,

            "precision":
                precision,

            "recall":
                recall,

            "f1_score":
                f1
        },


        "average_latency_seconds":
            total_latency/total,


        "results":
            results
    }


    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=4
        )
    )


    print("\nFINAL RESULTS")
    print(
        json.dumps(
            output["metrics"],
            indent=4
        )
    )

    print(
        "Average latency:",
        total_latency/total
    )



if __name__ == "__main__":
    evaluate()
