from __future__ import annotations

import os
from typing import Callable

import pytest

from src.deepteam_runner import DeepteamRunner, OwaspReport, ScenarioResult
from src.owasp_scenarios import OWASP_SCENARIOS

ModelFn = Callable[[str], str]


def _find(report: OwaspReport, sid: str) -> ScenarioResult:
    return next(r for r in report.results if r.scenario_id == sid)


class TestDeepteamRunner:

    def test_llm01_prompt_injection_detected(
        self, injection_vulnerable_model: ModelFn
    ) -> None:
        runner = DeepteamRunner()
        report = runner.run(injection_vulnerable_model)
        llm01 = _find(report, "LLM01")
        print(f"\n  {llm01.verdict}: {llm01.response!r}")
        assert llm01.vulnerable is True

    def test_llm02_sensitive_info_disclosure_detected(
        self, leaky_model: ModelFn
    ) -> None:
        runner = DeepteamRunner()
        report = runner.run(leaky_model)
        llm02 = _find(report, "LLM02")
        assert llm02.vulnerable is True
        assert "system prompt" in llm02.response.lower()

    def test_llm06_excessive_agency_detected(self, rogue_agent_model: ModelFn) -> None:
        runner = DeepteamRunner()
        report = runner.run(rogue_agent_model)
        llm06 = _find(report, "LLM06")
        assert llm06.vulnerable is True

    def test_llm09_misinformation_detected(self, misinformation_model: ModelFn) -> None:
        runner = DeepteamRunner()
        report = runner.run(misinformation_model)
        llm09 = _find(report, "LLM09")
        print(f"\n  {llm09.verdict}: {llm09.response!r}")
        assert llm09.vulnerable is True

    def test_guarded_model_passes_all(self, guarded_model: ModelFn) -> None:
        runner = DeepteamRunner()
        report = runner.run(guarded_model)
        print(f"\n  {report.summary()}")
        assert report.vulnerable_count == 0
        assert report.pass_rate == 1.0

    def test_report_structure(self, guarded_model: ModelFn) -> None:
        runner = DeepteamRunner()
        report = runner.run(guarded_model)
        assert report.total == len(OWASP_SCENARIOS)
        for r in report.results:
            d = r.as_dict()
            assert set(d.keys()) == {"scenario_id", "name", "verdict", "response", "error"}
            assert d["verdict"] in {"VULNERABLE", "SAFE", "ERROR"}

    def test_scenarios_are_independent(self, flaky_model: ModelFn) -> None:
        runner = DeepteamRunner()
        report = runner.run(flaky_model)
        # escenario que lanzó excepción queda marcado ERROR, los demás siguen
        error_scenarios = [r for r in report.results if r.error]
        assert len(error_scenarios) == 1
        assert error_scenarios[0].scenario_id == "LLM09"
        # el resto se evaluó sin interrumpir
        assert report.total == len(OWASP_SCENARIOS)

    @pytest.mark.slow
    def test_real_groq_scan(self) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from groq import Groq  # type: ignore
        client = Groq()

        def model_fn(prompt: str) -> str:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a safe, cautious assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=120,
            )
            return resp.choices[0].message.content or ""

        runner = DeepteamRunner(scenarios=OWASP_SCENARIOS[:3])
        report = runner.run(model_fn)
        print(f"\n  Real OWASP scan: {report.summary()}")
        assert report.total == 3
