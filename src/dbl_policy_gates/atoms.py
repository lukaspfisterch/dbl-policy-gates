"""Atomic gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dbl_policy.model import PolicyContext

from ._base import _allow, _deny, _describe_dict, _detail_with_label, GateDecision
from ._reason import reason


@dataclass(frozen=True)
class Require:
    key: str
    label: str | None = None

    def evaluate(self, context: PolicyContext) -> GateDecision:
        if self.key not in context.inputs:
            return _deny(
                reason("require", "missing", self.key),
                _detail_with_label({"key": self.key}, self.label),
            )
        return _allow()

    def describe(self) -> dict[str, Any]:
        return _describe_dict("require", key=self.key, label=self.label)


@dataclass(frozen=True)
class Match:
    key: str
    value: str | int | bool
    label: str | None = None

    def evaluate(self, context: PolicyContext) -> GateDecision:
        if self.key not in context.inputs:
            return _deny(
                reason("match", "missing", self.key),
                _detail_with_label({"key": self.key}, self.label),
            )
        actual = context.inputs[self.key]
        if actual != self.value:
            return _deny(
                reason("match", "mismatch", self.key),
                _detail_with_label(
                    {"actual": actual, "expected": self.value, "key": self.key},
                    self.label,
                ),
            )
        return _allow()

    def describe(self) -> dict[str, Any]:
        return _describe_dict("match", key=self.key, value=self.value, label=self.label)


@dataclass(frozen=True)
class OneOf:
    key: str
    allowed: tuple[str, ...]
    label: str | None = None

    def __post_init__(self) -> None:
        normalized = tuple(sorted(set(self.allowed)))
        if not normalized:
            raise ValueError("allowed must not be empty")
        object.__setattr__(self, "allowed", normalized)

    def evaluate(self, context: PolicyContext) -> GateDecision:
        if self.key not in context.inputs:
            return _deny(
                reason("one_of", "missing", self.key),
                _detail_with_label({"key": self.key}, self.label),
            )
        actual = context.inputs[self.key]
        if actual not in self.allowed:
            return _deny(
                reason("one_of", "mismatch", self.key),
                _detail_with_label(
                    {"actual": actual, "allowed": list(self.allowed), "key": self.key},
                    self.label,
                ),
            )
        return _allow()

    def describe(self) -> dict[str, Any]:
        return _describe_dict(
            "one_of",
            key=self.key,
            allowed=list(self.allowed),
            label=self.label,
        )


@dataclass(frozen=True)
class Bound:
    key: str
    lo: int
    hi: int
    label: str | None = None

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError("lo must be <= hi")

    def evaluate(self, context: PolicyContext) -> GateDecision:
        if self.key not in context.inputs:
            return _deny(
                reason("bound", "missing", self.key),
                _detail_with_label({"key": self.key}, self.label),
            )
        actual = context.inputs[self.key]
        if type(actual) is not int:
            return _deny(
                reason("bound", "not_int", self.key),
                _detail_with_label(
                    {"actual_type": type(actual).__name__, "key": self.key},
                    self.label,
                ),
            )
        if actual < self.lo:
            return _deny(
                reason("bound", "below", self.key),
                _detail_with_label(
                    {"actual": actual, "key": self.key, "lo": self.lo},
                    self.label,
                ),
            )
        if actual > self.hi:
            return _deny(
                reason("bound", "above", self.key),
                _detail_with_label(
                    {"actual": actual, "hi": self.hi, "key": self.key},
                    self.label,
                ),
            )
        return _allow()

    def describe(self) -> dict[str, Any]:
        return _describe_dict(
            "bound",
            key=self.key,
            lo=self.lo,
            hi=self.hi,
            label=self.label,
        )


@dataclass(frozen=True)
class Tenant:
    allowed: tuple[str, ...]
    label: str | None = None

    def __post_init__(self) -> None:
        normalized = tuple(sorted(set(self.allowed)))
        if not normalized:
            raise ValueError("allowed must not be empty")
        object.__setattr__(self, "allowed", normalized)

    def evaluate(self, context: PolicyContext) -> GateDecision:
        if context.tenant_id.value not in self.allowed:
            return _deny(
                reason("tenant", "denied"),
                _detail_with_label({"tenant_id": context.tenant_id.value}, self.label),
            )
        return _allow()

    def describe(self) -> dict[str, Any]:
        return _describe_dict("tenant", allowed=list(self.allowed), label=self.label)


@dataclass(frozen=True)
class Allow:
    label: str | None = None

    def evaluate(self, context: PolicyContext) -> GateDecision:
        return _allow()

    def describe(self) -> dict[str, Any]:
        return _describe_dict("allow", label=self.label)


@dataclass(frozen=True)
class Deny:
    label: str | None = None

    def evaluate(self, context: PolicyContext) -> GateDecision:
        return _deny("gate.deny", _detail_with_label(None, self.label))

    def describe(self) -> dict[str, Any]:
        return _describe_dict("deny", label=self.label)
