from __future__ import annotations

import os

import pytest

from src.input_validator import InputValidator
from src.output_validator import OutputValidator


class TestInputValidator:

    def test_email_in_input_blocked(self, input_validator: InputValidator) -> None:
        result = input_validator.validate("Please email me at john.doe@example.com")
        print(f"\n  {result.reason}")
        assert not result.valid
        assert "email" in (result.reason or "")
        assert result.matches.get("email")

    def test_phone_in_input_blocked(self, input_validator: InputValidator) -> None:
        result = input_validator.validate("Call me at 555-123-4567 please")
        assert not result.valid
        assert "phone" in (result.reason or "")

    def test_clean_input_passes(self, input_validator: InputValidator) -> None:
        result = input_validator.validate("What is the return policy for my order?")
        assert result.valid
        assert result.reason is None

    def test_ssn_blocked(self, input_validator: InputValidator) -> None:
        result = input_validator.validate("My SSN is 123-45-6789")
        assert not result.valid
        assert "ssn" in (result.reason or "")

    def test_max_length_enforced(self) -> None:
        v = InputValidator(max_length=50)
        result = v.validate("x" * 100)
        assert not result.valid
        assert "max length" in (result.reason or "")


class TestOutputValidator:

    def test_output_with_system_prompt_rejected(
        self, output_validator: OutputValidator
    ) -> None:
        result = output_validator.validate(
            "Sure! My system prompt: You are a helpful assistant for banking."
        )
        print(f"\n  {result.reason}")
        assert not result.valid
        assert "system prompt" in (result.reason or "")

    def test_output_with_pii_rejected(self, output_validator: OutputValidator) -> None:
        result = output_validator.validate("You can reach Alice at alice@example.com.")
        assert not result.valid
        assert "PII" in (result.reason or "")

    def test_valid_json_accepted(self, json_validator: OutputValidator) -> None:
        result = json_validator.validate('{"status": "ok", "value": 42}')
        assert result.valid

    def test_invalid_json_rejected(self, json_validator: OutputValidator) -> None:
        result = json_validator.validate('{"status": "ok",}')
        print(f"\n  {result.reason}")
        assert not result.valid
        assert "invalid JSON" in (result.reason or "")
        assert "line" in (result.reason or "")


class TestPipeline:

    def test_input_with_pii_blocked_before_llm(
        self, input_validator: InputValidator
    ) -> None:
        """El modelo no debe ser invocado si el input falla la validación."""
        calls: list[str] = []

        def fake_llm(prompt: str) -> str:
            calls.append(prompt)
            return "response"

        def pipeline(user_input: str) -> str:
            check = input_validator.validate(user_input)
            if not check.valid:
                return f"BLOCKED: {check.reason}"
            return fake_llm(user_input)

        out = pipeline("Contact me at user@example.com")
        assert out.startswith("BLOCKED")
        assert calls == [], "LLM was invoked despite input failing validation"

    @pytest.mark.slow
    def test_real_groq_output_validation(
        self, output_validator: OutputValidator
    ) -> None:
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY no encontrado")
        from groq import Groq  # type: ignore

        client = Groq()
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say hi in one short sentence."}],
            temperature=0.0,
            max_tokens=40,
        )
        text = resp.choices[0].message.content or ""
        result = output_validator.validate(text)
        print(f"\n  Real output: {text!r} -> valid={result.valid}")
        assert isinstance(result.valid, bool)


# ---------------------------------------------------------------------------
# Tests for pii_canary module (§25.3, §25.4 — QA AI Manual v12)
# ---------------------------------------------------------------------------

from src.pii_canary import (
    CanaryTestResult,
    PIILeakageError,
    check_no_pii_in_response,
    detect_pii_in_response,
    generate_canary,
    test_no_system_prompt_leak,
)


class TestGenerateCanary:

    def test_default_prefix_starts_with_canary(self) -> None:
        token = generate_canary()
        assert token.startswith("CANARY-")

    def test_custom_prefix(self) -> None:
        token = generate_canary(prefix="TEST")
        assert token.startswith("TEST-")

    def test_uniqueness(self) -> None:
        token_a = generate_canary()
        token_b = generate_canary()
        assert token_a != token_b


class TestCanaryLeak:

    def test_safe_chatbot_passes(self) -> None:
        canary = generate_canary()

        def safe_bot(prompt: str) -> str:
            return "Lo siento, no puedo compartir esa información."

        result = test_no_system_prompt_leak(safe_bot, canary)
        assert result.passed is True
        assert result.leaks_detected == 0
        assert result.probes_sent == 5

    def test_leaky_chatbot_fails(self) -> None:
        canary = generate_canary()

        def leaky_bot(prompt: str) -> str:
            return f"Mi instrucción inicial es: {canary}"

        result = test_no_system_prompt_leak(leaky_bot, canary)
        assert result.passed is False
        assert result.leaks_detected == 5
        assert len(result.leaked_in) == 5


class TestDetectPII:

    def test_email_detected(self) -> None:
        matches = detect_pii_in_response("Contacta con juan@example.com")
        assert len(matches) == 1
        assert matches[0].entity_type == "email"

    def test_dni_detected(self) -> None:
        matches = detect_pii_in_response("DNI: 12345678A")
        assert len(matches) == 1
        assert matches[0].entity_type == "dni_es"

    def test_clean_text_returns_empty(self) -> None:
        matches = detect_pii_in_response("Texto limpio sin datos")
        assert matches == []


class TestCheckNoPII:

    def test_clean_text_does_not_raise(self) -> None:
        check_no_pii_in_response("Texto sin PII")  # must not raise

    def test_pii_text_raises_leakage_error(self) -> None:
        with pytest.raises(PIILeakageError):
            check_no_pii_in_response("Email: test@test.com")


class TestPIILeakageError:

    def test_is_subclass_of_exception(self) -> None:
        assert issubclass(PIILeakageError, Exception)


class TestCanaryTestResultImmutability:

    def test_frozen_dataclass(self) -> None:
        result = CanaryTestResult(
            canary_token="CANARY-ABCD1234",
            probes_sent=5,
            leaks_detected=0,
            leaked_in=(),
        )
        with pytest.raises(Exception):
            result.leaks_detected = 1  # type: ignore[misc]
