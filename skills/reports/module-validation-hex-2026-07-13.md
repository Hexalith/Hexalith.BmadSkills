# Module Validation Report — BMAD Hexalith Module (`hex`)

- **Module folder:** `{project-root}/skills/`
- **Date:** 2026-07-13 (supersedes the earlier same-day report, which predated hex-setup and the full seven-skill module)
- **Validator:** bmad-module-builder / Validate Module (VM)
- **Skills reviewed:** hex-setup, hex-absorb, hex-consult, hex-enforce, hex-migrate, hex-extend, hex-create
- **Result:** ✅ **Pass** — ready for use; findings below are hardening and polish

## Structural validation (script) — PASS

Zero findings. Setup skill `hex-setup` detected, `module.yaml` complete, 24 CSV entries with no missing skills, no orphans, no duplicate menu codes, no broken `preceded-by`/`followed-by` references, all required fields present. `module.yaml` has no `agents:` block, so agent-roster checks do not apply.

## Registration completeness & accuracy — PASS

All 24 CSV rows cross-checked against each skill's actual capabilities:

| Skill | CSV rows | Capabilities found | Verdict |
|---|---|---|---|
| hex-setup | 1 (SH) | 1 invokable action | complete |
| hex-absorb | 5 (SK, IR, VK, DA, PI) | 5 intents | complete |
| hex-consult | 4 (CQ, SE, EF, FG) | 4 intents | complete |
| hex-enforce | 3 (GD, CV, PW) | 3 intents | complete |
| hex-migrate | 3 (AU, DU, FA) | 3 intents | complete |
| hex-extend | 6 (XA–XU) | 6 routes | complete |
| hex-create | 2 (NP, NM) | 2 invokable phases | complete |

Every distinct capability has its own row; hex-create's internal seed/verify phases are correctly *not* registered as separate entries (they run inside `scaffold`). Action names and args match the skills' documented inputs. Relationships are sound: `hex-absorb:seed` is the only `required: true` entry and everything KB-dependent is preceded by it; the plan→scaffold, audit→drive, gate→waiver, and gap→intake chains are correct. Menu codes are mnemonic and collision-free.

## Quality findings

### High — could break installation

1. **hex-setup runs its merge scripts with `python3`, but `merge-config.py` requires pyyaml** (declared via PEP 723). On a machine without system-wide pyyaml the install fails at the config-write step. Every other hex skill's scripts are invoked with `uv run`, which resolves PEP 723 deps. **Fix:** invoke via `uv run scripts/merge-config.py` / `uv run scripts/merge-help-csv.py` / `uv run scripts/cleanup-legacy.py`.

### Medium — misleading or latent defects

2. **hex-setup: leftover "bmb" copy-paste artifacts.** Confirm-section example says "Cleaned up 106 installer package files from **bmb/**, core/, _config/" (should be `hex/`); `cleanup-legacy.py`'s `--module-code` help text says `(e.g. 'bmb')`. **Fix:** replace both with `hex`.
3. **hex-setup: `merge-help-csv.py` fallback HEADER constant uses `after`/`before`** while the shipped CSV uses `preceded-by`/`followed-by`. Latent (a header always exists today), but writes a wrong header if ever exercised. **Fix:** align the constant.
4. **hex-setup: the TOML config branch is entirely manual.** The legacy YAML path is scripted and validated; the ≥6.10 TOML path (write `config.toml`, hand-merge rows into `_bmad/_config/bmad-help.csv`) has no script support — a larger error surface, and this project itself is on the TOML layout. **Fix:** add script support or a validation checklist for the TOML path.
5. **hex-extend: eval coverage is 1 of 6 routes.** Only the `command` route has eval cases; the kb-mini fixture has no projection, request-handler, or ui-page entries, so those routes' KB-driven shapes (including "UI page with localization stubs") are untested. **Fix:** add at least one eval per remaining route, or one representative structural route plus ui-page.
6. **hex-absorb: drain accounting can silently lose entries.** `entry-template.md` defaults `drained: na`, and `kb.py validate` does not enforce that AI.Tools-provenance entries have `drained: yes|no` — an AI.Tools entry left at `na` drops out of drain progress stats. **Fix:** add that cross-check to `kb.py validate`.
7. **Cross-skill contract drift risks.** hex-migrate cites "hex-consult's explain-finding intent" (hex-consult titles it "Explain a finding", headless code `explain`); hex-enforce's headless enum maps review-diff→`gate` only implicitly; the `tier` field hex-migrate adds to findings is not validated by the shared `gate.py validate_findings`. **Fix:** state the mappings explicitly and/or validate `tier` in the shared script.
8. **hex-migrate: report output location described two ways** — `{output_folder}/hex/` in prose vs the `--out` flag, and `{output_folder}` is never defined in its Resolution rules. **Fix:** one sentence connecting the two.

