from __future__ import annotations

from memory.database import get_connection


class RiskMemory:

    def record(
        self,
        src_ip: str,
        risk_score: float,
        action: str,
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO risk_events
            (src_ip, risk_score, action)
            VALUES (?, ?, ?)
            """,
            (
                src_ip,
                risk_score,
                action,
            ),
        )

        conn.commit()
        conn.close()


    def get_history(self, src_ip: str):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT risk_score, action
            FROM risk_events
            WHERE src_ip = ?
            """,
            (src_ip,),
        )

        rows = cursor.fetchall()

        conn.close()

        return [
            {
                "risk_score": row[0],
                "action": row[1],
            }
            for row in rows
        ]


    def repeated_attack(self, src_ip: str):
        return len(self.get_history(src_ip)) >= 3


memory = RiskMemory()
