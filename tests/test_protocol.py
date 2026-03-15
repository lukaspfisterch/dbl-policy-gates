from __future__ import annotations

from dbl_policy.model import PolicyContext, PolicyId, PolicyVersion, TenantId

from dbl_policy_gates import Match, RootPolicy


def test_root_policy_matches_dbl_policy_contract_shape() -> None:
    policy = RootPolicy(
        policy_id=PolicyId("chat.guardrails"),
        policy_version=PolicyVersion("1.0.0"),
        root=Match("capability", "chat", label="chat_capability"),
    )
    decision = policy.evaluate(
        PolicyContext(
            tenant_id=TenantId("tenant-1"),
            inputs={"capability": "search"},
        )
    )
    assert decision.policy_id.value == "chat.guardrails"
    assert decision.policy_version.value == "1.0.0"
    assert decision.tenant_id.value == "tenant-1"
    assert decision.reason_message == (
        '{"actual":"search","expected":"chat","key":"capability","label":"chat_capability"}'
    )
