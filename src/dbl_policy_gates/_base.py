"""Gate primitives and root policy adapter."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping, Protocol

from dbl_policy.model import (
    DecisionOutcome,
    PolicyContext,
    PolicyDecision,
    PolicyId,
    PolicyVersion,
)
from dbl_policy.validation import ensure_json_safe


@dataclass(frozen=True)
class GateDecision:
    outcome: DecisionOutcome
    reason_code: str
    detail: Mapping[str, Any] | None = None


class Gate(Protocol):
    def evaluate(self, context: PolicyContext) -> GateDecision:
        ...

    def describe(self) -> dict[str, Any]:
        ...


def _detail_json(detail: Mapping[str, Any] | None) -> str | None:
    if not detail:
        return None
    ensure_json_safe(detail)
    return json.dumps(
        detail,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _allow(reason_code: str = "gate.allow") -> GateDecision:
    return GateDecision(
        outcome=DecisionOutcome.ALLOW,
        reason_code=reason_code,
        detail=None,
    )


def _deny(reason_code: str, detail: Mapping[str, Any] | None = None) -> GateDecision:
    return GateDecision(
        outcome=DecisionOutcome.DENY,
        reason_code=reason_code,
        detail=detail,
    )


def _detail_with_label(
    detail: Mapping[str, Any] | None,
    label: str | None,
) -> dict[str, Any] | None:
    if detail is None and label is None:
        return None
    data = dict(detail or {})
    if label is not None:
        data["label"] = label
    return data


def _describe_dict(kind: str, *, label: str | None = None, **fields: Any) -> dict[str, Any]:
    description: dict[str, Any] = {
        "describe_version": 1,
        "type": kind,
    }
    description.update(fields)
    if label is not None:
        description["label"] = label
    return description


@dataclass(frozen=True)
class RootPolicy:
    policy_id: PolicyId
    policy_version: PolicyVersion
    root: Gate

    def evaluate(self, context: PolicyContext) -> PolicyDecision:
        decision = self.root.evaluate(context)
        return PolicyDecision(
            outcome=decision.outcome,
            reason_code=decision.reason_code,
            reason_message=_detail_json(decision.detail),
            policy_id=self.policy_id,
            policy_version=self.policy_version,
            tenant_id=context.tenant_id,
            authoritative_digest=context.compute_authoritative_digest(),
        )

    def describe(self) -> dict[str, Any]:
        return {
            "describe_version": 1,
            "type": "root_policy",
            "policy_id": self.policy_id.value,
            "policy_version": self.policy_version.value,
            "root": self.root.describe(),
        }
