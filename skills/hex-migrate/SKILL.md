---
name: hex-migrate
description: Migrates Hexalith repos to current framework conventions. Use when the user says 'migrate this module', 'audit this repo against conventions', 'create a gap report', 'drive the upgrade', or 'run a fleet audit'.
---

# hex-migrate

This skill keeps Hexalith module repos current with a framework that ships weekly: audit a repo against the conventions KB, deliver a tiered gap report, drive the approved upgrade, and aggregate audits across the fleet. Act as the migration engineer for two consumers — the maintainer who approves what gets applied, and bmad-loop driving the mechanical tier unattended. Both act on the gap report without this conversation in the room, so every gap cites a convention id and names its tier, and "migrated" is never claimed without a green build behind it.

**Non-negotiables:**

- Never leave a repo red. Every applied step ends on passing build and tests with its own commit, or is rolled back before anything else happens — a half-migrated broken repo is worse than a lagging one.
- The tier is honest about who decides: a judgment-tagged convention is never tiered mechanical and never auto-fixed. The machine does not settle what the KB marks as a human call.

Converse in `{communication_language}`; write reports, plans, and logs in `{document_output_language}`.

## Resolution rules

- Bare paths (e.g. `scripts/migrate.py`) resolve from this skill's installed directory.
- `{project-root}` → the project working directory.
- `{output_folder}` → the `output_folder` value from `{project-root}/_bmad/config.yaml` (default `{project-root}/_bmad-output`).

## Shared machinery

The audit engine is the shared audit core shipped with the sibling hex-enforce skill, installed beside this one: load its `references/audit-core.md` (procedure, findings schema, waivers, staleness) before any audit, and run its `scripts/gate.py` from that skill's directory. An explicit audit-core path in the invocation overrides the sibling lookup; neither resolvable → blocked. This skill always runs scope `repo`, layer `full`: a lagging repo's analyzer lags too, so no rule is presumed covered, and superseded KB entries act as from-states — code matching one is reported as "follows the convention as of its version, superseded by <id>", turning a bare violation into an upgrade path.

KB root defaults to `{project-root}/_bmad/hex/knowledge/`; an explicit path in the invocation overrides it. hex-absorb is its only writer; the one write surface here is `intake/` (source: migrate). No KB → blocked.

`scripts/migrate.py` owns the deterministic work — `tiers` (validate each finding's tier against the KB tags from `gate.py rules`; missing tiers on failing findings, unknown tiers, and tag-inconsistent tiers are rejected with the fix named), `report` (settled tiered verdict → gap report: HTML plus the machine-readable JSON beside it), `fleet` (directory of settled per-repo verdicts → fleet report: HTML + JSON with verdict, tier counts, and staleness lag per repo, drift hot-spots, waiver counts). Interface: `uv run scripts/migrate.py --help`. Reports land in `{output_folder}/hex/` unless the user points elsewhere — resolve that location and pass it as `--out` to the `report` and `fleet` subcommands. If script execution is unavailable — interactive only — do the same checks by hand against the schemas and mark every artifact `hand-rendered, unsettled`; headless returns blocked.

## Intents

Route on the user's words; when ambiguous, ask the one question that disambiguates (headless: infer or return blocked). A diff or PR gate is hex-enforce's job — redirect rather than answer a diff question with a repo audit.

**Audit** — run the audit core (repo scope, full layer), settle with `gate.py verdict`, then tier every failing finding: `mechanical` (safe, local, deterministic fix), `structural` (reshapes files or projects; applied only from an approved plan), `judgment` (the KB marks it a human call). Validate with `migrate.py tiers`, render with `migrate.py report`. The gap report is the contract everything downstream consumes: the human approves from it, drive executes from it, the fleet aggregates it.

**Drive** — input: a settled gap report; when absent, run Audit first — audit always precedes drive. Baseline before anything: build and test the untouched repo, because a green gate cannot tell migration breakage from pre-existing breakage — a red baseline stops drive (surface it; headless returns blocked). Work on a `hex-migrate/<slug>` branch (no git repo → `git init` and commit the baseline; a rollback point must exist); an existing `hex-migrate/*` branch is an unfinished prior run — surface it and offer resume from its migration log or abandon (headless: blocked naming the branch). Plan the step order from the report — group related findings, order by dependency and risk, note per-step risk — and get the human's per-tier approval (headless: mechanical tier only, no approval by design). Then execute: one step, one green gate (build + tests), one commit; a red gate reverts the step and records why. A judgment finding is decided by the human — cite hex-consult's "Explain a finding" intent (headless intent `explain`) for the tiebreak rather than re-arguing from raw KB entries. Deliver the branch plus a migration log beside the gap report: applied, reverted, escalated, each citing its findings.

**Fleet** — repos come from `hex_fleet_manifest` in `{project-root}/_bmad/config.yaml` or `config.user.yaml` (root or hex section; default `{project-root}/hex-fleet.yaml`); missing manifest: ask interactively, blocked headlessly. Audit each repo (local path, or clone via gh), write each settled tiered verdict into one directory, aggregate with `migrate.py fleet`. Name every manifest repo skipped and why — a fleet report that silently drops a repo aims the migration effort wrong.

## Headless

`--headless` / `-H`: never ask; the loop surface. Audit and fleet always run — they only report. Drive applies the mechanical tier only; every structural and judgment finding returns as an escalation carrying the finding, its tier, and what a human must decide. Return blocked when the KB or the audit core cannot be resolved, the target repo or fleet manifest cannot be identified, the waivers file is malformed, the baseline is red or an unfinished `hex-migrate/*` branch exists (drive), or script execution is unavailable. End with:

```json
{"status": "complete|blocked", "intent": "audit|drive|fleet", "verdict": "pass|fail|n/a", "report": "<gap or fleet report path, or null>", "counts": {"mechanical": 0, "structural": 0, "judgment": 0, "waived": 0}, "applied": 0, "reverted": 0, "escalations": [], "gaps_filed": [], "reason": "<only when blocked>"}
```

## Module handoff

module-code: hex · phase: conformance · after: hex-enforce · is-required: true · composability: repo-wide consumer of the shared audit core shipped with hex-enforce; the tiered gap-report JSON (audit-core findings schema + `tier` per finding) is the contract drive, the fleet aggregator, and bmad-loop consume; calls hex-consult headlessly to explain judgment findings; files gaps to KB `intake/` (source: migrate).
