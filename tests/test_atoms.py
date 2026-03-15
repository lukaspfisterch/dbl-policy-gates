from __future__ import annotations

from dbl_policy.model import DecisionOutcome, PolicyContext, TenantId

from dbl_policy_gates import Bound, Match, OneOf, Require, Tenant


def _context(**inputs: object) -> PolicyContext:
    return PolicyContext(tenant_id=TenantId("tenant-1"), inputs=inputs)


def test_require_missing() -> None:
    decision = Require("capability", label="capability_present").evaluate(_context())
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.require.missing:capability"
    assert decision.detail == {
        "key": "capability",
        "label": "capability_present",
    }


def test_match_mismatch() -> None:
    decision = Match("capability", "chat", label="chat_capability").evaluate(
        _context(capability="search")
    )
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.match.mismatch:capability"
    assert decision.detail == {
        "actual": "search",
        "expected": "chat",
        "key": "capability",
        "label": "chat_capability",
    }


def test_one_of_sorts_allowed() -> None:
    gate = OneOf("provider", ("anthropic", "openai", "anthropic"))
    assert gate.allowed == ("anthropic", "openai")


def test_bound_above_produces_structured_detail() -> None:
    decision = Bound(
        "max_output_tokens",
        1,
        4096,
        label="output_token_limit",
    ).evaluate(_context(max_output_tokens=5000))
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.bound.above:max_output_tokens"
    assert decision.detail == {
        "actual": 5000,
        "hi": 4096,
        "key": "max_output_tokens",
        "label": "output_token_limit",
    }


def test_tenant_denied() -> None:
    decision = Tenant(("tenant-2",), label="tenant_allowlist").evaluate(
        _context(intent_type="chat.message")
    )
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.tenant.denied"
    assert decision.detail == {
        "tenant_id": "tenant-1",
        "label": "tenant_allowlist",
    }
