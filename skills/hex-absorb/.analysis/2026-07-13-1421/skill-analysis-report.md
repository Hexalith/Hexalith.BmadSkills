# Analysis Report: skills/hex-absorb

Generated: 2026-07-13 · Schema: 2

**Grade: Good**

> Ship-ready: clean architecture, leanness, and customization; the three medium findings share one root cause — the skill under-wires machinery it already owns (kb.py partitions, intake/, branch state).

hex-absorb's intelligence placement is its primary strength: kb.py owns all deterministic KB work (validation, index, stats) while the prompt keeps only judgment, and the whole workflow fits in 1,285 destination-shaped tokens with headless propose-only behavior coherent with its non-negotiables. The primary opportunity is closing three read-side gaps in machinery the skill already ships: stats computes but discards the operand id lists Verify and Drain need, the intake/ folder accepts filings from everyone except the skill itself, and in-flight hex-absorb/* branches are never detected on activation.

| Severity | Count |
| --- | --- |
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low | 2 |

## Themes

### 1. Wire the read side of machinery the skill already owns

- Root cause: The write side of three mechanisms exists (kb.py computes verification/drain partitions, intake/ accepts gap filings, every run works on a hex-absorb/* branch) but nothing reads them back: stats discards entry ids so the model re-derives operand lists by scanning files, the skill's own mid-run discoveries have no route into intake/, and activation never checks for an in-flight branch from an interrupted or unmerged prior run.
- Fix: Extend kb.py stats (or add a 'due' subcommand) to emit operand id lists (never_verified, oldest_verified, undrained with provenance) plus a unit test; add one Intents-preamble line routing hex-absorb's own out-of-scope discoveries into intake/ with a new 'absorb' source (template legend + kb.py enum); add one clause to the branch paragraph checking for existing hex-absorb/* branches before creating one — surface and offer resume/abandon, headless returns blocked with the branch named.
- Findings:
  - `determinism-1` Verify and Drain operand selection is deterministic set-selection left to the prompt — `SKILL.md:Intents (Verify against source, Drain AI.Tools); scripts/kb.py:cmd_stats`
  - `enhancement-1` Add: capture-don't-interrupt — route the skill's own mid-run discoveries into intake/ — `SKILL.md:Intents; assets/intake-template.md; scripts/kb.py (intake source enum)`
  - `enhancement-2` Add: working-state resume leg — detect in-flight hex-absorb/* branches on activation — `SKILL.md:'Every run that touches entries' paragraph`

### 2. Scope the degraded path

- Root cause: The no-script fallback sanctions by-hand schema checks but sits beside an unconditional 'index regenerated' run contract, implicitly demanding hand-regeneration of generated content — exactly the deterministic work the script exists to make exact.
- Fix: One sentence: when script execution is unavailable, validate by hand but skip index regeneration, flag index.md as stale in the run summary (headless: note it in the JSON), and never hand-write generated content.
- Findings:
  - `determinism-2` No-script fallback implicitly demands hand-regeneration of the generated index — `SKILL.md:The knowledge base`

## Strengths

- Intelligence placement: kb.py owns fetch/parse/validate/count/transform with named-fix errors and 7 unit tests; the prompt keeps only judgment (release impact, source verification, entry drafting)
- 1,285 tokens of destination-shaped prose — stance, outcome, consumer, bar, and non-negotiables with their whys; no numbered marches, no ceremony
- Headless coherence: propose-only composes exactly with 'you propose; the human merges' and the PR-confirmation rule — no contradiction between modes
- Eval suite with discriminating rubrics: a deliberately-wrong fixture entry for verify, negative assertions (no invented entries), and process-discipline checks (branch, validate-clean, JSON return)
- Customization correctly declined and logged; module handoff fields carried per convention without authoring module.yaml

## Recommendations

1. Extend kb.py stats to emit operand id lists (never_verified, oldest_verified, undrained+provenance) and cover with a unit test; point Verify/Drain at the JSON instead of file-scanning (resolves: determinism-1)
2. Add the capture-don't-interrupt line to the Intents preamble and the 'absorb' intake source to the template legend and kb.py enum (resolves: enhancement-1)
3. Add the in-flight-branch check clause to the branch-per-run paragraph (resume or abandon; headless blocks with the branch named) (resolves: enhancement-2)
4. Scope the no-script fallback: skip index regeneration, flag stale, never hand-write generated content (resolves: determinism-2)
5. Cut the unused '{skill-root}' token from Resolution rules (resolves: leanness-1)

## Experience

- **Ingest a release** — release ref → convention-affecting changes → branch hex-absorb/ingest-<slug> → new/superseded entries + meta bump → validate clean + index → diff + impact note for the maintainer
- **Verify against source** — sample selection → each Statement checked against framework source → verified stamps + cited mismatches as marked proposals → diff + findings
- **Drain AI.Tools** — eval results + drained:no entries → deletion PR body mapped from provenance → drained:yes flips in same diff → PR creation only on explicit confirmation
- Headless: Propose-only across all intents with a JSON status block; never merges, never creates PRs, blocks on missing config — proven by three headless eval cases.

## Findings

### Medium (3)

#### determinism-1 — Verify and Drain operand selection is deterministic set-selection left to the prompt

- Lens: determinism
- Location: `SKILL.md:Intents (Verify against source, Drain AI.Tools); scripts/kb.py:cmd_stats`
- Evidence: cmd_stats already computes the verification buckets (never/stale/fresh) and the drained/undrained split but emits only counts, so every run the model re-derives the operand lists by scanning index.md/entries and comparing ISO dates to find the oldest-verified entry.
- Recommendation: Extend cmd_stats (or add a 'due' subcommand) to emit operand ids — never_verified: [ids], oldest_verified: id, undrained: [{id, provenance}]. The prompt keeps only the judgment: verifying Statements against source and mapping provenance to AI.Tools sections.

#### enhancement-1 — Add: capture-don't-interrupt — route the skill's own mid-run discoveries into intake/

- Lens: enhancement
- Location: `SKILL.md:Intents; assets/intake-template.md; scripts/kb.py (intake source enum)`
- Evidence: The skill owns the perfect capture mechanism — intake/ — but only lists hex-consult, hex-enforce, and humans as filers. Gaps noticed during verify, ambiguous changes during ingest, and unmapped AI.Tools content during drain die in the transcript or derail the current intent.
- Recommendation: One line in the Intents preamble: out-of-scope discoveries during any intent are filed as intake/*.md in the same reviewed diff, never acted on mid-run. Extend the intake source enum with 'absorb' (template legend + kb.py validate).

#### enhancement-2 — Add: working-state resume leg — detect in-flight hex-absorb/* branches on activation

- Lens: enhancement
- Location: `SKILL.md:'Every run that touches entries' paragraph`
- Evidence: KB-on-a-branch is a structured working artifact, but nothing on activation checks for an existing hex-absorb/* branch: after an interrupted run or an unmerged prior proposal, a re-invocation collides with or silently duplicates the branch, and partial proposals are never surfaced.
- Recommendation: Before creating the branch, check for existing hex-absorb/* branches; if one matches the intent, surface it and offer resume or abandon (headless: return blocked with the branch named in reason).

### Low (2)

#### determinism-2 — No-script fallback implicitly demands hand-regeneration of the generated index

- Lens: determinism
- Location: `SKILL.md:The knowledge base`
- Evidence: The fallback sanctions by-hand validation only, but the unconditional run contract says 'finish with validate clean and index regenerated' while index.md is 'generated; never hand-edit' — in a no-script environment the model must either hand-produce index.md or violate the contract, with no instruction picking which.
- Recommendation: Scope the fallback explicitly: when script execution is unavailable, skip index regeneration, flag index.md as stale in the run summary (or return blocked headlessly), and never hand-write generated content.

#### leanness-1 — Unused {skill-root} token defined in Resolution rules

- Lens: leanness
- Location: `SKILL.md:Resolution rules`
- Evidence: {skill-root} appears exactly once — in its own definition — and is never used; every skill-internal reference is a bare path.
- Recommendation: Cut 'and `{skill-root}`' so the bullet reads: 'Bare paths (e.g. `assets/entry-template.md`) resolve from this skill's installed directory.'
