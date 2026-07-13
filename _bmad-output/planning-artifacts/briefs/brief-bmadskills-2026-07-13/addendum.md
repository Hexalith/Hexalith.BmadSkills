---
title: "Addendum — BMAD Hexalith Module"
status: final
created: 2026-07-13
updated: 2026-07-13
---

# Addendum: BMAD Hexalith Module

Depth that belongs downstream (PRD, architecture, skill design) rather than in the brief.

## Conventions Inventory (to be encoded by the skills)

Verified from Hexalith sources and `Hexalith.AI.Tools/hexalith-llm-instructions.md` in mid-July 2026 — this inventory is the raw material for the knowledge base:

- **Platform:** ASP.NET Core on .NET 10+ / C# 14, Dapr 1.18+, .NET Aspire 13.x for local orchestration. MIT-licensed, multi-tenant by contract (tenant/partition in every relevant contract), ULID identifiers.
- **Architecture:** vertical-slice DDD modules; each module is both a deployable microservice and a set of NuGet packages composable into a single app. CQRS + event sourcing with EventStore mandatory — EF Core or direct DB access for domain state is forbidden. Pure-function aggregates: `Handle(Command, State?) → DomainResult`, `Apply(Event)`. Projections as read-model handlers.
- **Module boundary rule:** domain modules contain domain code only (aggregates, commands, events, projections, query handlers) — no AppHost of their own, Aspire wiring, or persistence; all boilerplate comes from the platform's domain-service SDK in Hexalith.EventStore.
- **Packaging:** per-layer NuGet packages — Domain (`.Aggregates`, `.Abstractions`, `.Events`), Application (`.Commands`, `.Requests`, `.Application`, `.Projections`), Infrastructure (`.ApiServer`, `.WebServer`, `.WebApp`), Presentation (`.UI.Components`, `.UI.Pages`, `.Localizations`), plus `test/`. Central package management; shared `Hexalith.Builds` git submodule for build props and CI.
- **UI:** Blazor with Fluent UI Blazor V5, composed exclusively through FrontComposer.
- **Testing:** xUnit v3 + Shouldly + NSubstitute, tests organized per aggregate.
- **Tooling/process:** `.slnx` solutions only; Conventional Commits + semantic-release; SDK-built containers (no Dockerfiles); SonarCloud, Codacy, Coverity quality gates.

## Module Landscape (as of 2026-07)

- **Technical modules:** Hexalith (core), Builds, Commons, PolymorphicSerializations, EventStore, FrontComposer, Memories.
- **Domain modules:** Tenants, Parties, Inventories, Sales, Contacts, Documents, Timesheets, Conversations, Folders, Agents, Todos, Works, Dynamics365Finance connector.
- **Scale & cadence:** ~58 repos in the GitHub org (~53 original plus forks). Core at v1.72.3 (shipped Jan 2026; 162 releases), active weekly.

## Existing Assets Audit

| Asset | State | Disposition per this brief |
|---|---|---|
| `Hexalith.AI.Tools` (`hexalith-llm-instructions.md`) | Active, descriptive | Drained into this module; content deleted as it moves (decided) |
| `Hexalith.MyNewModule` + `initialize.ps1` | Working but template-rot risk | Superseded by the Create skill |
| `Hexalith.MyNewPackage` | Template | Superseded by Create/Extend (decided) |
| `Hexalith.Templates`, `HexalithApp` | Stale | Out of scope; revisit after v1 |
| `Hexalith.Docs` / readthedocs | Stale since Oct 2024 | Out of scope (docs-site generation explicitly out) |
| This repo's BMAD install (bmm, bmb, cis, tea, bmad-loop; 4 platforms) | Fresh (installed 2026-07-13) | The substrate the module builds on |

## Distribution Options (open question — parked analysis)

Candidate mechanisms for external adopters. Selection constraint from the brief's version-coupling question: whichever channel is chosen must let an adopter see which skill version matches their framework version.

1. BMAD installer pointed at this public repo (cleanest if BMAD v6 supports third-party module sources).
2. Released/versioned artifact (GitHub release or NuGet-style package) installed by script.
3. Git submodule pattern, mirroring how `Hexalith.Builds` is already shared across module repos — familiar to Hexalith users, but submodule ergonomics are a known tax.

## Parked / Downstream Notes

- **Unattended fleet maintenance:** the bmad-loop wiring (`.bmad-loop/policy.toml`, hook) suggests a future where Migrate/Enforce run unattended across all module repos on a schedule. Treated as vision, not v1 scope.
- **Meta-drift ritual:** candidate mechanism — a semantic-release checklist step in framework repos that opens an "update BmadSkills conventions" task whenever a convention-affecting release ships. Now a v1 scope item; still needs design. Stronger alternative: the framework publishes a machine-readable conventions manifest with each release and skills read it instead of memorizing conventions — a skill that never memorized the rules cannot lag behind them. Caveat: this requires a framework change, which the brief currently scopes out; adopting it means amending scope.
- **Enforce tiering:** mechanical conventions (EventStore-mandatory, ULIDs, per-layer package shape) are pattern-matching, not judgment — enforceable at compile time by a Roslyn analyzer distributed through `Hexalith.Builds`, which every module repo already pulls. Reserving the LLM skill for judgment calls ("is this migration safe?") sharply lowers what the "Enforce still enabled after three months" criterion costs to sustain. PRD/architecture decision.
- **Cheap migration as moral hazard:** migration pain is today's only brake on convention churn; if Migrate removes it, nothing pushes the preview framework toward a stable release. Worth revisiting when 1.0 planning starts.
- **Audience verbosity knob:** rather than sequencing audiences, one skill with two verbosity modes — terse for the author who knows the why, explain-as-you-go for adopters with no context. Cheaper than two roadmaps; dissolves the v1-audience tension at the design level instead of settling it.
- **Skill granularity:** whether the four jobs are four skills or four families of finer-grained skills (e.g., extend-aggregate vs extend-ui-page) is a PRD/architecture decision, deliberately not fixed here.
