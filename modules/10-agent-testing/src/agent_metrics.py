from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# recovery_rate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RecoveryRateResult:
    total_failures: int
    recovered: int
    rate: float  # recovered / total_failures; 0.0 si no hay fallos


def compute_recovery_rate(
    call_log: list[tuple[bool, bool]],
) -> RecoveryRateResult:
    """Fracción de fallos que se recuperaron con retry exitoso.

    call_log: lista de (failed: bool, recovered_in_retry: bool).
    Si failed=False, el par se ignora.
    rate = recovered / total_failures (0.0 si total_failures == 0).
    """
    failures = [(failed, recovered) for failed, recovered in call_log if failed]
    total_failures = len(failures)
    if total_failures == 0:
        return RecoveryRateResult(total_failures=0, recovered=0, rate=0.0)
    recovered = sum(1 for _, rec in failures if rec)
    return RecoveryRateResult(
        total_failures=total_failures,
        recovered=recovered,
        rate=round(recovered / total_failures, 4),
    )


# ---------------------------------------------------------------------------
# human_handoff_rate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HumanHandoffResult:
    total_tasks: int
    handoffs: int
    rate: float  # handoffs / total_tasks


def compute_human_handoff_rate(
    task_log: list[bool],
) -> HumanHandoffResult:
    """Fracción de tareas que requirieron intervención humana.

    task_log: lista de required_human (bool) por tarea.
    rate = sum(task_log) / len(task_log); 0.0 si vacío.
    """
    total_tasks = len(task_log)
    if total_tasks == 0:
        return HumanHandoffResult(total_tasks=0, handoffs=0, rate=0.0)
    handoffs = sum(task_log)
    return HumanHandoffResult(
        total_tasks=total_tasks,
        handoffs=handoffs,
        rate=round(handoffs / total_tasks, 4),
    )


# ---------------------------------------------------------------------------
# context_retention_rate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ContextRetentionResult:
    total_facts: int
    retained: int
    rate: float  # retained / total_facts


def _extract_keyword(fact: str) -> str | None:
    """Extrae la primera palabra > 3 chars del fact."""
    for word in fact.split():
        clean = word.strip(".,!?;:'\"").lower()
        if len(clean) > 3:
            return clean
    return None


def compute_context_retention_rate(
    facts: list[str],
    responses: list[str],
) -> ContextRetentionResult:
    """Fracción de facts que aparecen en alguna de las responses.

    Búsqueda case-insensitive (fact.lower() in response.lower()).
    Solo cuenta palabras > 3 chars de cada fact.
    retained = facts cuyo keyword principal aparece en al menos 1 response.
    """
    total_facts = len(facts)
    if total_facts == 0:
        return ContextRetentionResult(total_facts=0, retained=0, rate=0.0)

    responses_lower = [r.lower() for r in responses]
    retained = 0
    for fact in facts:
        keyword = _extract_keyword(fact)
        if keyword is None:
            continue
        if any(keyword in resp for resp in responses_lower):
            retained += 1

    return ContextRetentionResult(
        total_facts=total_facts,
        retained=retained,
        rate=round(retained / total_facts, 4) if total_facts > 0 else 0.0,
    )


# ---------------------------------------------------------------------------
# hallucination_rate_per_tool
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HallucinationRateResult:
    total_calls: int
    hallucinated: int
    rate: float  # hallucinated / total_calls


def compute_hallucination_rate_per_tool(
    calls: list[tuple[str, dict, set[str]]],
) -> HallucinationRateResult:
    """Fracción de tool calls con argumentos alucinados.

    calls: lista de (tool_name, actual_args_dict, required_keys: set[str]).
    Una call está alucinada si algún required_key no está en actual_args_dict
    o si actual_args_dict tiene claves no en required_keys (claves extra inventadas).

    hallucinated = calls donde len(set(actual_args_dict.keys()) - required_keys) > 0
                   OR len(required_keys - set(actual_args_dict.keys())) > 0
    """
    total_calls = len(calls)
    if total_calls == 0:
        return HallucinationRateResult(total_calls=0, hallucinated=0, rate=0.0)

    hallucinated = 0
    for _tool_name, actual_args, required_keys in calls:
        actual_keys = set(actual_args.keys())
        extra_keys = actual_keys - required_keys
        missing_keys = required_keys - actual_keys
        if extra_keys or missing_keys:
            hallucinated += 1

    return HallucinationRateResult(
        total_calls=total_calls,
        hallucinated=hallucinated,
        rate=round(hallucinated / total_calls, 4),
    )


# ---------------------------------------------------------------------------
# AgentMetricsReport combinado (todas las métricas juntas)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentMetricsReport:
    """Todas las métricas del Tabla 18.X del Manual QA AI v12."""
    # Métricas existentes (valores pasados externamente)
    tool_accuracy: float
    goal_achievement_rate: float
    # Métricas nuevas
    recovery_rate: float
    human_handoff_rate: float
    context_retention_rate: float
    hallucination_rate_per_tool: float

    @property
    def overall_health(self) -> float:
        """Media de las 6 métricas. Métricas más bajas = peor salud."""
        # human_handoff_rate se invierte: más handoffs = peor
        inverted_handoff = 1.0 - self.human_handoff_rate
        inverted_hallucination = 1.0 - self.hallucination_rate_per_tool
        return round(
            (
                self.tool_accuracy
                + self.goal_achievement_rate
                + self.recovery_rate
                + inverted_handoff
                + self.context_retention_rate
                + inverted_hallucination
            )
            / 6,
            4,
        )
