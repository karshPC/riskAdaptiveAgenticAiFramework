"""Generate a five-event, repeated-source trace from the held-out split.

The trace exercises the explicitly enabled contextual graph mode.  It records
only redacted source information in the output and tracks the exact SQLite
rows created by the run so no pre-existing audit record is deleted.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration.graph import risk_graph
from memory.database import DB_PATH as MEMORY_DB


TEST_PATH = ROOT / "data/splits/ton_iot_network/test.csv"
RESULTS_DIR = ROOT / "experiments/results"
TRACE_PATH = RESULTS_DIR / "held_out_memory_trace.json"
FIGURE_PATH = ROOT / "paper/figures/held_out_memory_trace.png"
ESCALATION_DB = ROOT / "memory/escalation.db"


def select_clean_repeated_source(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Return five held-out events for a source with no pre-existing memory."""
    candidates = df["src_ip"].value_counts()
    candidates = candidates[candidates >= 5].index.tolist()

    conn = sqlite3.connect(MEMORY_DB)
    try:
        for src_ip in candidates:
            existing = conn.execute(
                "SELECT COUNT(*) FROM risk_events WHERE src_ip = ?", (src_ip,)
            ).fetchone()[0]
            if existing == 0:
                return str(src_ip), df.loc[df["src_ip"] == src_ip].head(5).copy()
    finally:
        conn.close()
    raise RuntimeError("No repeated held-out source has clean memory state.")


def ids_for_source(path: Path, table: str, src_ip: str) -> set[int]:
    conn = sqlite3.connect(path)
    try:
        return {
            int(row[0])
            for row in conn.execute(f"SELECT id FROM {table} WHERE src_ip = ?", (src_ip,))
        }
    finally:
        conn.close()


def delete_ids(path: Path, table: str, ids: set[int]) -> None:
    if not ids:
        return
    conn = sqlite3.connect(path)
    try:
        conn.executemany(f"DELETE FROM {table} WHERE id = ?", [(item,) for item in ids])
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TEST_PATH, low_memory=False)
    src_ip, events = select_clean_repeated_source(df)
    before_memory = ids_for_source(MEMORY_DB, "risk_events", src_ip)
    before_escalation = ids_for_source(ESCALATION_DB, "escalations", src_ip)
    trace = []

    try:
        for index, (_, row) in enumerate(events.iterrows(), start=1):
            result = risk_graph.invoke(
                {
                    "event": pd.DataFrame([row]),
                    "src_ip": src_ip,
                    "mode": "Hybrid_Memory_Threat",
                }
            )
            trace.append(
                {
                    "event_index": index,
                    "attack_type": str(row["type"]),
                    "base_risk": round(float(result["ml_score"]), 6),
                    "rule_score": round(float(result["rule_score"]), 6),
                    "memory_boost": round(float(result["memory_boost"]), 6),
                    "threat_boost": round(float(result["threat_boost"]), 6),
                    "final_risk": round(float(result["risk_score"]), 6),
                    "action": result["action"],
                }
            )
    finally:
        delete_ids(
            MEMORY_DB,
            "risk_events",
            ids_for_source(MEMORY_DB, "risk_events", src_ip) - before_memory,
        )
        delete_ids(
            ESCALATION_DB,
            "escalations",
            ids_for_source(ESCALATION_DB, "escalations", src_ip) - before_escalation,
        )

    artifact = {
        "dataset": "TON_IoT held-out test split",
        "records_in_split": int(len(df)),
        "source": "IP redacted",
        "mode": "Hybrid_Memory_Threat (explicit opt-in)",
        "events": trace,
    }
    TRACE_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    plt.figure(figsize=(6.0, 3.2))
    plt.plot(
        [item["event_index"] for item in trace],
        [item["memory_boost"] for item in trace],
        marker="o", color="#d95f02", label="Memory boost",
    )
    plt.xlabel("Sequential held-out events for one source (IP redacted)")
    plt.ylabel("Applied memory boost")
    plt.ylim(-0.01, 0.32)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=200)

    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
