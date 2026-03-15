from __future__ import annotations

from dbl_policy.model import PolicyId, PolicyVersion

from dbl_policy_gates import Bound, Match, RootPolicy, chain, describe_digest, tree_payload


def test_tree_payload_projects_root_policy_to_tree() -> None:
    policy = RootPolicy(
        policy_id=PolicyId("chat.guardrails"),
        policy_version=PolicyVersion("1.0.0"),
        root=chain(
            Match("capability", "chat", label="chat_capability"),
            Bound("max_output_tokens", 1, 4096, label="output_token_limit"),
            label="guardrail_chain",
        ),
    )

    payload = tree_payload(policy)

    assert payload["digest"] == describe_digest(policy)
    assert payload["tree"]["path"] == "root"
    assert payload["tree"]["kind"] == "root_policy"
    assert payload["tree"]["meta"] == {
        "policy_id": "chat.guardrails",
        "policy_version": "1.0.0",
    }

    root_child = payload["tree"]["children"][0]
    assert root_child["path"] == "root.root"
    assert root_child["kind"] == "chain"
    assert root_child["label"] == "guardrail_chain"
    assert len(root_child["children"]) == 2

    match_node = root_child["children"][0]
    assert match_node["path"] == "root.root.gates[0]"
    assert match_node["kind"] == "match"
    assert match_node["label"] == "chat_capability"
    assert match_node["meta"] == {"key": "capability", "value": "chat"}
    assert match_node["children"] == []

    bound_node = root_child["children"][1]
    assert bound_node["path"] == "root.root.gates[1]"
    assert bound_node["kind"] == "bound"
    assert bound_node["label"] == "output_token_limit"
    assert bound_node["meta"] == {
        "key": "max_output_tokens",
        "lo": 1,
        "hi": 4096,
    }
    assert bound_node["children"] == []


def test_tree_payload_accepts_raw_describe_dict() -> None:
    description = {
        "describe_version": 1,
        "type": "invert",
        "label": "not_blocked",
        "inner": {
            "describe_version": 1,
            "type": "deny",
            "label": "always_block",
        },
    }

    payload = tree_payload(description)

    assert payload["digest"] == describe_digest(description)
    assert payload["tree"]["path"] == "root"
    assert payload["tree"]["kind"] == "invert"
    assert payload["tree"]["label"] == "not_blocked"
    assert payload["tree"]["children"][0] == {
        "path": "root.inner",
        "kind": "deny",
        "label": "always_block",
        "meta": {},
        "children": [],
    }
