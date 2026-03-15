from __future__ import annotations

import pytest

from dbl_policy.model import DecisionOutcome, PolicyContext, PolicyId, PolicyVersion, TenantId

from dbl_policy_gates import Bound, Match, RootPolicy, any_of, chain, invert


def _context(**inputs: object) -> PolicyContext:
    return PolicyContext(tenant_id=TenantId("tenant-1"), inputs=inputs)


def test_chain_stops_on_first_deny() -> None:
    gate = chain(
        Match("capability", "chat"),
        Bound("max_output_tokens", 1, 128),
    )
    decision = gate.evaluate(_context(capability="chat", max_output_tokens=200))
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.bound.above:max_output_tokens"


def test_any_of_all_denied() -> None:
    gate = any_of(
        Match("capability", "chat"),
        Match("provider", "openai"),
        label="fallback_check",
    )
    decision = gate.evaluate(_context(capability="search", provider="anthropic"))
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.any_of.all_denied"
    assert decision.detail == {
        "actual": "anthropic",
        "expected": "openai",
        "key": "provider",
        "label": "fallback_check",
    }


def test_invert_flips_allow_to_deny() -> None:
    decision = invert(Match("capability", "chat"), label="no_chat").evaluate(
        _context(capability="chat")
    )
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.invert.inverted_allow"
    assert decision.detail == {
        "inverted_from": "ALLOW",
        "label": "no_chat",
    }


def test_root_policy_converts_detail_to_reason_message() -> None:
    policy = RootPolicy(
        policy_id=PolicyId("chat.guardrails"),
        policy_version=PolicyVersion("1.0.0"),
        root=Bound("max_output_tokens", 1, 4096, label="output_token_limit"),
    )
    decision = policy.evaluate(_context(max_output_tokens=5000))
    assert decision.outcome == DecisionOutcome.DENY
    assert decision.reason_code == "gate.bound.above:max_output_tokens"
    assert (
        decision.reason_message
        == '{"actual":5000,"hi":4096,"key":"max_output_tokens","label":"output_token_limit"}'
    )
    assert decision.authoritative_digest != ""


def test_chain_requires_at_least_one_gate() -> None:
    with pytest.raises(ValueError, match="chain requires at least one gate"):
        chain()


def test_any_of_requires_at_least_one_gate() -> None:
    with pytest.raises(ValueError, match="any_of requires at least one gate"):
        any_of()
