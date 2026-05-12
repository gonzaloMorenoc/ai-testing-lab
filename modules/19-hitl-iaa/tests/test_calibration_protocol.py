"""Tests del protocolo de calibración de 6 fases (§31.4)."""

import pytest

from calibration_protocol import CalibrationPhase, run_calibration


class TestCalibrationProtocol:
    def test_all_phases_pass_with_good_iaa(self):
        report = run_calibration(
            n_pilot_items=30,
            pilot_iaa=0.55,
            after_discussion_iaa=0.70,
            final_iaa=0.78,
        )
        assert report.all_passed
        assert report.failed_phase is None

    def test_fails_when_pilot_size_too_small(self):
        report = run_calibration(
            n_pilot_items=10,
            pilot_iaa=0.6,
            after_discussion_iaa=0.7,
            final_iaa=0.75,
        )
        assert not report.all_passed
        assert report.failed_phase == CalibrationPhase.PILOT

    def test_fails_when_pilot_size_too_large(self):
        report = run_calibration(
            n_pilot_items=100,
            pilot_iaa=0.6,
            after_discussion_iaa=0.7,
            final_iaa=0.75,
        )
        assert report.failed_phase == CalibrationPhase.PILOT

    def test_fails_when_iaa_doesnt_improve_after_discussion(self):
        report = run_calibration(
            n_pilot_items=30,
            pilot_iaa=0.70,
            after_discussion_iaa=0.65,  # bajó
            final_iaa=0.75,
        )
        assert not report.all_passed
        assert report.failed_phase == CalibrationPhase.DISCUSSION

    def test_fails_when_final_iaa_below_target(self):
        report = run_calibration(
            n_pilot_items=30,
            pilot_iaa=0.50,
            after_discussion_iaa=0.55,
            final_iaa=0.60,  # < target 0.70
            target_iaa=0.70,
        )
        assert not report.all_passed
        assert report.failed_phase == CalibrationPhase.RE_ANNOTATION

    def test_phases_in_canonical_order(self):
        report = run_calibration(30, 0.55, 0.70, 0.78)
        ordered = [
            CalibrationPhase.GUIDELINES,
            CalibrationPhase.PILOT,
            CalibrationPhase.DISCUSSION,
            CalibrationPhase.RE_ANNOTATION,
            CalibrationPhase.CERTIFICATION,
            CalibrationPhase.RE_CALIBRATION,
        ]
        assert [p.phase for p in report.phases] == ordered

    def test_six_phases_total(self):
        report = run_calibration(30, 0.55, 0.70, 0.78)
        assert len(report.phases) == 6


def test_pytest_module_loads():
    """Smoke test: verifica que el módulo carga sin errores."""
    from calibration_protocol import CalibrationPhase

    assert len(list(CalibrationPhase)) == 6
