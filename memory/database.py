from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).parent / "risk_memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS risk_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_ip TEXT NOT NULL,
            risk_score REAL NOT NULL,
            action TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


initialize_database()
