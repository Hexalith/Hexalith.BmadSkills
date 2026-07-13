---
id: ulid-identifiers
title: ULID identifiers everywhere
tag: mechanical
since: 1.40.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#identifiers
verified: 2026-07-01
drained: no
---

# ULID identifiers everywhere

## Statement

All entity, aggregate, command, and event identifiers are ULID strings generated through `UniqueIdHelper.GenerateUniqueStringId()`. GUIDs and database-generated integer ids are forbidden.

## Why

ULIDs sort lexicographically by creation time, keeping event streams and projections naturally ordered without a database round-trip, and stay unique across distributed services.

## Conformant example

`string id = UniqueIdHelper.GenerateUniqueStringId();` — see `Hexalith.Commons/UniqueIdHelper.cs`.
