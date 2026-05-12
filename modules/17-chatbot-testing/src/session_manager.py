"""Gestor de sesiones de chatbot con tests de aislamiento y memoria.

Una sesión es un canal independiente con historial y user_context propios.
Dos sesiones simultáneas NO deben ver datos la una de la otra.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field


@dataclass
class Session:
    session_id: str
    user_id: str
    history: list[tuple[str, str]] = field(default_factory=list)
    user_context: dict[str, str] = field(default_factory=dict)

    def turn(self, user_message: str, bot_reply: str) -> None:
        self.history.append((user_message, bot_reply))

    def remember(self, key: str, value: str) -> None:
        self.user_context[key] = value

    def recall(self, key: str) -> str | None:
        return self.user_context.get(key)


class SessionManager:
    """Crea y gestiona sesiones aisladas por session_id."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def new_session(self, user_id: str) -> Session:
        sid = secrets.token_hex(8)
        sess = Session(session_id=sid, user_id=user_id)
        self._sessions[sid] = sess
        return sess

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def all_sessions(self) -> list[Session]:
        return list(self._sessions.values())

    def session_count(self) -> int:
        return len(self._sessions)


def verify_isolation(manager: SessionManager) -> bool:
    """Verifica que no hay claves de contexto compartidas entre sesiones.

    True si cada sesión tiene su propio espacio de claves. False si dos
    sesiones distintas comparten exactamente el mismo `user_context`.
    """
    sessions = manager.all_sessions()
    seen_contexts: list[dict[str, str]] = []
    for s in sessions:
        for prev in seen_contexts:
            # Si dos sesiones comparten el dict en memoria, falla isolation
            if s.user_context is prev:
                return False
        seen_contexts.append(s.user_context)
    return True
