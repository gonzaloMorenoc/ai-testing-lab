"""
Solución módulo 05: añade versionado semántico (semver) al PromptRegistry
y detecta breaking changes entre versiones major.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "05-prompt-regression"))
from src.prompt_registry import PromptRegistry, PromptVersion


class SemverRegistry(PromptRegistry):
    def is_breaking_change(self, name: str, v_from: str, v_to: str) -> bool:
        try:
            major_from = int(v_from.lstrip("v").split(".")[0])
            major_to = int(v_to.lstrip("v").split(".")[0])
            return major_to > major_from
        except (ValueError, IndexError):
            return False


if __name__ == "__main__":
    reg = SemverRegistry()
    reg.register(PromptVersion("q", "v1.0.0", "Template A"))
    reg.register(PromptVersion("q", "v2.0.0", "Template B — breaking change"))
    print(reg.is_breaking_change("q", "v1.0.0", "v2.0.0"))  # True
    print(reg.is_breaking_change("q", "v1.0.0", "v1.1.0"))  # False
