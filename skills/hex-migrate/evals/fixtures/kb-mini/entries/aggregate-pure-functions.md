---
id: aggregate-pure-functions
title: Aggregates are pure functions over immutable state
tag: mechanical
since: 1.70.0
until: ''
supersedes: aggregate-mutable-apply
provenance: framework:Hexalith@v1.70.0
verified: 2026-07-01
drained: na
---

# Aggregates are pure functions over immutable state

## Statement

An aggregate is a pure function pair: `Handle(Command, State?) → DomainResult` produces the resulting events without touching state, and `Apply(Event)` returns a **new** immutable state record. No settable properties, no mutation, no side effects inside the aggregate.

## Why

Pure aggregates make replay, testing, and concurrent command handling trivial: the same inputs always produce the same events, and no hidden instance state can drift from the event stream. This is the 1.70.0 rework that replaced mutable `Apply`.

## Conformant example

`DomainResult result = PartyRegistration.Handle(command, state); PartyRegistrationState next = state.Apply(registered);` — see `Hexalith.Domains/IDomainAggregate.cs`.
