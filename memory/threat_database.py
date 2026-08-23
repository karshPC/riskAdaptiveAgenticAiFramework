from pathlib import Path
import sqlite3


DB_PATH = Path("memory/threat_intelligence.db")


class ThreatDatabase:

    def __init__(self):
        DB_PATH.parent.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                threat_level TEXT,
                source TEXT,
                confidence REAL
            )
            """
        )

        self.conn.commit()


    def add_threat(
        self,
        ip_address,
        threat_level,
        source,
        confidence,
    ):
        self.conn.execute(
            """
            INSERT OR REPLACE INTO threats
            (
                ip_address,
                threat_level,
                source,
                confidence
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ip_address,
                threat_level,
                source,
                confidence,
            ),
        )

        self.conn.commit()


    def lookup(self, ip_address):

        cursor = self.conn.execute(
            """
            SELECT
                threat_level,
                source,
                confidence
            FROM threats
            WHERE ip_address = ?
            """,
            (ip_address,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "threat_level": row[0],
            "source": row[1],
            "confidence": row[2],
        }


threat_db = ThreatDatabase()
