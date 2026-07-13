---
id: aggregate-handle-signature
title: Pure-function aggregate command handling
tag: judgment
since: 1.55.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#aggregates
verified: ''
drained: no
---

# Pure-function aggregate command handling

## Statement

Aggregates are pure functions: commands are handled through `ExecutionResult Handle(object command)` and state transitions through `IDomainAggregate Apply(object domainEvent)`. No I/O and no persistence access inside the aggregate.

## Why

Pure aggregates are trivially unit-testable and replayable from the event stream; any side effect inside `Handle` or `Apply` breaks event-sourcing determinism.

## Conformant example

See `Hexalith.Domains/IDomainAggregate.cs`.
