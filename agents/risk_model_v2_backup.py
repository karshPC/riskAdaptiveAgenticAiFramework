from __future__ import annotations


def calculate_risk(event) -> tuple[float, str]:

    risk = 0.0

    attack_type = (
        getattr(event, "attack_type", None)
        or ""
    ).lower()

    service = (
        getattr(event, "service", None)
        or ""
    ).lower()

    proto = (
        getattr(event, "proto", None)
        or ""
    ).lower()


    attack_weights = {
        "ddos": 0.35,
        "scanning": 0.30,
        "scan": 0.30,
        "password": 0.25,
        "backdoor": 0.35,
        "ransomware": 0.35,
        "injection": 0.20,
        "xss": 0.20,
        "mitm": 0.30,
    }

    risk += attack_weights.get(
        attack_type,
        0.0
    )


    duration = getattr(
        event,
        "duration",
        0
    ) or 0

    src_bytes = getattr(
        event,
        "src_bytes",
        0
    ) or 0

    dst_bytes = getattr(
        event,
        "dst_bytes",
        0
    ) or 0

    src_pkts = getattr(
        event,
        "src_pkts",
        0
    ) or 0

    dst_pkts = getattr(
        event,
        "dst_pkts",
        0
    ) or 0


    if src_bytes > 100000:
        risk += 0.15

    if dst_bytes > 100000:
        risk += 0.15

    if src_pkts > 100 and dst_pkts < 5:
        risk += 0.15

    if duration < 0.001 and src_bytes == 0:
        risk += 0.10


    if service in {
        "http",
        "https"
    } and attack_type in {
        "xss",
        "injection"
    }:
        risk += 0.20


    if proto == "udp" and attack_type == "ddos":
        risk += 0.20


    risk = min(
        risk,
        1.0
    )


    if risk >= 0.75:
        level = "CRITICAL"

    elif risk >= 0.50:
        level = "HIGH"

    elif risk >= 0.25:
        level = "MEDIUM"

    else:
        level = "LOW"


    return risk, level
