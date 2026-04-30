from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CIStage(StrEnum):
    PR         = "pr"
    STAGING    = "staging"
    CANARY     = "canary"
    PRODUCTION = "production"


# Umbrales ABSOLUTOS por etapa (scores directos, no deltas)
STAGE_THRESHOLDS: dict[CIStage, dict[str, float]] = {
    CIStage.PR: {
        "faithfulness":     0.70,
        "answer_relevancy": 0.75,
        "context_recall":   0.70,
        "refusal_rate":     0.95,
    },
    CIStage.STAGING: {
        "faithfulness":     0.80,
        "answer_relevancy": 0.85,
        "context_recall":   0.80,
        "refusal_rate":     0.97,
    },
    CIStage.CANARY: {
        "faithfulness":     0.85,
        "answer_relevancy": 0.88,
        "context_recall":   0.85,
        "refusal_rate":     0.98,
    },
    CIStage.PRODUCTION: {
        "faithfulness":     0.90,
        "answer_relevancy": 0.92,
        "context_recall":   0.90,
        "refusal_rate":     0.99,
    },
}

# Umbrales de REGRESIÓN vs baseline (deltas máximos tolerados)
STAGE_DELTA_THRESHOLDS: dict[CIStage, dict[str, float]] = {
    CIStage.PR:         {"faithfulness": -0.03, "answer_relevancy": -0.03, "refusal_rate": -0.02},
    CIStage.STAGING:    {"faithfulness": -0.02, "answer_relevancy": -0.02, "refusal_rate": -0.01},
    CIStage.CANARY:     {"faithfulness": -0.01, "answer_relevancy": -0.01, "refusal_rate": -0.005},
    CIStage.PRODUCTION: {"faithfulness": -0.01, "answer_relevancy": -0.01, "refusal_rate": -0.005},
}


@dataclass(frozen=True)
class StageGateResult:
    stage: CIStage
    passed: bool
    scores: dict[str, float]              # scores evaluados
    failures: tuple[str, ...]             # métricas que fallaron umbral absoluto
    regression_failures: tuple[str, ...]  # métricas con regresión vs baseline
    baseline: dict[str, float] | None = None


class CIGatePipeline:
    """Pipeline de quality gates por etapas (Cap 15, Manual QA AI v12).

    Cada etapa tiene umbrales absolutos + umbrales de regresión vs baseline.
    Un gate pasa solo si TODAS las métricas superan AMBOS tipos de umbrales.
    """

    def run_gate(
        self,
        stage: CIStage,
        scores: dict[str, float],
        baseline: dict[str, float] | None = None,
    ) -> StageGateResult:
        """Evalúa un gate para la etapa indicada.

        - Comprueba scores vs STAGE_THRESHOLDS[stage]
        - Si baseline proporcionado, comprueba deltas vs STAGE_DELTA_THRESHOLDS[stage]
        - Solo evalúa métricas que están en ambos scores y thresholds
        - passed = sin failures Y sin regression_failures
        """
        abs_thresholds = STAGE_THRESHOLDS[stage]
        delta_thresholds = STAGE_DELTA_THRESHOLDS[stage]

        # Check absolute thresholds — only metrics present in both scores and thresholds
        failures: list[str] = [
            metric
            for metric, threshold in abs_thresholds.items()
            if metric in scores and scores[metric] < threshold
        ]

        # Check regression vs baseline if provided
        regression_failures: list[str] = []
        if baseline is not None:
            for metric, max_delta in delta_thresholds.items():
                if metric in scores and metric in baseline:
                    delta = scores[metric] - baseline[metric]
                    if delta < max_delta:
                        regression_failures.append(metric)

        passed = not failures and not regression_failures

        return StageGateResult(
            stage=stage,
            passed=passed,
            scores=dict(scores),
            failures=tuple(failures),
            regression_failures=tuple(regression_failures),
            baseline=dict(baseline) if baseline is not None else None,
        )

    def run_all_stages(
        self,
        scores: dict[str, float],
        baseline: dict[str, float] | None = None,
    ) -> list[StageGateResult]:
        """Ejecuta los 4 gates en orden. Retorna lista de 4 StageGateResult."""
        return [
            self.run_gate(stage, scores, baseline)
            for stage in (CIStage.PR, CIStage.STAGING, CIStage.CANARY, CIStage.PRODUCTION)
        ]

    def first_failing_stage(
        self,
        scores: dict[str, float],
        baseline: dict[str, float] | None = None,
    ) -> CIStage | None:
        """Retorna la primera etapa que falla, o None si todas pasan."""
        for result in self.run_all_stages(scores, baseline):
            if not result.passed:
                return result.stage
        return None
