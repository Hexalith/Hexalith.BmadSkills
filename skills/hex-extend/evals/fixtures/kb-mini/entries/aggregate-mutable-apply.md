---
id: aggregate-mutable-apply
title: Aggregates apply events by mutating state
tag: mechanical
since: 1.40.0
until: 1.70.0
supersedes: ''
provenance: framework:Hexalith@v1.40.0
verified: 2026-05-02
drained: na
---

# Aggregates apply events by mutating state

## Statement

An aggregate handles a command on its instance (`void Handle(Command)`) and applies events by mutating its own properties (`void Apply(Event)`). State lives in settable properties on the aggregate class.

## Why

The original aggregate shape, before the pure-function rework: mutation kept the event-sourcing loop simple while the framework was single-service. Superseded in 1.70.0 by `aggregate-pure-functions` — kept as a from-state so migrations can recognize pre-1.70 aggregates.

## Conformant example

Historical only — see `aggregate-pure-functions` for the current shape.
