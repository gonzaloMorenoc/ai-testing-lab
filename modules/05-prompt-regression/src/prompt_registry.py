from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PromptVersion:
    name: str
    version: str
    template: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def render(self, **kwargs: str) -> str:
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", value)
        return result


class PromptRegistry:
    def __init__(self) -> None:
        self._prompts: dict[tuple[str, str], PromptVersion] = {}

    def register(self, prompt: PromptVersion) -> None:
        self._prompts[(prompt.name, prompt.version)] = prompt

    def get(self, name: str, version: str) -> PromptVersion:
        key = (name, version)
        if key not in self._prompts:
            raise KeyError(f"Prompt '{name}' version '{version}' not found")
        return self._prompts[key]

    def list_versions(self, name: str) -> list[str]:
        return [v for (n, v) in self._prompts if n == name]

    def latest(self, name: str) -> PromptVersion:
        versions = self.list_versions(name)
        if not versions:
            raise KeyError(f"No prompts found with name '{name}'")
        return self.get(name, sorted(versions)[-1])


def build_default_registry() -> PromptRegistry:
    registry = PromptRegistry()

    registry.register(PromptVersion(
        name="support_response",
        version="v1",
        template="You are a support agent. Answer the following question: {question}",
        description="Prompt básico sin instrucciones de formato",
    ))

    registry.register(PromptVersion(
        name="support_response",
        version="v2",
        template=(
            "You are a helpful customer support agent. "
            "Answer the following question concisely and accurately, "
            "citing specific policy details when relevant: {question}"
        ),
        description="Prompt mejorado con instrucciones de formato y contexto",
    ))

    return registry
