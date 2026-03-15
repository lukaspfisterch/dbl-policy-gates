"""Deterministic structural reason-code helpers."""

from __future__ import annotations


def reason(gate_type: str, condition: str, key: str | None = None) -> str:
    if key is not None:
        return f"gate.{gate_type}.{condition}:{key}"
    return f"gate.{gate_type}.{condition}"
