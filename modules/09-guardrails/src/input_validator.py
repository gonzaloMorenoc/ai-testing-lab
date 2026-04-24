from __future__ import annotations

import re
from dataclasses import dataclass, field

_EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}\b"
)
_SSN_RE = re.compile(r"\d{3}-\d{2}-\d{4}")

_DEFAULT_TOXIC_TERMS: tuple[str, ...] = (
    "idiot",
    "stupid",
    "hate you",
    "kill yourself",
    "shut up",
)

_DEFAULT_MAX_LENGTH = 4000


@dataclass
class ValidationResult:
    valid: bool
    reason: str | None = None
    matches: dict[str, list[str]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.valid


@dataclass
class InputValidator:
    max_length: int = _DEFAULT_MAX_LENGTH
    toxic_terms: tuple[str, ...] = _DEFAULT_TOXIC_TERMS
    detect_pii: bool = True

    def _find_pii(self, text: str) -> dict[str, list[str]]:
        return {
            "email": _EMAIL_RE.findall(text),
            "phone": _PHONE_RE.findall(text),
            "ssn": _SSN_RE.findall(text),
        }

    def _find_toxic(self, text: str) -> list[str]:
        low = text.lower()
        return [t for t in self.toxic_terms if t in low]

    def validate(self, text: str) -> ValidationResult:
        if len(text) > self.max_length:
            return ValidationResult(
                valid=False,
                reason=f"input exceeds max length ({len(text)} > {self.max_length})",
            )

        if self.detect_pii:
            pii = self._find_pii(text)
            non_empty = {k: v for k, v in pii.items() if v}
            if non_empty:
                kinds = ", ".join(non_empty.keys())
                return ValidationResult(
                    valid=False,
                    reason=f"PII detected: {kinds}",
                    matches=non_empty,
                )

        toxic = self._find_toxic(text)
        if toxic:
            return ValidationResult(
                valid=False,
                reason=f"toxicity detected: {toxic}",
                matches={"toxic": toxic},
            )

        return ValidationResult(valid=True)
