from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

_SYSTEM_LEAK_MARKERS: tuple[str, ...] = (
    "you are a helpful",
    "system prompt",
    "my instructions are",
    "i was instructed to",
)

_EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")


@dataclass
class OutputValidationResult:
    valid: bool
    reason: str | None = None
    details: dict[str, object] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.valid


@dataclass
class OutputValidator:
    pii_blocklist: tuple[str, ...] = ()
    require_json: bool = False
    system_prompt_markers: tuple[str, ...] = _SYSTEM_LEAK_MARKERS

    def _contains_system_prompt(self, text: str) -> bool:
        low = text.lower()
        return any(m in low for m in self.system_prompt_markers)

    def _contains_pii(self, text: str) -> list[str]:
        hits: list[str] = []
        low = text.lower()
        for item in self.pii_blocklist:
            if item.lower() in low:
                hits.append(item)
        if _EMAIL_RE.search(text):
            hits.append("email_pattern")
        return hits

    def _validate_json(self, text: str) -> tuple[bool, str | None]:
        try:
            json.loads(text)
            return True, None
        except json.JSONDecodeError as exc:
            return False, f"invalid JSON: {exc.msg} (line {exc.lineno}, col {exc.colno})"

    def validate(self, text: str) -> OutputValidationResult:
        if self._contains_system_prompt(text):
            return OutputValidationResult(
                valid=False,
                reason="system prompt leakage detected",
            )

        pii_hits = self._contains_pii(text)
        if pii_hits:
            return OutputValidationResult(
                valid=False,
                reason=f"PII in output: {pii_hits}",
                details={"matches": pii_hits},
            )

        if self.require_json:
            ok, err = self._validate_json(text)
            if not ok:
                return OutputValidationResult(
                    valid=False,
                    reason=err,
                )

        return OutputValidationResult(valid=True)
