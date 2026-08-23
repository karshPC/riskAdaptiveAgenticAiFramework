from __future__ import annotations

from memory.threat_database import threat_db


class ThreatIntelligenceAgent:

    def analyze(self, src_ip: str):

        threat = threat_db.lookup(src_ip)

        if not threat:
            return {
                "threat_boost": 0.0,
                "threat_reason": "No threat intelligence match found.",
            }

        boost = 0.0

        if threat["threat_level"] == "HIGH":
            boost = 0.30

        elif threat["threat_level"] == "MEDIUM":
            boost = 0.15

        return {
            "threat_boost": boost,
            "threat_reason": (
                f"Known {threat['threat_level']} threat "
                f"from {threat['source']}."
            ),
        }


threat_intelligence_agent = ThreatIntelligenceAgent()
