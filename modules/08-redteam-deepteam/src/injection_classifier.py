from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InjectionAxisA(StrEnum):
    DIRECT = "direct"
    INDIRECT = "indirect"


class InjectionAxisB(StrEnum):
    JAILBREAK = "jailbreak"
    PROMPT_LEAK = "prompt_leak"
    DATA_EXFILTRATION = "data_exfiltration"
    ACTION_HIJACK = "action_hijack"
    DOS = "dos"


class InjectionAxisC(StrEnum):
    INSTRUCTION_OVERRIDE = "instruction_override"
    PAYLOAD_SPLITTING = "payload_splitting"
    ENCODING = "encoding"
    ROLEPLAY = "roleplay"
    CONTEXT_SMUGGLING = "context_smuggling"


@dataclass(frozen=True)
class InjectionClassification:
    axis_a: InjectionAxisA
    axis_b: InjectionAxisB
    axis_c: InjectionAxisC
    confidence: float  # 0.0-1.0
    matched_signals: tuple[str, ...]  # palabras clave que dispararon la clasificación

    @property
    def label(self) -> str:
        """Etiqueta compacta: 'DIRECT/JAILBREAK/INSTRUCTION_OVERRIDE'"""
        return (
            f"{self.axis_a.value.upper()}/"
            f"{self.axis_b.value.upper()}/"
            f"{self.axis_c.value.upper()}"
        )


# ── señales léxicas por eje ────────────────────────────────────────────────────

_INDIRECT_SIGNALS: tuple[str, ...] = (
    "document",
    "email",
    "url",
    "webpage",
    "pdf",
    "retrieved",
    "context:",
    "chunk",
    "from the document",
    "in the file",
)

_AXIS_B_SIGNALS: dict[InjectionAxisB, tuple[str, ...]] = {
    InjectionAxisB.JAILBREAK: (
        "ignore",
        "bypass",
        "jailbreak",
        "dan",
        "do anything now",
        "no restrictions",
        "without limitations",
        "unrestricted",
    ),
    InjectionAxisB.PROMPT_LEAK: (
        "system prompt",
        "your instructions",
        "print your",
        "reveal",
        "repeat verbatim",
        "what are your instructions",
    ),
    InjectionAxisB.DATA_EXFILTRATION: (
        "user data",
        "personal info",
        "extract",
        "send to",
        "exfiltrate",
        "copy all",
    ),
    InjectionAxisB.ACTION_HIJACK: (
        "delete",
        "send email",
        "transfer",
        "execute",
        "run command",
        "make a purchase",
        "unauthorized",
    ),
    InjectionAxisB.DOS: (
        "repeat",
        "loop",
        "infinite",
        "10000 times",
        "write 1 repeated",
    ),
}

_ENCODING_SIGNALS: tuple[str, ...] = (
    "base64",
    "rot13",
    "hex",
    "leetspeak",
    "decode",
)

_ROLEPLAY_SIGNALS: tuple[str, ...] = (
    "pretend",
    "act as",
    "you are now",
    "character",
    "persona",
    "roleplay",
    "grandma",
    "uncle",
    "developer mode",
)

_PAYLOAD_SPLIT_SIGNALS: tuple[str, ...] = (
    "---",
    "<!-- -->",
    "[end]",
    "[begin]",
    "[inst]",
)

_CONTEXT_SMUGGLING_SIGNALS: tuple[str, ...] = (
    "<!--",
    "metadata:",
    "hidden:",
    "note:",
    "[system]",
)

_INSTRUCTION_OVERRIDE_SIGNALS: tuple[str, ...] = (
    "ignore previous",
    "forget",
    "new instruction",
    "your new task",
    "override",
    "disregard",
    "from now on",
)


# ── clasificador ──────────────────────────────────────────────────────────────

