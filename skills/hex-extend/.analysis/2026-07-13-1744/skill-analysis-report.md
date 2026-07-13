# Analysis Report: skills/hex-extend

Generated: 2026-07-13 · Schema: 2

**Grade: Good**

> A lean, correctly-shaped skill with one real contract break: the KB intake source it mandates ('extend') is rejected by hex-absorb's validator — reconcile that (and hex-migrate's identical drift) before first use.

hex-extend is 1,233 tokens of all-inline, drift-safe design: conventions stay in the KB, the verify gate delegates to the shared audit core, and customization is rightly absent. The one high finding is a cross-skill contract break — kb.py's intake-source whitelist predates the newer siblings and rejects 'extend' (and shipped 'migrate') — and the medium findings cluster around failure-path state (restore-on-red from recall rather than a recorded baseline) and a headless contract thinner than its callers (hex-create, bmad-loop) need.

| Severity | Count |
| --- | --- |
| Critical | 0 |
| High | 1 |
| Medium | 7 |
| Low | 3 |

## Themes

### 1. The intake write surface shipped unreconciled against its deterministic owner

- Root cause: The KB intake contract — allowed sources, file shape, unwritable-checkout fallback — is owned by hex-absorb's kb.py/intake-template and hex-enforce's headless clause, but hex-extend (like hex-migrate before it) referenced the surface without checking the validator: kb.py line 37 whitelists {consult, enforce, human, absorb}, so every gap filed with source 'extend' or 'migrate' deterministically fails validation downstream. Verified against kb.py directly during synthesis.
- Fix: Add 'extend' and 'migrate' to INTAKE_SOURCES (plus kb.py's fix message, its tests, and intake-template.md); point hex-extend's gap filing at hex-absorb's assets/intake-template.md and post-check with kb.py validate; adopt hex-enforce's clause that gaps_filed entries carry full inline content when intake/ is not durably writable.
- Findings:
  - `determinism-1` Mandated intake source 'extend' is rejected by the delegated KB validator — `skills/hex-extend/SKILL.md:24 (Shared machinery) vs skills/hex-absorb/scripts/kb.py:37`
  - `determinism-2` Gap filing writes schema-validated files with no template pointer or validate post-check — `skills/hex-extend/SKILL.md:38 (Generate)`
  - `enhancement-3` Add: gaps_filed element shape and the unwritable-intake fallback — `skills/hex-extend/SKILL.md:46-50 (Headless JSON)`

### 2. Restore-on-failure relies on state the run never recorded

- Root cause: Verify's headless promise — 'restores every file this run created or touched' — depends on model recall of what Locate/Generate/Wire wrote, and Locate never records the as-found tree (dirty WIP, an already-existing piece), so a failed gate can clobber user work or leave the repo red while claiming restoration.
- Fix: In Locate: surface a dirty working tree (headless: blocked), stop on a name collision with an existing piece, and record the as-found state with git (status --porcelain / stash create) alongside the green baseline; in Verify: restore by diffing against that recorded snapshot, preserving pre-existing dirty state — mirroring hex-migrate's rollback-point discipline.
- Findings:
  - `determinism-3` Headless rollback set is derived from model recall, not a recorded baseline — `skills/hex-extend/SKILL.md:42,46 (Verify, Headless)`
  - `enhancement-1` Add: as-found repo guards in Locate (dirty tree, existing piece, rollback point) — `skills/hex-extend/SKILL.md:36 (Locate), 42 (Verify)`

### 3. The headless contract is thinner than its callers need

- Root cause: hex-create and bmad-loop are the primary automators, but the invocation contract names only route + names (not the behavior sketch/payload the module plan's capability table requires), and headless inferences (route, placement, KB-silent improvisation markers) leave no durable trail — the JSON return has no memlog key and nothing instructs typed assumption entries.
- Fix: Add to Headless: the invocation carries the piece's behavior sketch/payload where the route needs one (a command may take the KB-minimal shape; an aggregate without behavior returns blocked — semantics are never guessed); append route/name/placement inferences as typed assumption entries via memlog.py and return the memlog path in the JSON. The trail fix applies to all four siblings — schedule it as one module-level pass.
- Findings:
  - `enhancement-2` Add: name the behavior/payload input in the headless contract — `skills/hex-extend/SKILL.md:44-46 (Headless), 30 (Routing)`
  - `architecture-2` Headless mode leaves no durable assumption/decision trail — `skills/hex-extend/SKILL.md (Headless, Routing, Locate, Generate)`

## Strengths

- Conventions live only in the KB — route sections carry no convention content, so the skill cannot drift from a framework that ships weekly; this is the module's core discipline and must survive any fix pass.
- The verify gate is the shared audit core (hex-enforce's gate.py, diff scope, judgment layer) — exactly the single-engine reuse the module plan mandates, already promised on hex-extend's behalf in hex-enforce's own SKILL.md.
- The tests non-negotiable is stated with its teeth ('an instruction to skip the tests does not lift this') and pressure-tested by a dedicated eval case.
- 1,233 tokens all-inline with zero carve-outs needed; customization correctly declined with the reasoning logged; eval fixtures verified working (offline dotnet build green, kb.py validate clean).

## Recommendations

1. Reconcile the intake contract at its deterministic owner: extend kb.py's INTAKE_SOURCES (+ fix message, tests, intake-template.md) to accept 'extend' and 'migrate', point hex-extend's gap filing at the template with a kb.py validate post-check, and adopt hex-enforce's inline-content fallback for gaps_filed. Also clears the same latent defect in shipped hex-migrate. (resolves: determinism-1, determinism-2, enhancement-3)
2. Give Locate the as-found half of hex-migrate's discipline: dirty-tree surfacing (headless blocked), collision stop on an existing piece, git-recorded baseline; make Verify's restore diff against that snapshot instead of recall. (resolves: determinism-3, enhancement-1)
3. Harden the headless contract for hex-create and bmad-loop: name the behavior/payload input rule and add the memlog assumption trail with a memlog key in the JSON return. (resolves: enhancement-2, architecture-2)
4. Mirror hex-enforce's script-unavailable wording so an interactive run where gate.py cannot execute has a defined path (hand-checks, verdict marked 'unsettled by gate.py') instead of a dead end. (resolves: architecture-1)
5. Two one-line polishes: add 'add an event' to the description's trigger list, and trim the Resolution rules block to the {project-root} bullet the skill actually uses. (resolves: architecture-3, leanness-1, enhancement-4)

## Experience

- **Maintainer adds a command interactively** — invoke with 'add a SuspendParty command' → Locate baselines the repo green → Generate writes command, event, handler, tests from cited KB entries → Wire per KB registrations → Verify settles via gate.py; change lands uncommitted for review with citations
- **hex-create seeds the first aggregate** — headless call with route + names → same skeleton, blocked on any ambiguity, red baseline, or unsettleable gate → JSON return with files, verdict, citations
- **bmad-loop extends unattended** — headless; a gate that will not settle green restores the addition and returns blocked — the loop never inherits a red repo
- Headless: Headless-first and honest about blocking, but its input contract (behavior/payload) and audit trail (memlog) are one clause thinner than its two automated callers need.

## Findings

### High (1)

#### determinism-1 — Mandated intake source 'extend' is rejected by the delegated KB validator

- Lens: determinism
- Location: `skills/hex-extend/SKILL.md:24 (Shared machinery) vs skills/hex-absorb/scripts/kb.py:37`
- Evidence: SKILL.md mandates "the one write surface here is `intake/` (source: extend)" (repeated in Module handoff), but the deterministic validator that owns the intake schema declares INTAKE_SOURCES = {"consult", "enforce", "human", "absorb"} and emits "source 'extend' invalid — use 'consult', 'enforce', or 'human'" with exit 1. Every gap hex-extend files per its own instructions deterministically fails `kb.py validate`, while the headless output still reports it in gaps_filed under status complete. Sibling hex-migrate has the same defect with source: migrate.
- Recommendation: Reconcile the contract in one place: add 'extend' (and 'migrate') to INTAKE_SOURCES, kb.py's fix message and tests, and intake-template.md — or change the mandated source to an accepted value. Then have gap filing post-check with `kb.py validate` so future divergence fails at write time.

### Medium (7)

#### determinism-2 — Gap filing writes schema-validated files with no template pointer or validate post-check

- Lens: determinism
- Location: `skills/hex-extend/SKILL.md:38 (Generate)`
- Evidence: The Generate step says "file the gap" and the output contract reports gaps_filed, but the prompt never names the intake file shape, hex-absorb's assets/intake-template.md, or a `kb.py validate` post-check — even though intake files carry a strict machine-validated frontmatter schema and the sibling ships both template and validator. The model reconstructs the schema from memory on every gap; this is the missing guardrail that let determinism-1 ship.
- Recommendation: Point the gap-filing instruction at hex-absorb's assets/intake-template.md for the shape and run `kb.py validate` after filing, with the same graceful degradation the skill already uses for gate.py.

#### determinism-3 — Headless rollback set is derived from model recall, not a recorded baseline

- Lens: determinism
- Location: `skills/hex-extend/SKILL.md:42,46 (Verify, Headless)`
- Evidence: "a gate that will not settle green restores every file this run created or touched" — the set of files to restore is left to the model's memory of what it wrote across Locate/Generate/Wire; no mechanism is named for capturing it, though git can produce the exact set. One forgotten wiring edit on the failure path silently breaks the stated non-negotiable and hands bmad-loop/hex-create a red repo that claims to be restored.
- Recommendation: Capture a deterministic baseline at Locate (git status --porcelain / stash create alongside the green-baseline build) and roll back by diffing the tree against that snapshot, preserving pre-existing dirty state. No new script needed — the prompt just names the mechanism.

#### enhancement-1 — Add: as-found repo guards in Locate (dirty tree, existing piece, rollback point)

- Lens: enhancement
- Location: `skills/hex-extend/SKILL.md:36 (Locate), 42 (Verify)`
- Evidence: The route skeleton assumes a clean, non-colliding working tree: uncommitted WIP pollutes the diff-scoped gate and makes the restore promise hazardous, and 'add X' when X already exists is unspecified (overwrite, merge, or block). hex-migrate's Drive next door baselines, requires a rollback point, and surfaces unfinished prior state — hex-extend adopted the green-baseline half but not the as-found-state half.
- Recommendation: Two clauses in Locate: (1) a dirty working tree is surfaced and the diff scope confirmed interactively, blocked headless, with as-found state recorded; (2) if the named piece already exists, surface it and stop rather than overwrite (headless: blocked naming the collision).

#### enhancement-2 — Add: name the behavior/payload input in the headless contract

- Lens: enhancement
- Location: `skills/hex-extend/SKILL.md:44-46 (Headless), 30 (Routing)`
- Evidence: Headless requires 'an unambiguous route and names' — but names are not the only interactive input: the module plan's capability table takes 'Name, behavior, invariants' for an aggregate and hex-create passes 'aggregate name + behavior sketch'. The invocation contract never mentions behavior/payload, so the primary automator does not know what to pass, and a behavior-less aggregate request is undefined.
- Recommendation: One sentence in Headless: the invocation carries the piece's behavior sketch/payload where the route needs one; absent it, a command may take the KB-minimal shape, an aggregate returns blocked — behavior is user intent, not a KB convention, so it is never inferred.

#### enhancement-3 — Add: gaps_filed element shape and the unwritable-intake fallback

- Lens: enhancement
- Location: `skills/hex-extend/SKILL.md:46-50 (Headless JSON)`
- Evidence: hex-enforce's headless section specifies that when KB `intake/` is not durably writable (ephemeral CI checkout, read-only KB) each gaps_filed entry carries the gap's full content inline so the caller can re-file. hex-extend files gaps to the same intake/ and is called headlessly in the same environment class, yet its schema shows only "gaps_filed": [] — element type unspecified, no fallback — so filed gaps can silently die with the checkout.
- Recommendation: Adopt the sibling's clause: gaps_filed entries are intake paths, or full inline content when intake/ is not durably writable.

#### architecture-1 — Interactive verify dead-ends when script execution is unavailable

- Lens: architecture
- Location: `skills/hex-extend/SKILL.md (The route skeleton: Verify + Shared machinery)`
- Evidence: Verify mandates the audit be 'settled with gate.py verdict — never by hand'. Shared machinery authorizes the 'unsettled — run hex-enforce' marking only when the audit-core files cannot be resolved, and Headless blocks on script-execution-unavailable — but no clause covers the interactive run where audit-core resolves and gate.py cannot execute; 'never by hand' forbids the only remaining path. hex-enforce handles this branch explicitly.
- Recommendation: Extend the Shared machinery fallback to cover script-execution-unavailable interactively (hand-checks, verdict marked 'unsettled by gate.py'), or scope Verify's 'never by hand' to runs where gate.py executes, mirroring hex-enforce's wording.

#### architecture-2 — Headless mode leaves no durable assumption/decision trail

- Lens: architecture
- Location: `skills/hex-extend/SKILL.md (Headless, Routing, Locate, Generate)`
- Evidence: The skill authorizes headless inference (route, placement, KB-silent markers), but the summary is conversational, the JSON return carries no memlog path, and nothing instructs typed assumption entries — skill-quality-principles.md (Headless mode) requires exactly this discipline. The callers named in Module handoff (hex-create, bmad-loop) consume this skill headlessly, so the buried inferences are consequential. All four siblings share the omission; the fix belongs at module level.
- Recommendation: Add one Headless line: append route/name/placement inferences as typed assumption/decision entries via {project-root}/_bmad/scripts/memlog.py and include the memlog path in the JSON return. Apply to the sibling headless skills in one module-level pass.

### Low (3)

#### architecture-3 — Description trigger set omits the event route

- Lens: architecture
- Location: `skills/hex-extend/SKILL.md (frontmatter description)`
- Evidence: Routing names 'a command or event contract' as a first-class route and the headless enum includes 'event', but the description quotes triggers only for aggregate, command, projection, request handler, and UI page — 'add an event' is absent, making the trigger surface narrower than the routing surface it fronts.
- Recommendation: Add 'add an event' to the quoted trigger list in the description.

#### leanness-1 — Bare-path resolution rule defends against nothing in this skill

- Lens: leanness
- Location: `skills/hex-extend/SKILL.md:17-20 (Resolution rules)`
- Evidence: The bullet 'Bare paths (e.g. `evals/cases.json`) resolve from this skill's installed directory' is house boilerplate, but hex-extend's runtime flow contains no bare path that resolves from its own directory: the KB paths are scoped to the KB root, the audit-core paths to the sibling hex-enforce directory, and the cited example is an eval asset the runtime never loads. In the siblings the same bullet is load-bearing; here it fails the canon's core test. The {project-root} bullet is used once (KB root default) and survives.
- Recommendation: Drop the bare-path bullet; keep the {project-root} gloss as the lone bullet or folded into the Shared machinery line that uses it.
- Proposed smallest: ## Resolution rules

- `{project-root}` → the project working directory.
- Predicted delta: Nothing — no runtime instruction references a bare skill-relative path, so the rule never fires. Route to variant eval to confirm: run add-command-green-gate against the smallest version; expect identical resolution behavior.

#### enhancement-4 — Remove: bare-path bullet of the Resolution rules block governs nothing

- Lens: enhancement
- Location: `skills/hex-extend/SKILL.md:17-20 (Resolution rules)`
- Evidence: The canonical Resolution rules block is stamped for SKILL.mds that reference multiple internal files. hex-extend ships no references/, scripts/, or assets/ and SKILL.md contains no bare internal path except the block's own example; the audit core resolves from the sibling's directory and the KB from {project-root}. The bare-path rule is a house pattern paying rent on nothing here.
- Recommendation: Trim the block to the {project-root} bullet, which the KB-root default actually uses. Lost: only cosmetic uniformity with siblings whose blocks do govern real internal paths.
