---
id: per-aggregate-tests
title: Every aggregate behavior ships with its per-aggregate tests
tag: judgment
since: 1.50.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#testing
verified: 2026-06-20
drained: no
---

# Every aggregate behavior ships with its per-aggregate tests

## Statement

Each aggregate has its own test class in the module's test project; every command handled adds tests covering the `Handle` outcomes (emitted events and failure paths) and the `Apply` state transition. New behavior without its tests does not merge.

## Why

Pure-function aggregates are cheap to test and the tests are the executable specification of domain behavior; untested handlers are where regressions ship at framework-upgrade time.

## Conformant example

`PartyRegistrationTests` covering `Handle` success, rejection, and `Apply` — one class per aggregate in `test/<Module>.Tests`.
