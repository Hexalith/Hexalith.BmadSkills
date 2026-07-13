# Hexalith core v1.73.0 — release notes

## Breaking changes

- **Projection registration**: manual `IProjectionFactory` wiring is replaced by
  the `AddProjectionHandler<THandler>()` extension on `IServiceCollection`. The
  old wiring keeps compiling in 1.73 but is marked `[Obsolete]` and will be
  removed in 1.75.

  Before (<= 1.72):

      services.AddSingleton<IProjectionFactory<PartySummary>, PartySummaryProjectionFactory>();

  After (>= 1.73):

      services.AddProjectionHandler<PartySummaryProjectionHandler>();

## Other changes

- Bug fixes in EventStore snapshot compaction (no convention impact).
- Dependency bumps: Dapr 1.18.2, Aspire 13.1.
