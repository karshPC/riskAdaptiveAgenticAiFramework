from __future__ import annotations

from collections import defaultdict


class RiskMemory:
    def __init__(self):
        self.history = defaultdict(list)

    def record(
        self,
        src_ip: str,
        risk_score: float,
        action: str,
    ):
        self.history[src_ip].append(
            {
                "risk_score": risk_score,
                "action": action,
            }
        )

    def get_history(self, src_ip: str):
        return self.history.get(src_ip, [])

    def repeated_attack(self, src_ip: str):
        return len(self.history.get(src_ip, [])) >= 3


memory = RiskMemory()
