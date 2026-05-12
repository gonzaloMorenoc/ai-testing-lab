"""Tests del postmortem y mejoras estructurales (D.10)."""

from postmortem import IMPROVEMENTS, antipatterns_prevented, build_bug_report


class TestImprovements:
    def test_five_structural_improvements(self):
        assert len(IMPROVEMENTS) == 5

    def test_each_has_owner_role(self):
        for imp in IMPROVEMENTS:
            assert imp.owner_role

    def test_meta_test_prevents_ap10_and_op09(self):
        meta = next(i for i in IMPROVEMENTS if "meta_test" in i.name)
        assert "AP-10" in meta.prevents
        assert "OP-09" in meta.prevents

    def test_antipatterns_prevented_covers_multiple(self):
        prevented = antipatterns_prevented()
        # Las mejoras del postmortem deben cubrir varios antipatrones
        assert "AP-10" in prevented
        assert "OP-09" in prevented
        assert len(prevented) >= 4


class TestBugReport:
    def test_bug_id_format(self):
        report = build_bug_report()
        assert report.id.startswith("INC-")

    def test_severity_high(self):
        report = build_bug_report()
        assert report.severity == "high"

    def test_status_resolved(self):
        report = build_bug_report()
        assert report.status == "resolved"

    def test_metrics_capture_pre_post_faithfulness(self):
        report = build_bug_report()
        assert "faithfulness_pre" in report.metrics_observed
        assert "faithfulness_post" in report.metrics_observed
        assert (
            report.metrics_observed["faithfulness_pre"]
            > report.metrics_observed["faithfulness_post"]
        )

    def test_remediations_include_rollback_and_meta_test(self):
        report = build_bug_report()
        remediations_text = " ".join(report.remediations)
        assert "rollback" in remediations_text.lower() or "Rollback" in remediations_text
        assert "meta-test" in remediations_text.lower() or "meta-test" in remediations_text

    def test_root_cause_mentions_gate_disabled(self):
        report = build_bug_report()
        assert "gate" in report.root_cause.lower()
        assert "merge" in report.root_cause.lower()
