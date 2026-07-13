---
id: aggregate-result-domainresult
title: Aggregate Handle returns DomainResult
tag: mechanical
since: 1.72.0
until: ''
supersedes: aggregate-result-executionresult
provenance: framework:Hexalith.Domains@1.72.0
verified: ''
drained: na
---

# Aggregate Handle returns DomainResult

## Statement

An aggregate handles a command through the pure function `DomainResult Handle(command, state)`; `DomainResult` replaces `ExecutionResult` and carries the produced events plus a typed failure reason.

## Why

`ExecutionResult` conflated infrastructure and domain failures; `DomainResult` keeps the handler pure while making domain rejection reasons typed and testable.

## Conformant example

`DomainResult result = aggregate.Handle(command, state);` — see `Hexalith.Domains/IDomainAggregate.cs` since 1.72.0.
