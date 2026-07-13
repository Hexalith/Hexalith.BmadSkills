---
id: central-package-management
title: Package versions live only in Directory.Packages.props
tag: mechanical
since: 1.62.0
until: ''
supersedes: ''
provenance: ai-tools:hexalith-llm-instructions.md#central-package-management
verified: 2026-07-01
drained: no
---

# Package versions live only in Directory.Packages.props

## Statement

Every module repo carries a `Directory.Packages.props` at its root with
`ManagePackageVersionsCentrally` set to `true`, and every package version is
declared there as a `PackageVersion` item. A `PackageReference` inside a csproj
never carries a `Version` attribute. A freshly scaffolded module ships the props
file even before its first package reference exists.

## Why

Central package management is how a fleet-wide dependency bump stays a one-line
diff per repo; a version pinned inside a csproj hides from that sweep and drifts
silently.

## Conformant example

`<Project>\n  <PropertyGroup>\n    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>\n  </PropertyGroup>\n  <ItemGroup />\n</Project>`
at repo root as `Directory.Packages.props`.
