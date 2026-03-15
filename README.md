# dbl-policy-gates

[![Tests](https://github.com/lukaspfisterch/dbl-policy-gates/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/lukaspfisterch/dbl-policy-gates/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/dbl-policy-gates.svg)](https://pypi.org/project/dbl-policy-gates/)
[![Python >=3.11](https://img.shields.io/pypi/pyversions/dbl-policy-gates.svg?label=Python)](https://pypi.org/project/dbl-policy-gates/)
[![Typing: Typed](https://img.shields.io/badge/typing-typed-2d7f5e.svg)](https://pypi.org/project/dbl-policy-gates/)

Deterministic gate algebra for `dbl-policy`.

This package provides the primitive gate operations used to build governance
functions. It does not execute tasks, emit events, or observe runtime
artifacts.

## Position in the Stack

```text
execution-without-normativity
    -> dbl-core
    -> dbl-policy
    -> dbl-policy-gates
    -> domain policies
```

`dbl-policy` defines the contract for policy decisions.
`dbl-policy-gates` defines the algebra used to assemble them.

## Model

There are two layers in this package:

- `Gate`: deterministic structure that evaluates to a gate-local decision
- `RootPolicy`: wrapper that stamps a gate decision into a
  `dbl_policy.model.PolicyDecision`

This split is intentional. Gates remain anonymous structure; only the root
policy carries `policy_id` and `policy_version`.

## Install

```bash
pip install dbl-policy-gates
```

Requires Python 3.11+ and `dbl-policy>=0.3,<0.4`.

## Quickstart

```python
from dbl_policy.model import PolicyId, PolicyVersion, PolicyContext, TenantId
from dbl_policy_gates import Bound, Match, RootPolicy, chain

root = RootPolicy(
    policy_id=PolicyId("chat.guardrails"),
    policy_version=PolicyVersion("1.0.0"),
    root=chain(
        Match("capability", "chat", label="chat_capability"),
        Bound("max_output_tokens", 1, 4096, label="output_token_limit"),
    ),
)

ctx = PolicyContext(
    tenant_id=TenantId("tenant-1"),
    inputs={"capability": "chat", "max_output_tokens": 512},
)

decision = root.evaluate(ctx)
```

## Included Gates

- `Require`
- `Match`
- `OneOf`
- `Bound`
- `Tenant`
- `Allow`
- `Deny`
- `Chain`
- `AnyOf`
- `Invert`

`Chain` and `AnyOf` require at least one child gate. Empty combinators are
rejected at construction time.

## Describe and Drift

Every gate implements `describe()`.

Use `describe_digest(gate)` to get a stable SHA-256 digest of the canonical gate
description. This is intended for drift detection and replay tooling.

## Structured Reason Detail

Gates produce structural `reason_code` values such as:

```text
gate.bound.above:max_output_tokens
```

When a `RootPolicy` converts a gate denial into `PolicyDecision`, the gate
detail dict is serialized into canonical JSON for `reason_message`.

Example:

```text
{"actual":5000,"hi":4096,"key":"max_output_tokens","label":"output_token_limit"}
```

## Development

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```
