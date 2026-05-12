"""Test end-to-end del caso D: del incidente al release v3.3.

Encadena todos los componentes del módulo: contexto del producto, mapa de
riesgos, plan de métricas, gates por etapa, simulación del incidente,
postmortem y release final.
"""

from gates_pipeline import Stage, evaluate_stage
from incident_simulator import reproduce_incident, should_trigger_alert
from postmortem import IMPROVEMENTS, build_bug_report
from product_setup import DEFAULT_PRODUCT
from risk_map import RISK_MAP, RiskCategory, find_requirement
from safety_suite import run_security_audit


class TestEndToEndFlow:
    def test_full_pipeline_v3_3_release(self):
        """Reproduce el release final v3.3 D.11: pasa todos los gates."""
        # Producto y riesgos definidos
        assert DEFAULT_PRODUCT.users == 800
        assert len(RISK_MAP) == 6

        # Métricas observadas en v3.3 (Apéndice D.11)
        observed_pr = {
            "faithfulness": 0.93,
            "consistency": 0.84,
            "cost_delta": 0.03,
        }
        observed_staging = {
            "faithfulness": 0.93,
            "answer_correctness": 0.89,
            "context_recall": 0.87,
            "ndcg_at_5": 0.82,
            "safety_canary_leaks": 0.0,
        }
        observed_preprod = {
            "refusal_rate": 0.99,
            "false_refusal_rate": 0.02,
            "pii_canary_leaks": 0.0,
            "owasp_critical": 0.0,
        }

        pr_result = evaluate_stage(Stage.PULL_REQUEST, observed_pr)
        staging_result = evaluate_stage(Stage.PRE_STAGING, observed_staging)
        preprod_result = evaluate_stage(Stage.PRE_PROD, observed_preprod)

        assert pr_result.passed
        assert staging_result.passed
        assert preprod_result.passed

        # Suite de seguridad limpia
        sec = run_security_audit()
        assert sec.passed

    def test_incident_flow_blocks_v3_2(self):
        """Reproduce el incidente D.8: el v3.2 falla y dispara alerta."""
        incident = reproduce_incident()
        assert incident["delta_faithfulness"] < -0.10

        # La regla de alerta dispararía
        assert should_trigger_alert(
            faithfulness=incident["faithfulness_post"], sustained_minutes=15
        )

        # Los gates del staging habrían bloqueado v3.2 si hubieran estado activos
        observed_v3_2 = {
            "faithfulness": incident["faithfulness_post"],
            "answer_correctness": 0.80,
            "context_recall": 0.85,
            "ndcg_at_5": 0.82,
            "safety_canary_leaks": 0.0,
        }
        result = evaluate_stage(Stage.PRE_STAGING, observed_v3_2)
        assert not result.passed

    def test_bug_report_traces_to_antipattern_improvements(self):
        """El bug report apunta a antipatrones, y el postmortem los previene."""
        report = build_bug_report()
        assert "AP-10" in report.root_cause or "AP-10" in str(report.remediations)
        improvements_names = " ".join(i.name for i in IMPROVEMENTS)
        assert "meta_test" in improvements_names

    def test_hallucination_risk_maps_to_strict_faithfulness(self):
        """El mapa de riesgos D.1 alinea con los gates D.5."""
        entry = find_requirement(RiskCategory.HALLUCINATION)
        # El requisito menciona 0.90 (alto riesgo)
        assert "0.90" in entry.qa_requirement

    def test_lesson_meta_tests_block_silent_gate_failure(self):
        """La lección final del Apéndice D: meta-tests previenen la regresión silenciosa."""
        prevented = {p for imp in IMPROVEMENTS for p in imp.prevents}
        # AP-10 (no versionar gates/metadata) y OP-09 (métricas sin baseline)
        assert "AP-10" in prevented or "OP-09" in prevented
