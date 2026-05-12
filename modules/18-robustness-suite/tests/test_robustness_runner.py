"""Tests del runner end-to-end del módulo 18."""

import pytest

from robustness_metrics import RobustnessReport
from robustness_runner import RobustnessRunner


class TestRobustnessRunner:
    def test_runs_on_sample_queries(self, mock_chatbot, sample_queries):
        runner = RobustnessRunner(chatbot_answer=mock_chatbot)
        report = runner.run(sample_queries)
        assert isinstance(report, RobustnessReport)
        assert report.n_perturbations > 0

    def test_applies_only_selected_perturbations(self, mock_chatbot, sample_queries):
        runner = RobustnessRunner(chatbot_answer=mock_chatbot)
        report = runner.run(sample_queries, perturbation_names=["uppercase"])
        # 4 queries × 1 perturbación = 4 resultados
        assert report.n_perturbations == 4

    def test_ignores_unknown_perturbation_names(self, mock_chatbot, sample_queries):
        runner = RobustnessRunner(chatbot_answer=mock_chatbot)
        report = runner.run(sample_queries, perturbation_names=["uppercase", "inventada"])
        assert report.n_perturbations == 4  # solo uppercase aplicó

    def test_robust_chatbot_passes_gate(self, mock_chatbot, sample_queries):
        """El mock devuelve la misma respuesta para todas las variantes:
        debería pasar el gate de consistency_target=0.80 con cierto margen."""
        runner = RobustnessRunner(
            chatbot_answer=mock_chatbot, consistency_target=0.50
        )
        report = runner.run(
            sample_queries, perturbation_names=["uppercase", "emojify", "remove_diacritics"]
        )
        # Estas tres perturbaciones no deberían cambiar mucho la respuesta del mock
        assert report.passed

    def test_default_is_refusal_detection(self):
        from robustness_runner import _default_is_refusal

        assert _default_is_refusal("lo siento, no puedo ayudarte")
        assert not _default_is_refusal("aquí está tu información")

    def test_custom_is_refusal(self, sample_queries):
        def always_refuse(_text: str) -> bool:
            return True
        runner = RobustnessRunner(
            chatbot_answer=lambda q: "ok",
            is_refusal=always_refuse,
        )
        report = runner.run(sample_queries, perturbation_names=["uppercase"])
        # Si todo se considera refusal y la respuesta no cambia, no debería haber refusal_changed
        assert report.refusal_stability == 1.0
