# Hexalith module structure (excerpt)

Per-layer NuGet packages of a domain module:

- Domain: `<Module>.Aggregates`, `<Module>.Abstractions`, `<Module>.Events`
- Application: `<Module>.Commands`, `<Module>.Requests`, `<Module>.Application`, `<Module>.Projections`
  - `<Module>.Requests` holds the request (query) contracts AND their request
    handlers; a request handler answers a read request from projections, never
    from the event stream directly.
- Infrastructure: `<Module>.ApiServer`, `<Module>.WebServer`, `<Module>.WebApp`
- Presentation: `<Module>.UI.Components`, `<Module>.UI.Pages`, `<Module>.Localizations`