### Low — polish

9. **Flag notation:** SKILL.md bodies say `--headless`, all CSV args columns say `-H`. Consider `{-H/--headless: headless mode}` in the CSV.
10. **CSV description nitpicks:** `SK` opens with "Found the conventions KB…" — "Found" (to found) reads as past tense of "find"; "Seed…" is unambiguous and matches the display name. `NP`'s "Interview (or args) to a validated…scaffold plan" is not verb-first.
11. **Packaging hygiene:** stray dev artifacts (`.memlog.md`, `.analysis/`) in several skill directories (absorb, consult, create, extend) will ship with the module — clean or exclude before packaging.
12. **hex-create:** the `.slnx`-only constraint of `scaffold.py verify` lives only in the script docstring, not the SKILL.md narrative.

## Positives

All file references across all seven skills resolve (zero broken references). Headless JSON contracts are precisely specified everywhere. The shared-machinery design (gate.py / audit-core.md / kb.py reused across skills) is coherent. Frontmatter trigger phrases map one-to-one onto documented intents in every skill.

## Overall assessment

**The module is ready for use.** Structure, registration, and descriptions are in good shape — the CSV needed zero corrections for completeness or accuracy. Fix finding #1 before distributing (install can fail on a clean machine); #2–#4 are quick follow-ons in the same skill. Everything else is hardening and polish.

## Fixes applied (same day, post-validation)

- **#1 fixed** — hex-setup SKILL.md now invokes all three setup scripts (and their `--help` references) via `uv run`; the uv row in the tool-check table now covers the setup scripts too.
- **#2 fixed** — Confirm-section example now says `hex/`; `cleanup-legacy.py` help text example now says `'hex'`.
- **#3 fixed** — `merge-help-csv.py` HEADER constant now uses `preceded-by`/`followed-by`.
- **#6 fixed** — `kb.py validate` now rejects `drained: na` on entries with `ai-tools:` provenance; unit test added (`test-kb.py`, 11/11 pass).
- **#7 fixed (prose)** — hex-migrate and hex-enforce now cite hex-consult's "Explain a finding" intent by its real name with the headless code `explain`; hex-enforce's Headless section states the intent→code mapping (`gate`/`coverage`/`waiver`) explicitly. The `tier` field remains validated by `migrate.py tiers` rather than the shared `gate.py` (by design — noted, not changed).
- **#8 fixed** — hex-migrate defines `{output_folder}` in Resolution rules and states that the resolved location is passed as `--out` to `report`/`fleet`.
- **#9 fixed** — all CSV args entries now read `{-H/--headless: headless mode}`.
- **#10 fixed** — `SK` description now opens with "Seed…"; `NP` description is verb-first ("Build a validated machine-readable scaffold plan…").
- **#12 fixed** — hex-create SKILL.md states the `.slnx`-only constraint of `scaffold.py verify`.
- **Not applied:** #4 (TOML-branch script support — design work), #5 (hex-extend eval coverage for 5 more routes — new eval cases and KB fixtures), #11 (deleting stray `.memlog.md`/`.analysis/` dev artifacts — packaging call for the maintainer).

Structural validation re-run after fixes: **pass, 0 findings**. `python3 -m py_compile` clean on all touched scripts.
