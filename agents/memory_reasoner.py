from __future__ import annotations

from agents.memory import memory


class MemoryReasoner:

    def analyze(self, src_ip: str):

        history = memory.get_history(src_ip)

        if not history:
            return {
                "risk_boost": 0.0,
                "reason": "No previous history found.",
            }

        attack_count = len(history)

        previous_actions = [
            event["action"]
            for event in history
        ]

        boost = 0.0
        reasons = []

        if attack_count >= 3:
            boost += 0.20
            reasons.append(
                "Repeated attack behavior detected."
            )

        if "BLOCK" in previous_actions:
            boost += 0.10
            reasons.append(
                "Previous blocking action recorded."
            )

        return {
            "risk_boost": boost,
            "reason": " ".join(reasons)
            if reasons
            else "Historical activity is normal.",
        }


memory_reasoner = MemoryReasoner()
