from __future__ import annotations

import os
from pathlib import Path
import pytest
from src.prompt_registry import PromptRegistry, build_default_registry
from src.regression_checker import RegressionChecker, RegressionReport


class TestPromptRegistry:

    def test_get_prompt_by_version(self, registry: PromptRegistry) -> None:
        v1 = registry.get("support_response", "v1")
        assert "support agent" in v1.template

    def test_get_prompt_v2_has_more_detail(self, registry: PromptRegistry) -> None:
        v2 = registry.get("support_response", "v2")
        assert "concisely" in v2.template or "accurately" in v2.template

    def test_list_versions(self, registry: PromptRegistry) -> None:
        versions = registry.list_versions("support_response")
        assert "v1" in versions
        assert "v2" in versions

    def test_get_latest_returns_v2(self, registry: PromptRegistry) -> None:
        latest = registry.latest("support_response")
        assert latest.version == "v2"

    def test_render_replaces_variables(self, registry: PromptRegistry) -> None:
        v1 = registry.get("support_response", "v1")
        rendered = v1.render(question="What is the return policy?")
        assert "What is the return policy?" in rendered
        assert "{question}" not in rendered

    def test_missing_prompt_raises_key_error(self, registry: PromptRegistry) -> None:
        with pytest.raises(KeyError):
            registry.get("nonexistent", "v1")


class TestRegressionChecker:

    def test_improvement_not_regression(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.75, "v2", 0.85)
        print(f"\n  {report.summary()}")
        assert not report.regression_detected
        assert report.delta > 0

    def test_degradation_detected(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.85, "v2", 0.70)
        print(f"\n  {report.summary()}")
        assert report.regression_detected
        assert report.delta < 0

    def test_within_tolerance_not_regression(self, checker: RegressionChecker) -> None:
        report = checker.check("support_response", "v1", 0.80, "v2", 0.75)
        print(f"\n  {report.summary()} (delta={report.delta}, threshold={checker.threshold})")
        assert not report.regression_detected

    def test_multiple_metrics_partial_regression(
        self, checker: RegressionChecker
    ) -> None:
        scores = {
            "relevancy": (0.80, 0.85),
            "faithfulness": (0.90, 0.70),
        }
        reports = checker.check_multiple("support_response", "v1", "v2", scores)
        assert len(reports) == 2
        regressions = [r for r in reports if r.regression_detected]
        assert len(regressions) == 1
        assert regressions[0].metric_name == "faithfulness"

    def test_promptfooconfig_is_valid_yaml(self) -> None:
        import yaml
        config_path = Path(__file__).parent.parent / "promptfooconfig.yaml"
        assert config_path.exists(), "promptfooconfig.yaml debe existir"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "prompts" in config
        assert "providers" in config
        assert "tests" in config
        assert len(config["prompts"]) >= 2

    @pytest.mark.slow
    def test_with_promptfoo_cli(self) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        import subprocess
        result = subprocess.run(
            ["promptfoo", "eval", "--config", "promptfooconfig.yaml", "--no-cache"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent,
        )
        print(f"\n  Promptfoo output: {result.stdout[-300:]}")
        assert result.returncode == 0, f"Promptfoo falló: {result.stderr}"
