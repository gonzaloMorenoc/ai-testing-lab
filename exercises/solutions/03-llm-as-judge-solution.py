"""
Solución módulo 03: añade una rúbrica de 'completeness' al GEvalJudge
que verifique que la respuesta cubre todos los aspectos de la política.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "03-llm-as-judge"))

from src.geval_judge import GEvalJudge, GEvalResult


class CompletenessJudge(GEvalJudge):
    def evaluate_completeness(
        self, output: str, required_aspects: list[str], threshold: float = 0.7
    ) -> GEvalResult:
        output_lower = output.lower()
        covered = [asp for asp in required_aspects if asp.lower() in output_lower]
        score = round(len(covered) / len(required_aspects), 3) if required_aspects else 1.0
        missing = [asp for asp in required_aspects if asp not in covered]
        reason = (
            f"Covered {len(covered)}/{len(required_aspects)} aspects. Missing: {missing}"
            if missing
            else "All aspects covered."
        )
        return GEvalResult(score=score, reason=reason, criteria="completeness", threshold=threshold)


if __name__ == "__main__":
    judge = CompletenessJudge()
    response = "Returns are allowed within 30 days. Items must be in original condition."
    aspects = ["30 days", "condition", "refund", "packaging"]
    result = judge.evaluate_completeness(response, aspects)
    print(result)
