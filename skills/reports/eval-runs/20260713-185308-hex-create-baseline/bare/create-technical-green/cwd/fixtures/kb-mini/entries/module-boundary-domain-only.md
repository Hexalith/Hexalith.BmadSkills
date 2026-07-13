---
id: module-boundary-domain-only
title: Domain modules contain domain code only
tag: judgment
since: 1.60.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#module-boundary
verified: 2026-06-15
drained: no
---

# Domain modules contain domain code only

## Statement

A domain module carries aggregates, commands, events, projections, and request handlers — nothing else. No AppHost, no Aspire wiring, no persistence infrastructure (DbContexts, repositories, storage clients). Hosting and persistence boilerplate comes from Hexalith.EventStore's domain-service SDK.

## Why

The module boundary is what lets ~20 domain modules ride one infrastructure upgrade: when persistence and hosting live only in the SDK, a framework release updates them everywhere at once. A DbContext inside a domain module pins that module to an infrastructure choice the framework no longer owns.

## Conformant example

`Parties.Domain` referencing only `Hexalith.Domains` and `Hexalith.Commons`; hosting comes from the `HexalithApp` SDK packages — see `docs/module-structure.md` in framework source.
