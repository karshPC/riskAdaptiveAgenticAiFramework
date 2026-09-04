from __future__ import annotations


def calculate_risk(event) -> tuple[float, str]:

    risk = 0.0


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


    service = (
        getattr(event, "service", None)
        or ""
    ).lower()


    proto = (
        getattr(event, "proto", None)
        or ""
    ).lower()



    # High volume traffic behaviour
    if src_bytes > 100000:
        risk += 0.20

    if dst_bytes > 100000:
        risk += 0.20


    # Packet flooding behaviour
    if src_pkts > 500:
        risk += 0.20

    if dst_pkts > 500:
        risk += 0.20


    # Asymmetric traffic
    if src_pkts > 100 and dst_pkts < 10:
        risk += 0.15


    # Very short suspicious connections
    if duration < 0.001 and src_bytes == 0:
        risk += 0.10


    # Protocol behaviour
    if proto == "udp" and dst_bytes > 50000:
        risk += 0.15


    # Web anomaly behaviour
    if service in {
        "http",
        "https"
    } and src_bytes > 5000:
        risk += 0.10


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
