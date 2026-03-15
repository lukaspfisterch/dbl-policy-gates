"""Pure helpers for projecting gate descriptions into viewer payloads."""

from __future__ import annotations

from typing import Any

from .describe import Describable, describe_digest


_STRUCTURAL_KEYS = frozenset({
    "describe_version",
    "type",
    "label",
    "root",
    "gates",
    "inner",
})


def tree_payload(target: Describable | dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic tree payload for viewer rendering."""
    description = target.describe() if hasattr(target, "describe") else target
    return {
        "digest": describe_digest(description),
        "tree": _tree_node(description, path="root"),
    }


def _tree_node(description: dict[str, Any], *, path: str) -> dict[str, Any]:
    kind = description["type"]
    label = description.get("label")
    children = _children(description, path=path)
    meta = {
        key: value
        for key, value in description.items()
        if key not in _STRUCTURAL_KEYS
    }
    return {
        "path": path,
        "kind": kind,
        "label": label,
        "meta": meta,
        "children": children,
    }


def _children(description: dict[str, Any], *, path: str) -> list[dict[str, Any]]:
    kind = description["type"]
    if kind == "root_policy":
        return [_tree_node(description["root"], path=f"{path}.root")]
    if kind in {"chain", "any_of"}:
        return [
            _tree_node(child, path=f"{path}.gates[{index}]")
            for index, child in enumerate(description["gates"])
        ]
    if kind == "invert":
        return [_tree_node(description["inner"], path=f"{path}.inner")]
    return []
