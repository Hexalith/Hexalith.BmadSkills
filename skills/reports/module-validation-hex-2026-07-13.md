# Module Validation Report — `hex`

- **Module folder:** `{project-root}/skills/`
- **Date:** 2026-07-13 (supersedes the earlier same-day report, which predated hex-enforce)
- **Validator:** bmad-module-builder / Validate Module (VM)
- **Skills reviewed:** hex-absorb, hex-consult, hex-enforce
- **Result:** ❌ **Fail (structural)** — all three skills are registration-ready, but module packaging does not exist yet

## Structural issues (validation script)

| # | Severity | Finding |
|---|----------|---------|
| 1 | **Critical** | No setup skill (`hex-setup/`) exists, and no skill has standalone self-registration (`assets/module.yaml`, `assets/module-setup.md`, `assets/module-help.csv`, merge scripts). The module cannot be installed or registered — no help CSV, no config merge, no registration path. |
| 2 | **Warning** | Stray empty directory tree `skills/hex-enforce/skills/hex-enforce/evals/fixtures/...` — a scaffolding artifact (directories only, zero files), likely from a script resolving fixture paths against the wrong root. Delete it; a nested `skills/` tree inside a skill can confuse skill discovery during CM scaffolding. |

**Fix for #1:** Run **Create Module (CM)** on `skills/` to scaffold `hex-setup` with `module.yaml`, the help CSV, and merge scripts.
**Fix for #2:** `rm -r skills/hex-enforce/skills`.

## Quality findings (LLM review)

### hex-absorb — ✅ strong

- Frontmatter correct: `name` matches directory; description is verb-led with five trigger phrases mapping one-to-one to its five intents (seed, ingest release, verify against source, drain AI.Tools, process intake).
- Module handoff metadata present: `module-code: hex · phase: knowledge · is-required: true`.
- Headless contract defined. Referenced assets all exist (`assets/entry-template.md`, `assets/intake-template.md`, `scripts/kb.py`).
- **When packaged, register 5 CSV entries — one per intent.**

### hex-consult — ✅ strong

- Frontmatter correct: verb-led description with trigger phrases matching its four intents (answer a question, show a conformant example, explain a finding, file a gap).
- Module handoff metadata present: `module-code: hex · phase: knowledge · after: hex-absorb · is-required: false`. The `after: hex-absorb` ordering genuinely reflects the dependency (consult reads the KB that absorb writes).
- Headless contract defined.
- **When packaged, register 4 CSV entries — one per intent.**

### hex-enforce — ✅ strong (new since prior report)

- Frontmatter correct: `name` matches directory; verb-led description ("Gates Hexalith changes…") with five trigger phrases that route cleanly onto its three intents (review a diff / gate a PR, coverage map, propose a waiver).
- Module handoff metadata present and consistent with the roster: `module-code: hex · phase: conformance · after: hex-consult · is-required: true`. The `after: hex-consult` ordering is real — enforce calls hex-consult headlessly for judgment-call explanations.
- Headless contract defined, with a well-thought-out blocked policy (malformed waivers file fails loudly; no hand-computed verdicts when `gate.py` is unavailable).
- Referenced files all exist: `references/audit-core.md`, `scripts/gate.py` (+ tests), `assets/hex-waivers-template.yaml`, full eval fixture set (`kb-mini`, `repo-mini`).
- **When packaged, register 3 CSV entries — one per intent (gate, coverage, waiver).**

### Minor findings

| Severity | Skill | Finding | Suggestion |
|----------|-------|---------|------------|
| Minor | hex-absorb | Seed intent references `{project-root}/skills/reports/module-plan-bmad-hexalith.md`, a path that exists only in this builder repo — not in a target project after installation. Guarded with "when present", so nothing breaks. | Reword to make clear the module plan is a builder-repo-only seed source. |
| Minor | hex-absorb, hex-enforce | Working artifacts live inside the skill folders: `.memlog.md` (both), `.analysis/` (hex-enforce), `scripts/__pycache__/` (hex-absorb). Harmless locally, but they must not ship in the installable module. | Exclude dot-prefixed files/dirs and `__pycache__` during CM packaging, or clean before scaffolding. |
| Minor | (module) | `skills/reports/` (a non-skill folder) lives inside the module skills folder because `bmad_builder_reports` points there. | When running CM, ensure the scaffolder does not treat `reports/` as a skill candidate. |
| Minor | hex-enforce | SKILL.md references sibling skills `hex-migrate` and `hex-extend` that are not built yet (shared audit core, repo-wide rerun). Consistent with the module plan, so not an error — but the composability claims are unverifiable until those skills exist. | No action now; re-validate the cross-references when hex-migrate/hex-extend land. |

## Completeness vs. plan

The module plan envisions ~6 skills: hex-absorb, hex-consult, hex-enforce, hex-migrate, hex-extend, hex-create (plus hex-fleet mentioned). **Built: 3 of ~6.** Not a validation defect, but relevant to sequencing: package now and re-run CM as skills land, or finish the roster first and package once.

## Checklist

- [ ] Delete the stray nested tree: `rm -r skills/hex-enforce/skills`
- [ ] Run Create Module (CM) on `skills/` to scaffold `hex-setup` (module.yaml, help CSV, merge scripts)
- [ ] Verify CM generates 5 CSV rows for hex-absorb, 4 for hex-consult, 3 for hex-enforce
- [ ] Ensure `reports/` is excluded from skill discovery during scaffolding
- [ ] Ensure working artifacts (`.memlog.md`, `.analysis/`, `__pycache__`) are excluded from packaging
- [ ] (Optional) Reword hex-absorb Seed intent's module-plan reference for portability
- [ ] Re-run Validate Module (VM) after CM to confirm a clean pass
