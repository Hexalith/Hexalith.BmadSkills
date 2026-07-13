---
id: command-polymorphic-serialization
title: Commands and events register for polymorphic serialization
tag: mechanical
since: 1.55.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#serialization
verified: 2026-07-01
drained: no
---

# Commands and events register for polymorphic serialization

## Statement

Every command and event record carries `[PolymorphicSerialization]` (Hexalith.PolymorphicSerializations). A contract type without the attribute deserializes as its base type and silently drops its payload in the event store.

## Why

Envelope serialization is polymorphic across the bus and the event store; the attribute registration is what makes a contract round-trip as itself instead of degrading to its base shape.

## Conformant example

`[PolymorphicSerialization] public record RegisterParty(string Id, string Name);`
