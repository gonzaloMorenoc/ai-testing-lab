"""
Solución módulo 04: implementa detección de contradicciones entre turnos.
Si el asistente dice "30 days" en el turno 1 y "60 days" en el turno 3,
la conversación tiene una contradicción.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "04-multi-turn"))
from src.conversation import Conversation


class ContradictionDetector:
    def find_day_mentions(self, text: str) -> list[str]:
        return re.findall(r"\d+\s*days?", text, re.IGNORECASE)

    def detect(self, conversation: Conversation) -> bool:
        all_mentions: list[str] = []
        for turn in conversation.get_assistant_turns():
            all_mentions.extend(self.find_day_mentions(turn))
        unique = set(m.lower() for m in all_mentions)
        return len(unique) > 1


if __name__ == "__main__":
    conv = Conversation()
    conv.add_turn("How long to return?", "Returns allowed within 30 days.")
    conv.add_turn("Are you sure?", "Actually it's 60 days for premium members.")
    detector = ContradictionDetector()
    print("Contradiction detected:", detector.detect(conv))
