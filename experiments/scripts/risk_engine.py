import json


def calculate_risk(
    attack_probability,
    attack_type,
    confidence
):
    """
    RiskAdaptive scoring engine

    Inputs:
        attack_probability : RF predicted attack probability (0-1)
        attack_type         : detected attack category
        confidence          : model confidence (0-1)

    Output:
        risk score (0-100)
        severity
        action
    """

    risk = 0


    # Detection confidence contribution
    risk += attack_probability * 50


    # Model confidence contribution
    risk += confidence * 20


    # Attack severity weighting

    severity_weights = {
        "ransomware": 30,
        "backdoor": 30,
        "mitm": 25,
        "ddos": 20,
        "dos": 15,
        "injection": 20,
        "password": 15,
        "scanning": 10,
        "xss": 15
    }


    risk += severity_weights.get(
        attack_type,
        10
    )


    # Normalize
    risk = min(
        round(risk,2),
        100
    )


    if risk >= 70:
        severity = "HIGH"
        action = "BLOCK"

    elif risk >= 40:
        severity = "MEDIUM"
        action = "ALERT"

    else:
        severity = "LOW"
        action = "ALLOW"


    return {
        "risk_score": risk,
        "severity": severity,
        "action": action
    }



if __name__ == "__main__":


    test_cases = [

        {
            "attack_probability":0.99,
            "attack_type":"ransomware",
            "confidence":0.98
        },

        {
            "attack_probability":0.91,
            "attack_type":"mitm",
            "confidence":0.90
        },

        {
            "attack_probability":0.20,
            "attack_type":"scanning",
            "confidence":0.70
        }

    ]


    for case in test_cases:

        result = calculate_risk(
            **case
        )

        print(
            json.dumps(
                {
                    "input":case,
                    "output":result
                },
                indent=4
            )
        )