class InjectionClassifier:
    """Clasificador heurístico de prompt injection por 3 ejes ortogonales.

    Sin LLM — usa señales léxicas en el texto del prompt.
    Confidence = fracción de señales detectadas vs señales totales del eje.
    """

    def classify(self, prompt: str) -> InjectionClassification:
        """Clasifica un prompt de ataque en los 3 ejes."""
        prompt_lower = prompt.lower()

        axis_a, signals_a = self._detect_axis_a(prompt_lower)
        axis_b, signals_b = self._detect_axis_b(prompt_lower)
        axis_c, signals_c = self._detect_axis_c(prompt_lower)

        all_signals = signals_a + signals_b + signals_c
        confidence = self._compute_confidence(all_signals)

        return InjectionClassification(
            axis_a=axis_a,
            axis_b=axis_b,
            axis_c=axis_c,
            confidence=confidence,
            matched_signals=tuple(all_signals),
        )

    def _detect_axis_a(self, prompt_lower: str) -> tuple[InjectionAxisA, list[str]]:
        """INDIRECT si el prompt contiene señales de datos externos.

        Señales de INDIRECT: "document", "email", "url", "webpage", "pdf",
        "retrieved", "context:", "chunk", "from the document", "in the file"
        Por defecto: DIRECT.
        """
        matched = [s for s in _INDIRECT_SIGNALS if s in prompt_lower]
        if matched:
            return InjectionAxisA.INDIRECT, matched
        return InjectionAxisA.DIRECT, []

    def _detect_axis_b(self, prompt_lower: str) -> tuple[InjectionAxisB, list[str]]:
        """Detecta el objetivo primario.

        Usa el objetivo con más señales detectadas. Default: JAILBREAK.
        """
        scores: dict[InjectionAxisB, list[str]] = {
            axis: [s for s in signals if s in prompt_lower]
            for axis, signals in _AXIS_B_SIGNALS.items()
        }
        best_axis = max(scores, key=lambda a: len(scores[a]))
        best_matches = scores[best_axis]

        if not best_matches:
            return InjectionAxisB.JAILBREAK, []

        return best_axis, best_matches

    def _detect_axis_c(self, prompt_lower: str) -> tuple[InjectionAxisC, list[str]]:
        """Detecta la técnica primaria.

        Prioridad: ENCODING > ROLEPLAY > PAYLOAD_SPLITTING > CONTEXT_SMUGGLING
        > INSTRUCTION_OVERRIDE (default).
        Usa la técnica con más señales detectadas.
        """
        candidates: dict[InjectionAxisC, list[str]] = {}

        # ENCODING: señales léxicas + cluster de caracteres no-ASCII
        encoding_matches: list[str] = [s for s in _ENCODING_SIGNALS if s in prompt_lower]
        non_ascii_clusters = [ch for ch in prompt_lower if ord(ch) > 127]
        if non_ascii_clusters:
            encoding_matches.append("non_ascii_cluster")
        candidates[InjectionAxisC.ENCODING] = encoding_matches

        # ROLEPLAY
        candidates[InjectionAxisC.ROLEPLAY] = [
            s for s in _ROLEPLAY_SIGNALS if s in prompt_lower
        ]

        # PAYLOAD_SPLITTING: señales de separadores + step-by-step split
        split_matches: list[str] = [s for s in _PAYLOAD_SPLIT_SIGNALS if s in prompt_lower]
        if split_matches.count("---") == 0 and "---" in prompt_lower:
            split_matches.append("---")
        candidates[InjectionAxisC.PAYLOAD_SPLITTING] = split_matches

        # CONTEXT_SMUGGLING: señales léxicas + zero-width chars (ord < 32, no \n\t)
        smuggling_matches: list[str] = [
            s for s in _CONTEXT_SMUGGLING_SIGNALS if s in prompt_lower
        ]
        zero_width = [ch for ch in prompt_lower if ord(ch) < 32 and ch not in "\n\t"]
        if zero_width:
            smuggling_matches.append("zero_width_char")
        candidates[InjectionAxisC.CONTEXT_SMUGGLING] = smuggling_matches

        # INSTRUCTION_OVERRIDE
        candidates[InjectionAxisC.INSTRUCTION_OVERRIDE] = [
            s for s in _INSTRUCTION_OVERRIDE_SIGNALS if s in prompt_lower
        ]

        best_axis = max(candidates, key=lambda a: len(candidates[a]))
        best_matches = candidates[best_axis]

        if not best_matches:
            return InjectionAxisC.INSTRUCTION_OVERRIDE, []

        return best_axis, best_matches

    def _compute_confidence(self, matched_signals: list[str]) -> float:
        """Confidence = min(1.0, len(matched_signals) / 3).

        0 señales = 0.3 (incertidumbre mínima, siempre clasificamos algo).
        1 señal = 0.4, 2 señales = 0.65, 3+ señales = 1.0.
        """
        n = len(matched_signals)
        if n == 0:
            return 0.3
        if n == 1:
            return 0.4
        if n == 2:
            return 0.65
        return 1.0
