---
id: command-contract-shape
title: Commands are imperative records, events are past-tense records
tag: judgment
since: 1.40.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#contracts
verified: 2026-07-01
drained: no
---

# Commands are imperative records, events are past-tense records

## Statement

A command is an immutable record named as an imperative verb phrase (`RegisterParty`, `SuspendParty`), carrying the target aggregate id (`Id`, a ULID string) and only the data the decision needs. Its events are past-tense records (`PartyRegistered`, `PartySuspended`) carrying what changed.

## Why

Commands are intent, events are fact; the naming and shape keep the event stream readable as business history, and the shared ULID `Id` ties both to their aggregate stream.

## Conformant example

`public record SuspendParty(string Id, string Reason);` handled into `public record PartySuspended(string Id, string Reason);`
