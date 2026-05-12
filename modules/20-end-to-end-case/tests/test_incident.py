"""Tests del simulador de incidente (D.8)."""

from incident_simulator import (
    FAITHFULNESS_AUTO_ROLLBACK,
    FAITHFULNESS_BASELINE,
    FAITHFULNESS_INCIDENT,
    INCIDENT_TIMELINE,
    diagnose_root_cause,
    reproduce_incident,
    should_trigger_alert,
)


class TestIncidentConstants:
    def test_baseline_is_0_91(self):
        assert FAITHFULNESS_BASELINE == 0.91

    def test_incident_value_is_0_76(self):
        assert FAITHFULNESS_INCIDENT == 0.76

    def test_auto_rollback_is_0_80(self):
        assert FAITHFULNESS_AUTO_ROLLBACK == 0.80


class TestShouldTriggerAlert:
    def test_alert_when_below_threshold_sustained(self):
        assert should_trigger_alert(faithfulness=0.78, sustained_minutes=15)

    def test_no_alert_if_brief_dip(self):
        assert not should_trigger_alert(faithfulness=0.78, sustained_minutes=5)

    def test_no_alert_if_above_threshold(self):
        assert not should_trigger_alert(faithfulness=0.88, sustained_minutes=60)


class TestDiagnoseRootCause:
    def test_only_prompt_changed(self):
        assert diagnose_root_cause(True, False, False) == "prompt"

    def test_only_model_changed(self):
        assert diagnose_root_cause(False, True, False) == "model"

    def test_multiple_changes_concatenated(self):
        result = diagnose_root_cause(True, True, False)
        assert "prompt" in result
        assert "model" in result
        assert "multiple" in result

    def test_no_changes_suggests_provider_drift(self):
        assert "provider_drift" in diagnose_root_cause(False, False, False)


class TestReproduceIncident:
    def test_delta_faithfulness_negative(self):
        report = reproduce_incident()
        assert report["delta_faithfulness"] < 0

    def test_prompt_version_changed(self):
        report = reproduce_incident()
        assert report["prompt_version_pre"] != report["prompt_version_incident"]

    def test_root_cause_documented(self):
        report = reproduce_incident()
        assert "tone" in report["root_cause"]

    def test_gate_violation_references_antipatterns(self):
        report = reproduce_incident()
        violation = report["gate_violation"]
        assert "ap10" in violation.lower() or "op09" in violation.lower()


class TestIncidentTimeline:
    def test_five_canonical_snapshots(self):
        assert len(INCIDENT_TIMELINE) == 5

    def test_timeline_starts_with_firing_alert(self):
        first = INCIDENT_TIMELINE[0]
        assert first.timestamp_minutes == 0
        assert first.alert_status == "FIRING"

    def test_timeline_ends_resolved(self):
        last = INCIDENT_TIMELINE[-1]
        assert last.alert_status == "RESOLVED"
        assert last.prompt_version == "v3.1"

    def test_rollback_at_t_25(self):
        rollback = next(s for s in INCIDENT_TIMELINE if s.runbook_step == "rollback")
        assert rollback.timestamp_minutes == 25
        assert rollback.prompt_version == "v3.1"
