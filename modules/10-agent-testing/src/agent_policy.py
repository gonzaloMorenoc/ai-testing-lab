from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class AgentPolicy:
    """Permission boundary + sandbox + budget para un agente (§18.6 Manual QA AI v12).

    Alineado con OWASP LLM06 (Excessive Agency).
    """

    allowed_tools: set[str] = field(default_factory=set)
    sandbox_root: str = "/tmp/sandbox"
    network_allowlist: set[str] = field(default_factory=set)
    max_iterations: int = 12
    max_cost_usd: float = 1.0
    max_tokens: int = 50_000
    human_approval_required: set[str] = field(
        default_factory=lambda: {"send_email", "execute_payment", "delete_record"}
    )


class PolicyViolationError(Exception):
    """El agente intentó una acción fuera de los límites de la política."""


def enforce_policy(
    tool: str,
    args: dict,
    policy: AgentPolicy,
    iterations_so_far: int,
    cost_so_far: float,
    human_approved: bool = False,
) -> None:
    """Verifica que una tool call cumpla la política. Lanza PolicyViolationError si no.

    Comprueba en orden: allowlist, max_iterations, budget, human_approval.
    """
    if tool not in policy.allowed_tools:
        raise PolicyViolationError(f"Tool fuera de allowlist: {tool!r}")
    if iterations_so_far >= policy.max_iterations:
        raise PolicyViolationError(
            f"max_iterations alcanzado ({iterations_so_far} >= {policy.max_iterations})"
        )
    if cost_so_far > policy.max_cost_usd:
        raise PolicyViolationError(
            f"Presupuesto USD agotado: {cost_so_far:.4f} > {policy.max_cost_usd}"
        )
    if tool in policy.human_approval_required and not human_approved:
        raise PolicyViolationError(
            f"Acción destructiva requiere aprobación humana: {tool!r}"
        )


# --- Tool Schema Validator (Cap 27) ---


@dataclass(frozen=True)
class SchemaValidationResult:
    valid: bool
    tool_name: str
    error: str | None = None


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_tool_call(
    tool_name: str, args: dict, tool_schemas: dict[str, dict]
) -> SchemaValidationResult:
    """Valida argumentos de una tool call contra su JSON Schema simplificado.

    Comprueba: tool registrada, required fields presentes, tipos básicos, format:email.
    (jsonschema.validate no activa format por defecto; este validator sí lo hace.)
    """
    if tool_name not in tool_schemas:
        return SchemaValidationResult(
            valid=False,
            tool_name=tool_name,
            error=f"Tool no registrada: {tool_name!r}",
        )

    schema = tool_schemas[tool_name]
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for field_name in required:
        if field_name not in args:
            return SchemaValidationResult(
                valid=False,
                tool_name=tool_name,
                error=f"Campo obligatorio ausente: {field_name!r}",
            )

    for field_name, value in args.items():
        prop = properties.get(field_name, {})
        expected_type = prop.get("type")
        if expected_type == "string" and not isinstance(value, str):
            return SchemaValidationResult(
                valid=False,
                tool_name=tool_name,
                error=f"{field_name!r} debe ser string, got {type(value).__name__}",
            )
        if expected_type == "string" and prop.get("format") == "email":
            if not _EMAIL_RE.match(value):
                return SchemaValidationResult(
                    valid=False,
                    tool_name=tool_name,
                    error=f"{field_name!r} no es un email válido: {value!r}",
                )
        max_length = prop.get("maxLength")
        if max_length is not None and isinstance(value, str) and len(value) > max_length:
            return SchemaValidationResult(
                valid=False,
                tool_name=tool_name,
                error=f"{field_name!r} excede maxLength={max_length} ({len(value)} chars)",
            )

    return SchemaValidationResult(valid=True, tool_name=tool_name)
