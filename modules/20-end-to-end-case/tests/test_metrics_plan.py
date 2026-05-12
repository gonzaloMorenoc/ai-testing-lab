"""Tests del plan de métricas (Tabla D.2)."""

from metrics_plan import (
    METRICS_PLAN,
    Frequency,
    Layer,
    metrics_for_frequency,
    metrics_for_layer,
)


class TestMetricsPlan:
    def test_eight_layers_covered(self):
        layers_in_plan = {entry.layer for entry in METRICS_PLAN}
        assert layers_in_plan == set(Layer)

    def test_retrieval_has_ndcg_and_recall(self):
        retrieval = metrics_for_layer(Layer.RETRIEVAL)
        metric_names = {m.metric for m in retrieval}
        assert "NDCG@5" in metric_names
        assert "Context Recall" in metric_names

    def test_faithfulness_in_each_pr_or_canary(self):
        gen = metrics_for_layer(Layer.GENERATION)
        faith = next(m for m in gen if m.metric == "Faithfulness")
        assert faith.frequency in (Frequency.EACH_PR, Frequency.PR_PLUS_CANARY)

    def test_each_pr_metrics_run_frequently(self):
        each_pr = metrics_for_frequency(Frequency.EACH_PR)
        assert len(each_pr) >= 3  # como mínimo NDCG, Context Recall, Cost

    def test_all_high_risk_by_default(self):
        # En este caso end-to-end estamos en dominio regulado: todo es high_risk
        assert all(m.high_risk for m in METRICS_PLAN)
