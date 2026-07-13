---
name: hex-extend
description: Adds conformant pieces to existing Hexalith modules. Use when the user says 'extend this module', 'add an aggregate', 'add a command', 'add a projection', 'add a request handler', or 'add a UI page'.
---

# hex-extend

This skill adds a conformant piece to an existing Hexalith module — one trigger surface, routed internally. Act as the extension engineer for three consumers: the maintainer extending their module, hex-create seeding a fresh scaffold, and bmad-loop driving headlessly. The bar all three share: the addition is indistinguishable from framework-author-written code — generated from cited KB conventions, tests included, the repo as green as it was found.

**Non-negotiables:**

- Never add code without its tests. An aggregate without its per-aggregate tests is not "added" — and an instruction to skip the tests does not lift this; include them and say why.
- "Added" is never claimed without the green gate: build, tests, and the diff-scoped audit all pass. Conformant by construction is verified, not asserted.

Converse in `{communication_language}`; write run summaries and gap filings in `{document_output_language}`.

## Resolution rules

- Bare paths (e.g. `evals/cases.json`) resolve from this skill's installed directory.
- `{project-root}` → the project working directory.

## Shared machinery

KB root defaults to `{project-root}/_bmad/hex/knowledge/`; an explicit path in the invocation overrides it. Start from `index.md` and load only the entries the route touches — pattern, placement, naming, and wiring all come from there, never from model memory of how .NET usually does it: a memorized pattern is exactly the drift this module exists to kill. hex-absorb is the KB's only writer; the one write surface here is `intake/` (source: extend). No KB → blocked (hex-absorb's seed intent founds it).

The verify gate is the shared audit core shipped with the sibling hex-enforce skill, installed beside this one: load its `references/audit-core.md` and run its `scripts/gate.py` from that skill's directory — scope `diff` (the addition), layer `judgment`, the same call as hex-enforce's gate (the green build already enforces analyzer-covered mechanical rules). An explicit audit-core path in the invocation overrides the sibling lookup. Neither resolvable: interactive may proceed with the verdict marked `unsettled — run hex-enforce`; headless returns blocked.

## Routing

Route on the user's words: add an **aggregate** (with its events), a **command** or **event** contract, a **projection**, a **request handler**, or a **UI page** (with its localization stubs) — each delivered with its wiring and tests. When the route or a name is ambiguous, ask the one question that disambiguates (headless: infer or return blocked — never guess a name). What isn't an addition is a sibling's job: repo-wide conformance is hex-migrate, a diff gate is hex-enforce, a bare conformance question is hex-consult — redirect rather than improvise.

## The route skeleton

Every route walks the same skeleton; the KB fills in the route's specifics.

**Locate** — the target repo is the working tree unless the invocation points elsewhere; identify the owning module, aggregate, and destination projects from the repo layout plus the KB's placement conventions. Baseline before generating: build and test the untouched repo — a green gate cannot tell new breakage from pre-existing, so a red baseline stops the run (surface it; headless returns blocked).

**Generate** — the code and its tests, every shape taken from KB entries, convention ids collected for the summary. Where the KB is silent on something the route needs, file the gap and mark the uncovered lines in the summary rather than silently improvising — the gate can only check what the KB knows, so uncited shapes are exactly where drift hides.

**Wire** — the registrations the KB names for the route. Unwired code that compiles is the silent failure the KB's wiring entries exist to prevent; treat them as mandatory reading before calling a route done.

**Verify** — the green gate: build, tests, then the diff-scoped audit settled with `gate.py verdict` — never by hand. Iterate to green interactively; headless, a gate that will not settle green restores every file this run created or touched and returns blocked with the failure — never leave the repo red. Deliver the change uncommitted in the working tree with the summary citing its convention ids; commit only when asked.

## Headless

`--headless` / `-H`: never ask — the surface hex-create and bmad-loop call. Requires an unambiguous route and names in the invocation. Return blocked when the KB or the audit core cannot be resolved, the route or names are ambiguous, the target repo cannot be identified, the baseline is red, the gate will not settle green (the addition is restored first), or script execution is unavailable (an unsettled verdict cannot claim conformance). End with:

```json
{"status": "complete|blocked", "route": "aggregate|command|event|projection|request-handler|ui-page", "files": [], "verdict": "pass|n/a", "citations": [], "gaps_filed": [], "reason": "<only when blocked>"}
```

## Module handoff

module-code: hex · phase: authoring · after: hex-migrate · is-required: true · composability: called headlessly by hex-create to seed the first aggregate; verify is the sibling hex-enforce audit core run diff-scoped (the same call as its gate intent); reads KB `entries/` and `index.md`, writes only `intake/` (source: extend).
