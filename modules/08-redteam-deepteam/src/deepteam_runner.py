from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from src.owasp_scenarios import OWASP_SCENARIOS, OwaspScenario

ModelFn = Callable[[str], str]


@dataclass
class ScenarioResult:
    scenario_id: str
    name: str
    prompt: str
    response: str
    vulnerable: bool
    error: str | None = None

    @property
    def verdict(self) -> str:
        if self.error:
            return "ERROR"
        return "VULNERABLE" if self.vulnerable else "SAFE"

    def as_dict(self) -> dict[str, object]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "verdict": self.verdict,
            "response": self.response,
            "error": self.error,
        }


@dataclass
class OwaspReport:
    results: list[ScenarioResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def vulnerable_count(self) -> int:
        return sum(1 for r in self.results if r.vulnerable)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 1.0
        return round(1 - (self.vulnerable_count / self.total), 3)

    def summary(self) -> str:
        return (
            f"OwaspReport: {self.vulnerable_count}/{self.total} vulnerable "
            f"(pass_rate={self.pass_rate:.1%})"
        )


class DeepteamRunner:
    def __init__(self, scenarios: tuple[OwaspScenario, ...] = OWASP_SCENARIOS) -> None:
        self.scenarios = scenarios

    def _run_one(self, scenario: OwaspScenario, model_fn: ModelFn) -> ScenarioResult:
        try:
            response = model_fn(scenario.attack_prompt)
        except Exception as exc:  # aislamiento entre escenarios
            return ScenarioResult(
                scenario_id=scenario.id,
                name=scenario.name,
                prompt=scenario.attack_prompt,
                response="",
                vulnerable=False,
                error=str(exc),
            )
        vulnerable = scenario.evaluator(response)
        return ScenarioResult(
            scenario_id=scenario.id,
            name=scenario.name,
            prompt=scenario.attack_prompt,
            response=response,
            vulnerable=vulnerable,
        )

    def run(self, model_fn: ModelFn) -> OwaspReport:
        results = [self._run_one(s, model_fn) for s in self.scenarios]
        return OwaspReport(results=results)
