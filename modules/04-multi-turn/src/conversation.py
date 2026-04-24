from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)

    def add_turn(self, user_input: str, assistant_response: str) -> None:
        self.messages.append(Message(role="user", content=user_input))
        self.messages.append(Message(role="assistant", content=assistant_response))

    def get_user_turns(self) -> list[str]:
        return [m.content for m in self.messages if m.role == "user"]

    def get_assistant_turns(self) -> list[str]:
        return [m.content for m in self.messages if m.role == "assistant"]

    def reset(self) -> None:
        self.messages.clear()

    def num_turns(self) -> int:
        return len([m for m in self.messages if m.role == "user"])

    def to_deepeval_format(self) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def contains_info(self, info: str) -> bool:
        return any(
            info.lower() in m.content.lower()
            for m in self.messages
            if m.role == "assistant"
        )

    def detect_contradiction(self, keyword: str, value_a: str, value_b: str) -> bool:
        turns = self.get_assistant_turns()
        found_a = any(f"{keyword}.*{value_a}" in t or f"{value_a}.*{keyword}" in t
                      for t in turns)
        found_b = any(f"{keyword}.*{value_b}" in t or f"{value_b}.*{keyword}" in t
                      for t in turns)
        return found_a and found_b
