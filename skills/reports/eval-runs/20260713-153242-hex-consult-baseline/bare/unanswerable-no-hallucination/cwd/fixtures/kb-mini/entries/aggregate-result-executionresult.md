---
id: aggregate-result-executionresult
title: Aggregate Handle returns ExecutionResult
tag: mechanical
since: 1.50.0
until: 1.72.0
supersedes: ''
provenance: framework:Hexalith.Domains@1.50.0
verified: 2026-06-20
drained: na
---

# Aggregate Handle returns ExecutionResult

## Statement

An aggregate handles a command through the pure function `ExecutionResult Handle(command, state)`; the result carries the produced events and the success or failure of the command.

## Why

A pure command handler keeps the aggregate deterministic and unit-testable without infrastructure; the result type makes failure an explicit value instead of an exception.

## Conformant example

`ExecutionResult result = aggregate.Handle(command, state);` — see `Hexalith.Domains/IDomainAggregate.cs` at 1.50.0.
