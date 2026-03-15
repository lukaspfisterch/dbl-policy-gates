# Policy Viewer

## Purpose

This document defines the architecture direction for a visual policy viewer on
top of `dbl-policy-gates`.

The goal is to make the policy algebra visible without introducing a second
policy language, a builder DSL, or UI-specific semantics into the algebra
itself.

## Core idea

`describe()` is the canonical structural representation of a policy tree.

That means:

- the algebra produces structure
- the structure is the intermediate representation
- the viewer renders that structure

In compiler terms, the viewer operates on the policy AST.

## Motivation

`dbl-gateway` already shows the temporal flow of the system:

```text
INTENT -> DECISION -> PROOF -> EXECUTION
```

A policy viewer would show the structural side:

```text
inputs -> policy tree -> decision
```

Together, these two views make the DBL model legible:

- execution flow shows what happened in time
- policy tree shows how governance is structured

## Design constraints

The viewer must preserve the current algebraic design.

Required constraints:

- no new policy language
- no YAML or JSON DSL in the algebra core
- no hidden evaluation semantics in the viewer
- no UI-specific fields in gate evaluation logic
- no duplication of canonical structure outside `describe()`

The viewer is a renderer, not a second source of truth.

## Architectural split

### 1. Algebra core

Lives in `dbl-policy-gates`.

Responsibilities:

- define gate atoms and combinators
- evaluate deterministic gate trees
- produce canonical structure with `describe()`
- produce structural identity with `describe_digest()`

Non-responsibilities:

- layout
- graph rendering
- interaction
- policy editing

### 2. Viewer adapter

Can live in `dbl-policy-gates` as pure helper code, or in a separate UI-facing
package if needed later.

Responsibilities:

- traverse a `describe()` tree
- produce nodes and edges
- attach node metadata derived from the structure

This layer should remain pure and deterministic.

Example responsibility:

```text
describe dict -> tree payload
describe dict -> graph payload
```

### 3. UI surface

Can live in `dbl-gateway` or in a dedicated demo tool.

Responsibilities:

- render the tree
- show labels and parameters
- show the policy digest
- optionally overlay evaluation results

The UI should not define policy semantics. It should only display them.

## Canonical input

The canonical input to the viewer is the output of `describe()`.

That is important because:

- it is already deterministic
- it is already JSON-safe
- it is already recursive
- it already carries gate types, labels, and parameters
- it already has a digestable canonical form

The viewer should not invent an alternative internal schema unless it is a
strict projection derived from `describe()`.

## Suggested viewer data model

Minimal viewer payload:

```python
{
  "root": {
    "id": "root",
    "kind": "root_policy",
    "label": None,
    "meta": {...},
  },
  "nodes": [...],
  "edges": [...],
  "digest": "...",
}
```

Each node should be derivable from a structural path.

Example path conventions:

- `root`
- `root.gates[0]`
- `root.gates[2].gates[1]`
- `root.inner`

This gives the viewer a stable local identity without introducing new semantic
IDs into the gate model.

## Evaluation overlay

The first viewer should be structural.

An optional second layer can add evaluation overlay:

- input values used for a test run
- ALLOW or DENY result
- the path that was traversed
- the gate that produced the decisive DENY

This overlay must remain separate from the structure itself.

The structure is canonical.
The overlay is a run-specific projection.

## MVP

The smallest useful viewer is:

1. Accept a `RootPolicy`
2. Render the policy tree
3. Show gate type, label, and parameters
4. Show `describe_digest(root.describe())`
5. Optionally evaluate sample inputs and highlight the decisive path

This is enough to make the algebra legible without expanding the core design.

## Non-goals

For the first iteration:

- no policy builder
- no drag-and-drop editor
- no persistence format beyond `describe()`
- no automatic policy authoring
- no additional gate types just to improve visuals

The purpose is explanation, not authoring.

## Placement recommendation

Recommended split:

- keep structural helpers close to `dbl-policy-gates`
- place interactive visualization in `dbl-gateway` or a demo-oriented surface

Reason:

- `dbl-policy-gates` owns the algebra and canonical structure
- `dbl-gateway` already owns the strongest live demo surface in the stack

This keeps the algebra pure while reusing the existing observer and demo
experience.
