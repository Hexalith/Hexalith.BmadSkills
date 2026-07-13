---
id: projection-registration
title: Manual projection factory registration
tag: mechanical
since: 1.58.0
until: ''
supersedes: ''
provenance: framework:Hexalith@v1.58.0
verified: ''
drained: na
---

# Manual projection factory registration

## Statement

Projections register through explicit `IProjectionFactory` wiring in the web server setup: each read-model handler is added with `services.AddSingleton<IProjectionFactory<TState>, TFactory>()`.

## Why

Read-model handlers over the event stream are wired explicitly so the projection set of a service stays visible in one place.

## Conformant example

See `HexalithApp/ProjectionSetup.cs`.
