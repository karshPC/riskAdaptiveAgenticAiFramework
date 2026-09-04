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
    "experiments/data/ton_iot_eval.json"
)


OUTPUT_FILE = (
    ROOT /
    "experiments/results/ton_iot_results.json"
)



def evaluate():

    events = json.loads(
        INPUT_FILE.read_text()
    )


    results = []

    TP = TN = FP = FN = 0


    total_latency = 0


    for event_data in events:


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
            if result["action"] != "ALLOW"
            else "benign"
        )


        actual = event_data["label"]



        if prediction == "attack" and actual == "attack":
            TP += 1

        elif prediction == "benign" and actual == "benign":
            TN += 1

        elif prediction == "attack" and actual == "benign":
            FP += 1

        else:
            FN += 1



        results.append(
            {
                "input": event_data,

                "prediction": prediction,

                "risk_score":
                    result.get("risk_score"),

                "action":
                    result.get("action"),

                "severity":
                    result.get("severity"),

                "latency_seconds":
                    latency
            }
        )


    total = TP+TN+FP+FN


    accuracy = (
        (TP+TN)/total
    )


    precision = (
        TP/(TP+FP)
        if TP+FP else 0
    )


    recall = (
        TP/(TP+FN)
        if TP+FN else 0
    )


    f1 = (
        2*precision*recall/
        (precision+recall)
        if precision+recall else 0
    )


    output = {

        "dataset":
            "TON_IoT Network Dataset",

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
