from __future__ import annotations

from dbl_policy.model import PolicyContext, TenantId

from dbl_policy_gates import Bound, chain


def test_same_context_same_gate_same_result() -> None:
    gate = chain(Bound("max_output_tokens", 1, 4096))
    context = PolicyContext(
        tenant_id=TenantId("tenant-1"),
        inputs={"max_output_tokens": 1024},
    )
    assert gate.evaluate(context) == gate.evaluate(context)


def test_policy_context_snapshot_keeps_gate_deterministic() -> None:
    raw = {"max_output_tokens": 1024}
    context = PolicyContext(tenant_id=TenantId("tenant-1"), inputs=raw)
    raw["max_output_tokens"] = 999999
    decision = Bound("max_output_tokens", 1, 4096).evaluate(context)
    assert decision.reason_code == "gate.allow"
