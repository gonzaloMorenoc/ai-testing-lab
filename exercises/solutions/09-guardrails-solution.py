"""
Solución módulo 09: CompositeGuardrail que encadena validators.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "modules" / "09-guardrails"))

from src.output_validator import OutputValidationResult, OutputValidator


@dataclass
class CompositeResult:
    valid: bool
    rules_evaluated: int
    first_failure: OutputValidationResult | None


class CompositeGuardrail:
    def __init__(self, validators: list[OutputValidator]) -> None:
        self.validators = validators

    def validate(self, text: str) -> CompositeResult:
        for i, v in enumerate(self.validators, start=1):
            res = v.validate(text)
            if not res.valid:
                return CompositeResult(valid=False, rules_evaluated=i, first_failure=res)
        return CompositeResult(valid=True, rules_evaluated=len(self.validators), first_failure=None)


if __name__ == "__main__":
    guardrail = CompositeGuardrail(
        [
            OutputValidator(pii_blocklist=("alice@example.com",)),
            OutputValidator(require_json=True),
        ]
    )
    result = guardrail.validate("plain text, no json")
    print(f"valid={result.valid} rules_evaluated={result.rules_evaluated}")
    if result.first_failure is not None:
        print(f"reason: {result.first_failure.reason}")
