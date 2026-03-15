from __future__ import annotations

from dbl_policy.model import PolicyId, PolicyVersion

from dbl_policy_gates import Bound, OneOf, RootPolicy, any_of, describe_digest, describe_json


def test_describe_json_is_canonical() -> None:
    gate = Bound("max_output_tokens", 1, 4096, label="output_token_limit")
    assert (
        describe_json(gate)
        == '{"describe_version":1,"hi":4096,"key":"max_output_tokens","label":"output_token_limit","lo":1,"type":"bound"}'
    )


def test_describe_digest_is_stable() -> None:
    gate1 = any_of(
        OneOf("provider", ("openai", "anthropic")),
        Bound("max_output_tokens", 1, 4096),
    )
    gate2 = any_of(
        OneOf("provider", ("anthropic", "openai", "openai")),
        Bound("max_output_tokens", 1, 4096),
    )
    assert describe_digest(gate1) == describe_digest(gate2)


def test_root_policy_describe_includes_identity() -> None:
    policy = RootPolicy(
        policy_id=PolicyId("chat.guardrails"),
        policy_version=PolicyVersion("1.0.0"),
        root=Bound("max_output_tokens", 1, 4096),
    )
    assert policy.describe()["policy_id"] == "chat.guardrails"
    assert policy.describe()["policy_version"] == "1.0.0"
