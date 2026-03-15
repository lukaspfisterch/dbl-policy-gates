"""Canonical gate description utilities."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol

from dbl_policy.validation import ensure_json_safe


class Describable(Protocol):
    def describe(self) -> dict[str, Any]:
        ...


def describe_json(target: Describable | dict[str, Any]) -> str:
    value = target.describe() if hasattr(target, "describe") else target
    ensure_json_safe(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def describe_digest(target: Describable | dict[str, Any]) -> str:
    payload = describe_json(target).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
