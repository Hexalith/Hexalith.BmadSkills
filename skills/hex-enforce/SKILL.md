---
name: hex-enforce
description: Gates Hexalith changes against conventions with cited findings. Use when the user says 'enforce hexalith conventions', 'review this diff for conformance', 'run the conformance gate', 'check analyzer coverage', or 'propose a waiver'.
---

# hex-enforce

This skill is the Hexalith conformance gate — two layers: a Roslyn analyzer (mechanical rules, compile-time, shipped via Hexalith.Builds) and this LLM review (judgment calls). Act as the gate for CI pipelines and bmad-loop first, PR authors second — headless is the primary surface here, not the afterthought. A verdict must be actionable without this conversation in the room, and the gate must stay cheap enough that it is still enabled three months from now: scope tightly, skip what the analyzer owns, and never pad a verdict.

**Non-negotiables:**

- An objection you cannot tie to a KB convention id and a code location is not a finding. When something looks wrong but the KB is silent or ambiguous, file a gap to the KB's `intake/` (format in `references/audit-core.md`) instead of rejecting.
- Never double-report with the analyzer: a mechanical rule the coverage manifest lists is the analyzer's — skip it. An uncovered mechanical rule is yours, and the verdict names the coverage gap.

Converse in `{communication_language}`; write findings and reports in `{document_output_language}`.

## Resolution rules

- Bare paths (e.g. `references/audit-core.md`) resolve from this skill's installed directory.
- `{project-root}` → the project working directory.

## Shared machinery

The audit procedure, the findings JSON schema, waiver semantics, and the staleness check live in `references/audit-core.md` — the one operational definition of "conformant", shared with hex-migrate and the fleet report. Load it before any review or gate run.

KB root defaults to `{project-root}/_bmad/hex/knowledge/`; an explicit path in the invocation overrides it. The KB is read-only here — hex-absorb is its only writer; your one write surface is `intake/`. No KB → blocked (hex-absorb's seed intent founds it).

`scripts/gate.py` owns the deterministic work — `rules` (KB entry enumeration + index drift), `waivers` (parse + validate + expiry), `coverage` (KB mechanical ids × analyzer manifest), `staleness` (KB target vs repo's pinned Hexalith version), `verdict` (schema-validate findings, reject unknown convention ids, apply waivers, move analyzer-covered ids to a surfaced bucket, settle pass/fail, exit code, `--format annotations` for GitHub). Interface: `uv run scripts/gate.py --help`. If script execution is unavailable — interactive only — do the same checks by hand against the schemas in `references/audit-core.md` and mark the verdict `unsettled by gate.py`, never skipping waiver or citation checks silently; headless returns blocked instead.

## Intents

Route on the user's words; when ambiguous, ask the one question that disambiguates (headless: infer or return blocked). A repo-wide audit is hex-migrate's job — this skill is diff-scoped; redirect rather than improvise a repo run.

**Review a diff / gate a PR** — the audit core run with scope `diff`, layer `judgment`. Interactive: the diff is the working tree against the default branch unless the user points elsewhere; walk the findings with the user, and offer a waiver draft for any finding they declare intentional. CI/headless: the diff is the PR; settle with `gate.py verdict` (exit code is the gate; `--format annotations` feeds PR annotations via the workflow log or `gh`). Every verdict carries the staleness check. For a judgment finding the human contests, hex-consult's explain-finding intent is the tiebreaker — cite its explanation rather than re-arguing from raw entries.

**Coverage map** — `gate.py coverage` against the repo's `analyzer-rules.json`, then report: which mechanical conventions the analyzer covers, which fall to this skill in the meantime, and which manifest mappings point at no KB entry (analyzer and KB have drifted). The uncovered list is the analyzer backlog — it feeds Hexalith.Builds work, so keep it citable by convention id.

**Propose a waiver** — draft a well-formed entry (convention id, reason worth reading in a PR, review date defaulting ~6 months out) as a diff against the target repo's `hex-waivers.yaml`, creating the file from `assets/hex-waivers-template.yaml` when absent. Validate with `gate.py waivers` before presenting. The human merges; never commit a waiver on your own — a waiver is a policy decision, not a fix.

## Headless

`--headless` / `-H`: never ask; the CI/loop surface. Findings settle only through `gate.py verdict`. Return blocked when the KB root is missing, the target diff/repo cannot be identified, the waivers file is malformed (a broken policy file must fail loudly, not waive silently), or script execution is unavailable (a gate that cannot settle deterministically must not emit a hand-computed verdict). `artifact` carries the intent's deliverable: the drafted waiver entry (inline content), the coverage partition from `gate.py coverage`, or null for gate. When the KB's `intake/` is not durably writable (ephemeral CI checkout, read-only KB), each `gaps_filed` entry carries the gap's full content inline instead of a path, so the caller can re-file it. End with:

```json
{"status": "complete|blocked", "intent": "gate|coverage|waiver", "verdict": "pass|fail|n/a", "counts": {"fail": 0, "warn": 0, "waived": 0, "analyzer_owned": 0}, "artifact": null, "gaps_filed": [], "reason": "<only when blocked>"}
```

## Module handoff

module-code: hex · phase: conformance · after: hex-consult · is-required: true · composability: diff-scoped consumer of the shared audit core (`references/audit-core.md`), which hex-migrate reruns repo-wide; hex-extend's verify step is the same diff-scoped call; files gaps to KB `intake/` (source: enforce); calls hex-consult headlessly for judgment-call explanations.
