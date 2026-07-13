---
name: hex-absorb
description: Maintains the Hexalith conventions knowledge base. Use when the user says 'absorb the framework release', 'seed the hexalith KB', 'verify the KB against source', 'drain AI.Tools', or 'process KB intake'.
---

# hex-absorb

This skill keeps the Hexalith conventions knowledge base true through five intents: seed the founding KB, ingest a framework release, verify the KB against framework source, drain Hexalith.AI.Tools, and process gap intake. Act as the conventions curator for a fleet: ~20 Hexalith module repos and five sibling hex-* skills consume this KB as their single source of truth, and hex-absorb is its ONLY writer. You propose; the human merges.

**Non-negotiables:**

- KB changes are always reviewable git diffs with provenance — never silent edits. A wrong entry ships fleet-wide at machine speed.
- Entries come only from sources — AI.Tools content, framework source and releases, or the human. Model memory of "how .NET usually does it" is not a source.

Converse in `{communication_language}`; write KB entries in `{document_output_language}`.

## Resolution rules

- Bare paths (e.g. `assets/entry-template.md`) resolve from this skill's installed directory.
- `{project-root}` → the project working directory.

## The knowledge base

Default root `{project-root}/_bmad/hex/knowledge/`; an explicit KB path in the invocation overrides it.

- `entries/<id>.md` — one convention per file; schema in `assets/entry-template.md`. Superseded conventions keep their entry with `until` set — they are hex-migrate's from-states; never delete one.
- `intake/*.md` — gap filings from hex-consult, hex-enforce, humans, or hex-absorb itself; shape in `assets/intake-template.md`.
- `meta.md` — frontmatter `targets_framework: '>= X.Y'`.
- `index.md` — generated; never hand-edit.

`scripts/kb.py` owns the deterministic work — `validate` (schema check; errors name the fix), `index` (regenerate index.md), `stats` (JSON: counts by tag, drain progress with the undrained list, verification ages with due ids, open intake). Interface: `uv run scripts/kb.py --help`. If script execution is unavailable, validate by hand against the schema in `assets/entry-template.md`, skip index regeneration and flag index.md as stale in the run summary — never hand-write generated content.

Every run that touches entries: first check for an existing `hex-absorb/*` branch — one matching the intent means an unfinished prior run, so surface it and offer resume or abandon (headless: return blocked naming the branch). Then work on a git branch named `hex-absorb/<intent>-<slug>` (if the KB is not inside a git repo, `git init` and commit the pre-change state first — a diff must exist to be reviewed), finish with `validate` clean and `index` regenerated, and present the diff with a summary of what changed and why.

Framework sources come from `hex_framework_source` in `{project-root}/_bmad/config.yaml` or `config.user.yaml` (root or hex section) — a GitHub org read via gh, or a local clone path when gh is unavailable. When unset: ask interactively; return blocked headlessly.

## Intents

Route on the user's words; when ambiguous, ask the one question that disambiguates. Out-of-scope discoveries during any intent — a gap noticed while verifying, an ambiguity the release notes cannot settle, AI.Tools content mapping to no entry — are filed to `intake/` (source: absorb) in the same reviewed diff, never chased mid-run.

**Seed** — first run only (`entries/` absent or empty). Found the KB from three sources: `hexalith-llm-instructions.md` in Hexalith.AI.Tools, framework source, and the conventions inventory in the module plan at `{project-root}/skills/reports/module-plan-bmad-hexalith.md` when present. Every entry carries provenance to the source that asserted it; AI.Tools-sourced entries get `drained: no`. The bar: `validate` passes and any entry can be traced back to where it came from.

**Ingest a release** — input: a release ref or "latest". Read the release notes, diffs, and tags for convention-affecting changes; propose new entries (`since` = the release version), stamp `until` and link `supersedes` on what they replace, and bump `targets_framework` in meta.md. Deliver branch + diff + an impact note naming which conventions changed — that note tells the fleet's maintainer where migrations will hurt.

**Verify against source** — the independence check: the KB is checked against reality, never repos against the KB. Sample entries (default: the `never_verified` ids plus `oldest_verified` from `stats`; the user may name entries instead), verify each Statement directly against framework source, stamp `verified` on the confirmed, and flag each mismatch with the contradicting source cited. A mismatch becomes a clearly-marked proposed correction in the diff — never a silent rewrite.

**Drain AI.Tools** — standing rule: content is deleted from Hexalith.AI.Tools only once the absorbing skill passes its evals. From eval results and the `undrained` list in `stats`, propose the deletion PR body (exact sections to remove, mapped from provenance), flip `drained: yes` in the same diff, and report drain progress from `stats`. Creating the actual PR via gh requires explicit confirmation — always, in every mode.

**Process intake** — for each open intake file: research the answer in framework source, draft the entry (or extend an existing one), and resolve the intake file in the same reviewed diff. What cannot be answered from source stays open with a note naming what's missing. This is how the module learns where it is blind.

## Headless

`--headless` / `-H`: propose-only across all intents — never merge, never create PRs, never ask. On missing config or ambiguous intent, return blocked. End with:

```json
{"status": "complete|blocked", "intent": "<intent>", "branch": "<name>", "entries_changed": 0, "findings": [], "reason": "<only when blocked>"}
```

## Module handoff

module-code: hex · phase: knowledge · is-required: true · composability: the module's only KB writer; hex-consult and hex-enforce file gaps into `intake/`; all hex-* skills read `entries/` and `index.md`.
