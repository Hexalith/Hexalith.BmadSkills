---
id: module-skeleton-structure
title: A module repo is a .slnx over src and test project folders
tag: mechanical
since: 1.65.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#module-structure
verified: 2026-07-01
drained: no
---

# A module repo is a .slnx over src and test project folders

## Statement

A module repository is rooted by `{Module}.slnx` — an XML solution listing every
project as `<Project Path="..." />` — plus a `.gitignore` covering `bin/` and
`obj/`. Projects are named `{Module}.{Layer}` and live at
`src/{Module}.{Layer}/{Module}.{Layer}.csproj`; their tests live at
`test/{Module}.{Layer}.Tests/{Module}.{Layer}.Tests.csproj` with a
`ProjectReference` to the project under test. The minimal skeleton is the domain
layer pair: `src/{Module}.Domain` and `test/{Module}.Domain.Tests`. Every project
targets `net10.0` with `ImplicitUsings` and `Nullable` enabled. Every project in
the repo appears in the `.slnx`; a project on disk but absent from the solution
is a defect.

## Why

One solution file that names every project is what lets machines audit
completeness: build, test, and conformance gates all enumerate the same set. The
`{Module}.{Layer}` naming makes package identity predictable across ~20 module
repos.

## Conformant example

`Parties.slnx` at repo root:
`<Solution>\n  <Project Path="src/Parties.Domain/Parties.Domain.csproj" />\n  <Project Path="test/Parties.Domain.Tests/Parties.Domain.Tests.csproj" />\n</Solution>`
— each csproj:
`<Project Sdk="Microsoft.NET.Sdk">\n  <PropertyGroup>\n    <TargetFramework>net10.0</TargetFramework>\n    <ImplicitUsings>enable</ImplicitUsings>\n    <Nullable>enable</Nullable>\n  </PropertyGroup>\n</Project>`
with the test csproj adding an `<ItemGroup>` holding a `<ProjectReference>` to
`src/Parties.Domain/Parties.Domain.csproj` — the Include path written relative
to the test project, as `dotnet add reference` computes it.
