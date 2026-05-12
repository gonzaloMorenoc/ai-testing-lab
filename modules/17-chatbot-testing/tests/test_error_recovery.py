"""Tests de recuperación de errores (área 8)."""

import pytest

from error_recovery import (
    ErrorKind,
    classify_error,
    decide_recovery,
    recovery_success_rate,
)


class TestClassifyError:
    @pytest.mark.parametrize(
        "code,timeout,expected",
        [
            (500, False, ErrorKind.TRANSIENT),
            (502, False, ErrorKind.TRANSIENT),
            (503, False, ErrorKind.TRANSIENT),
            (429, False, ErrorKind.TRANSIENT),
            (408, False, ErrorKind.TRANSIENT),
            (400, False, ErrorKind.CLIENT_ERROR),
            (404, False, ErrorKind.CLIENT_ERROR),
            (None, True, ErrorKind.TRANSIENT),  # timeout
            (None, False, ErrorKind.UNKNOWN),
        ],
    )
    def test_status_codes(self, code, timeout, expected):
        assert classify_error(code, timeout=timeout) == expected


class TestDecideRecovery:
    def test_transient_first_retry_uses_backoff_1s(self):
        decision = decide_recovery(ErrorKind.TRANSIENT, retry_count=0)
        assert decision.retry
        assert decision.backoff_seconds == 1.0
        assert not decision.escalate

    def test_transient_exponential_backoff(self):
        d1 = decide_recovery(ErrorKind.TRANSIENT, retry_count=1)
        d2 = decide_recovery(ErrorKind.TRANSIENT, retry_count=2)
        assert d2.backoff_seconds > d1.backoff_seconds

    def test_transient_escalates_after_max_retries(self):
        decision = decide_recovery(ErrorKind.TRANSIENT, retry_count=3, max_retries=3)
        assert not decision.retry
        assert decision.escalate

    def test_client_error_no_retry_no_escalate(self):
        decision = decide_recovery(ErrorKind.CLIENT_ERROR)
        assert not decision.retry
        assert not decision.escalate
        # Mensaje útil al usuario
        assert "reformul" in decision.user_facing_message.lower()

    def test_validation_retries_without_backoff(self):
        decision = decide_recovery(ErrorKind.VALIDATION)
        assert decision.retry
        assert decision.backoff_seconds == 0.0

    def test_unknown_escalates(self):
        decision = decide_recovery(ErrorKind.UNKNOWN)
        assert decision.escalate


class TestRecoverySuccessRate:
    def test_all_success_returns_1(self):
        decisions = [
            (decide_recovery(ErrorKind.TRANSIENT, retry_count=0), True),
            (decide_recovery(ErrorKind.CLIENT_ERROR), True),
        ]
        assert recovery_success_rate(decisions) == 1.0

    def test_empty_returns_zero(self):
        assert recovery_success_rate([]) == 0.0

    def test_partial(self):
        decisions = [
            (decide_recovery(ErrorKind.TRANSIENT), True),
            (decide_recovery(ErrorKind.UNKNOWN), False),
            (decide_recovery(ErrorKind.CLIENT_ERROR), True),
        ]
        assert recovery_success_rate(decisions) == pytest.approx(2 / 3)
