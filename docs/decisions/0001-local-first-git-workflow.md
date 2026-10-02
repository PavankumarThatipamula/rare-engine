# ADR 0001: Local-First Git Workflow & Agent Isolation

## Status
Accepted

## Context
Developing with autonomous agents requires guardrails to prevent unverified code pushes, broken builds, and monolithic refactors directly on `main`.

## Decision
1. All changes must originate on local phase branches (`phase/XX-name`).
2. Agents must execute tests locally before presenting code for human commit.
3. No code is committed directly to `main`.
4. Outer dependencies will be introduced incrementally when strictly required.

## Consequences
- Requires explicit branch creation before starting work on a new phase.
- Prevents drift and ensures complete auditability of agent-generated modifications.