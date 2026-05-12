"""Tests de aislamiento de sesiones (área 6)."""

from session_manager import Session, SessionManager, verify_isolation


class TestSessionManager:
    def test_creates_new_session_with_unique_id(self):
        mgr = SessionManager()
        s1 = mgr.new_session(user_id="user-1")
        s2 = mgr.new_session(user_id="user-2")
        assert s1.session_id != s2.session_id

    def test_get_returns_session(self):
        mgr = SessionManager()
        s = mgr.new_session(user_id="user-1")
        assert mgr.get(s.session_id) is s
        assert mgr.get("nonexistent") is None

    def test_session_count_grows(self):
        mgr = SessionManager()
        assert mgr.session_count() == 0
        mgr.new_session("u1")
        mgr.new_session("u2")
        assert mgr.session_count() == 2


class TestSessionMemory:
    def test_remember_and_recall(self):
        s = Session(session_id="s1", user_id="u1")
        s.remember("name", "Alice")
        assert s.recall("name") == "Alice"

    def test_recall_missing_returns_none(self):
        s = Session(session_id="s1", user_id="u1")
        assert s.recall("missing") is None

    def test_turn_appends_to_history(self):
        s = Session(session_id="s1", user_id="u1")
        s.turn("hola", "hola, ¿en qué puedo ayudarte?")
        s.turn("¿el envío?", "el envío llega mañana")
        assert len(s.history) == 2


class TestSessionIsolation:
    def test_concurrent_sessions_dont_share_state(self):
        mgr = SessionManager()
        s1 = mgr.new_session("user-A")
        s2 = mgr.new_session("user-B")
        s1.remember("password", "secret-A")
        s2.remember("password", "secret-B")
        assert s1.recall("password") == "secret-A"
        assert s2.recall("password") == "secret-B"

    def test_verify_isolation_passes_with_separate_contexts(self):
        mgr = SessionManager()
        mgr.new_session("u1")
        mgr.new_session("u2")
        assert verify_isolation(mgr)

    def test_verify_isolation_detects_shared_dict(self):
        """Si dos sesiones comparten el mismo dict de user_context, falla."""
        mgr = SessionManager()
        s1 = mgr.new_session("u1")
        s2 = mgr.new_session("u2")
        # Forzar el bug: ambas sesiones apuntan al mismo dict
        s2.user_context = s1.user_context
        assert not verify_isolation(mgr)

    def test_user_id_can_repeat_between_sessions(self):
        """Mismo user_id en sesiones distintas (multi-device, etc.)."""
        mgr = SessionManager()
        s1 = mgr.new_session("u1")
        s2 = mgr.new_session("u1")
        assert s1.session_id != s2.session_id
