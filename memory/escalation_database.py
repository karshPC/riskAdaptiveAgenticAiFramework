from pathlib import Path
import sqlite3
from datetime import datetime


DB_PATH = Path("memory/escalation.db")


class EscalationDatabase:

    def __init__(self):
        DB_PATH.parent.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_ip TEXT,
                risk_score REAL,
                action TEXT,
                severity TEXT,
                reason TEXT,
                created_at TEXT
            )
            """
        )

        self.conn.commit()


    def record(
        self,
        src_ip,
        risk_score,
        action,
        severity,
        reason,
    ):
        self.conn.execute(
            """
            INSERT INTO escalations
            (
                src_ip,
                risk_score,
                action,
                severity,
                reason,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                src_ip,
                risk_score,
                action,
                severity,
                reason,
                datetime.utcnow().isoformat(),
            ),
        )

        self.conn.commit()


    def get_all(self):
        cursor = self.conn.execute(
            """
            SELECT
                src_ip,
                risk_score,
                action,
                severity,
                reason,
                created_at
            FROM escalations
            """
        )

        rows = cursor.fetchall()

        return [
            {
                "src_ip": row[0],
                "risk_score": row[1],
                "action": row[2],
                "severity": row[3],
                "reason": row[4],
                "created_at": row[5],
            }
            for row in rows
        ]


escalation_db = EscalationDatabase()
