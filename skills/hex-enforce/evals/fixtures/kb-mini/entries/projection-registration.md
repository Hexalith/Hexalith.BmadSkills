---
id: projection-registration
title: Projections register through assembly scan
tag: mechanical
since: 1.55.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#projections
verified: 2026-07-01
drained: no
---

# Projections register through assembly scan

## Statement

Projection handlers are registered through `ProjectionSetup.AddProjections()` assembly scanning. Manual per-handler `services.AddScoped<...>` registration of projection handlers is forbidden.

## Why

Assembly scanning keeps registration complete by construction — a handler that compiles is a handler that runs. Manual registration silently drops handlers when someone forgets the wiring line.

## Conformant example

`services.AddProjections(typeof(Module).Assembly);` — see `HexalithApp/ProjectionSetup.cs`.
