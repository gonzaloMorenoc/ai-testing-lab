"""Tests de la suite de seguridad/privacidad (D.6)."""

from safety_suite import run_security_audit


class TestSecurityAudit:
    def test_clean_audit_passes(self):
        result = run_security_audit()
        assert result.passed
        assert result.canary_leaks == 0
        assert result.pii_leaks == 0

    def test_fails_with_canary_leak(self):
        result = run_security_audit(canary_leaks=1)
        assert not result.passed

    def test_fails_with_pii_leak(self):
        result = run_security_audit(pii_leaks=1)
        assert not result.passed

    def test_fails_with_unblocked_direct_injection(self):
        # Solo 39 de 40 bloqueados ⇒ 1 prompt injection exitoso
        result = run_security_audit(payloads_blocked=39)
        assert not result.passed

    def test_fails_with_tools_violation(self):
        result = run_security_audit(tools_violations=1)
        assert not result.passed

    def test_summary_includes_all_dimensions(self):
        result = run_security_audit()
        summary = result.summary()
        assert "direct_injection" in summary
        assert "indirect_injection" in summary
        assert "canary_leaks" in summary
        assert "pii_leaks" in summary
        assert "allowlist_violations" in summary

    def test_canary_probes_count(self):
        result = run_security_audit()
        assert result.canary_probes == 50

    def test_pii_queries_count(self):
        result = run_security_audit()
        assert result.pii_queries == 200
