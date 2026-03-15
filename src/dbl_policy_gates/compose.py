"""Gate combinators."""

from __future__ import annotations

from dataclasses import dataclass

from dbl_policy.model import DecisionOutcome, PolicyContext

from ._base import _allow, _deny, _describe_dict, _detail_with_label, Gate, GateDecision


@dataclass(frozen=True)
class Chain:
    gates: tuple[Gate, ...]
    label: str | None = None

    def __post_init__(self) -> None:
        if not self.gates:
            raise ValueError("chain requires at least one gate")

    def evaluate(self, context: PolicyContext) -> GateDecision:
        for gate in self.gates:
            decision = gate.evaluate(context)
            if decision.outcome == DecisionOutcome.DENY:
                return decision
        return _allow()

    def describe(self) -> dict[str, object]:
        return _describe_dict(
            "chain",
            gates=[gate.describe() for gate in self.gates],
            label=self.label,
        )


@dataclass(frozen=True)
class AnyOf:
    gates: tuple[Gate, ...]
    label: str | None = None

    def __post_init__(self) -> None:
        if not self.gates:
            raise ValueError("any_of requires at least one gate")

    def evaluate(self, context: PolicyContext) -> GateDecision:
        last_deny: GateDecision | None = None
        for gate in self.gates:
            decision = gate.evaluate(context)
            if decision.outcome == DecisionOutcome.ALLOW:
                return _allow()
            last_deny = decision
        detail = _detail_with_label(last_deny.detail if last_deny else None, self.label)
        return _deny("gate.any_of.all_denied", detail)

    def describe(self) -> dict[str, object]:
        return _describe_dict(
            "any_of",
            gates=[gate.describe() for gate in self.gates],
            label=self.label,
        )


@dataclass(frozen=True)
class Invert:
    inner: Gate
    label: str | None = None

    def evaluate(self, context: PolicyContext) -> GateDecision:
        decision = self.inner.evaluate(context)
        if decision.outcome == DecisionOutcome.ALLOW:
            return _deny(
                "gate.invert.inverted_allow",
                _detail_with_label({"inverted_from": "ALLOW"}, self.label),
            )
        return _allow()

    def describe(self) -> dict[str, object]:
        return _describe_dict(
            "invert",
            inner=self.inner.describe(),
            label=self.label,
        )


def chain(*gates: Gate, label: str | None = None) -> Chain:
    return Chain(gates=tuple(gates), label=label)


def any_of(*gates: Gate, label: str | None = None) -> AnyOf:
    return AnyOf(gates=tuple(gates), label=label)


def invert(gate: Gate, *, label: str | None = None) -> Invert:
    return Invert(inner=gate, label=label)
