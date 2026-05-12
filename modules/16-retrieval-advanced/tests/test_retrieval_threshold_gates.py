"""Integración con qa_thresholds.py (Tabla 4.2 del Manual v13)."""

from qa_thresholds import QA_THRESHOLDS, RiskLevel


class TestThresholdsAccessible:
    def test_context_recall_in_table(self):
        assert "context_recall" in QA_THRESHOLDS

    def test_faithfulness_target(self):
        assert QA_THRESHOLDS["faithfulness"].target == 0.85


class TestRetrievalGate:
    def test_context_recall_minimum_70(self):
        recall_score = 0.72
        threshold = QA_THRESHOLDS["context_recall"]
        assert threshold.gate(recall_score, RiskLevel.MINIMUM)

    def test_context_recall_high_risk_requires_90(self):
        recall_score = 0.85
        threshold = QA_THRESHOLDS["context_recall"]
        assert not threshold.gate(recall_score, RiskLevel.HIGH_RISK)
