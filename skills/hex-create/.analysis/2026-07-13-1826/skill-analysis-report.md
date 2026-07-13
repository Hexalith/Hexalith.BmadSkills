# Analysis Report: skills/hex-create

Generated: 2026-07-13 · Schema: 2

**Grade: Good**

> Structurally sound and lean with zero high or critical findings; the two fixes that mattered — an unexecutable audit-core fallback branch and a disk-to-plan completeness hole in scaffold.py — were applied same-session along with the other eight.

hex-create holds the module's settled-never-asserted bar well: plan-validate-execute with a convention-free script, KB-only conventions, and a sibling-consistent headless contract. The lenses found the bar leaking at three edges (a stray unplanned .csproj invisible to every gate, a hand-tallied files count, and a fallback branch that hand-checks against schemas living in the unresolvable file) plus a plan artifact that was a deliverable nobody could feed back in. All ten findings were applied in the same session's fix pass.

| Severity | Count |
| --- | --- |
| Critical | 0 |
| High | 0 |
| Medium | 4 |
| Low | 6 |

## Themes

### 1. Machine-settled must cover every direction

- Root cause: The skill's own bar — 'created' settled by machines, never asserted — leaked at three edges: verify checked plan-to-disk and plan-to-solution but not disk-to-plan (a stray conformant .csproj passed every gate), the headless files_created count had no machine source, and the interactive fallback told the model to hand-check against schemas that live inside the very file that failed to resolve.
- Fix: Extend scaffold.py verify with an unplanned_on_disk .csproj sweep and a files_present count (both now emitted and unit-tested), and split the fallback conditions to match hex-extend: core unresolvable → 'unsettled — run hex-enforce', core resolved but scripts unavailable → hand-check against its schemas.
- Findings:
  - `determinism-1` verify settles plan-to-disk and plan-to-solution but not disk-to-plan, so 'generate exactly the plan' is partly model-asserted — `skills/hex-create/scripts/scaffold.py:cmd_verify + skills/hex-create/SKILL.md:Scaffold/Verify`
  - `determinism-2` Headless contract field files_created has no machine source — the model tallies it — `skills/hex-create/SKILL.md:Headless (contract JSON)`
  - `architecture-1` Interactive fallback conflates 'audit core unresolvable' with 'script execution unavailable', making one branch unexecutable — `skills/hex-create/SKILL.md — ## Shared machinery`

### 2. The plan artifact is a first-class entry point

- Root cause: Plan declared the scaffold plan 'a deliverable on its own' but no path consumed it: session two would rebuild the plan from scratch, and the restore-point commit's content was unspecified since the plan landed outside the target repo.
- Fix: Scaffold now opens on an existing validated plan (re-validated with scaffold.py plan on entry; headless accepts a plan path recorded in assumptions), and the restore commit is defined: git init, copy the plan into the repo root, commit.
- Findings:
  - `enhancement-1` Add: skip-to-build entry point — Scaffold from an existing validated plan — `skills/hex-create/SKILL.md (Plan and Scaffold stages)`
  - `architecture-2` Plan artifact location and the restore-point commit don't connect — `skills/hex-create/SKILL.md — ## The path from nothing (Plan → Scaffold)`

### 3. Close the degradation and relay enumerations

- Root cause: dotnet and git appeared only in the headless blocked list, leaving interactive Verify with no named path when they are absent; and the seed relay dropped hex-extend's assumptions, hiding unattended inferences from the automation caller.
- Fix: Shared machinery now names the interactive fallback (deliver the scaffold with blocked gates named, marked unsettled, never 'created'), and Seed relays citations, files, assumptions (prefixed seed:), and filed gaps.
- Findings:
  - `enhancement-2` Add: named degradation for dotnet/git unavailable in interactive mode — `skills/hex-create/SKILL.md (Shared machinery, Verify)`
  - `enhancement-3` Add: relay the seed sub-run's assumptions, not only citations, files, and gaps — `skills/hex-create/SKILL.md (Seed stage, Headless)`

### 4. Intro carried positioning prose

- Root cause: Two intro lines failed the canon's core test: the supersedes-the-template sentence changed no reader move where it stood, and the verified-never-asserted rule was stated twice within six lines — together sitting in the token warn band.
- Fix: Cut the supersedes sentence and move its one real deterrent into the Shared machinery KB clause ('nor from the retired Hexalith.MyNewModule template'); end the intro bar at 'every shape cited from the KB', leaving Non-negotiable 1 as the rule's single home.
- Findings:
  - `leanness-1` Supersedes-the-template line is meta-positioning, not an instruction — `skills/hex-create/SKILL.md (intro paragraph)`
  - `leanness-2` Verified-never-asserted rule stated twice within six lines — `skills/hex-create/SKILL.md (intro bar + Non-negotiable 1)`
  - `architecture-3` SKILL.md is over the configured desired token tier (warn band, not a block) — `skills/hex-create/SKILL.md`

## Strengths

- Plan-validate-execute with a deliberately convention-free script: KB-derived rules travel inside the plan JSON as declared constraints with citations, so rules live in the KB and enforcement stays deterministic — the module's meta-drift countermeasure, preserved.
- Conventions live only in the KB: SKILL.md carries no skeleton inventory, so a framework release cannot rot the skill.
- Sibling-consistent architecture: shared audit core resolved from hex-enforce (scope repo, layer full — no rule presumed covered on a newborn repo), headless JSON contract, module handoff footer, single-writer KB with intake-only writes.
- Eval fixtures verified end-to-end before ship: hand-scaffold per KB entries → dotnet build 0 errors, tests green, scaffold.py verify ok, gate.py verdict pass.

## Recommendations

1. Extend scaffold.py verify with the disk-to-plan .csproj sweep (unplanned_on_disk) and a machine files_present count; point the headless files_created field at it. (resolves: determinism-1, determinism-2)
2. Split the interactive fallback conditions per the hex-extend convention and name the dotnet/git-unavailable path inline. (resolves: architecture-1, enhancement-2)
3. Make Scaffold consume an existing validated plan (re-validated on entry, headless plan path in assumptions) and define the restore commit as plan-copied-then-committed. (resolves: enhancement-1, architecture-2)
4. Trim the intro (cut the supersedes sentence, single home for verified-never-asserted) and fold the template deterrent into the KB clause. (resolves: leanness-1, leanness-2, architecture-3)
5. Relay the seed sub-run's assumptions into this run's assumptions prefixed seed:. (resolves: enhancement-3)

## Experience

- **Founding a module interactively** — Capture name/type/target (mine any brief) → build plan from KB entries with citations and constraints → scaffold.py plan validates → approve → git init + plan commit → generate from cited entries → optional seed via hex-extend → build, test, scaffold.py verify, zero-gap gate.py verdict → founding commit.
- **Automation scaffolding headlessly** — Name+type from args (target defaults to ./<name>, recorded) → optional existing plan path supersedes rebuilding → validated plan proceeds without approval → any unsettleable gate returns blocked naming it, scaffold left for inspection → JSON contract with machine-sourced files_created, citations, assumptions, gaps.
- Headless: Headless is a first-class surface: never asks, never guesses names, every gate machine-settled or blocked, every inference surfaced in assumptions.

## Findings

### Medium (4)

#### determinism-1 — verify settles plan-to-disk and plan-to-solution but not disk-to-plan, so 'generate exactly the plan' is partly model-asserted

- Lens: determinism
- Location: `skills/hex-create/scripts/scaffold.py:cmd_verify + skills/hex-create/SKILL.md:Scaffold/Verify`
- Evidence: SKILL.md promises 'generate exactly the plan' and 'the solution references exactly the planned set'. cmd_verify computed missing, missing_from_solution, unplanned_in_solution, and violations — but no disk-to-plan sweep at project granularity. A stray unplanned .csproj on disk never referenced in the .slnx was invisible to every machine gate: verify did not walk for it, dotnet build never compiles an unreferenced project, and gate.py audits convention conformance, not plan conformance.
- Recommendation: Extend cmd_verify with a disk-to-plan project sweep: rglob .csproj under target, skip SKIP_DIRS, diff against the planned set, report unplanned_on_disk failing like the other buckets; add the matching unit test. Keep the sweep to .csproj — the plan's unit of project identity.

#### architecture-1 — Interactive fallback conflates 'audit core unresolvable' with 'script execution unavailable', making one branch unexecutable

- Lens: architecture
- Location: `skills/hex-create/SKILL.md — ## Shared machinery`
- Evidence: The audit procedure and findings schema live in hex-enforce's references/audit-core.md — the exact file that is missing in the 'cannot be resolved' branch, so there are no schemas to hand-check against. The validated sibling hex-extend deliberately splits these cases.
- Recommendation: Split the conditions to match the hex-extend convention: audit core unresolvable → interactive proceeds with the verdict marked 'unsettled — run hex-enforce' (no hand-audit); core resolved but script execution unavailable → hand-check against its schemas and mark 'unsettled by gate.py' / 'unsettled by scaffold.py'. Keep headless blocked in both cases.

#### enhancement-1 — Add: skip-to-build entry point — Scaffold from an existing validated plan

- Lens: enhancement
- Location: `skills/hex-create/SKILL.md (Plan and Scaffold stages)`
- Evidence: The Plan stage declares the scaffold plan 'a deliverable on its own — stopping here is fine', inviting a two-session flow, yet neither Scaffold nor Headless named a way to enter with an existing plan: every path rebuilt the plan, so the approved artifact was never read back. The plumbing already supports it (both subcommands take --file) and hex-migrate models the exact pattern.
- Recommendation: Open Scaffold with the sibling's shape: input a validated scaffold plan; when absent, run Plan first — with scaffold.py plan re-validated on entry. Mirror in Headless: an optional plan path supersedes rebuilding, recorded in assumptions.

#### enhancement-2 — Add: named degradation for dotnet/git unavailable in interactive mode

- Lens: enhancement
- Location: `skills/hex-create/SKILL.md (Shared machinery, Verify)`
- Evidence: dotnet and git appeared only in the headless blocked list; interactively, Verify's build/test cannot be hand-checked the way scaffold.py/gate.py can, and the non-negotiable forbids claiming 'created' without the full gate — so an interactive run without dotnet reached Verify with no named path.
- Recommendation: One clause in Shared machinery beside the existing fallback: dotnet or git unavailable — interactive delivers the scaffold with the gates it blocks named and the result marked unsettled, never 'created'; headless returns blocked.

### Low (6)

#### determinism-2 — Headless contract field files_created has no machine source — the model tallies it

- Lens: determinism
- Location: `skills/hex-create/SKILL.md:Headless (contract JSON)`
- Evidence: The headless return contract requires files_created, but nothing deterministic emits that number: scaffold.py plan reports planned counts and verify returned only ok/missing/violation buckets. Counting files actually created is a metrics-category operation with one correct answer per input.
- Recommendation: Have cmd_verify emit a files_present count from its existing walk and point the contract field at that machine value.

#### architecture-2 — Plan artifact location and the restore-point commit don't connect

- Lens: architecture
- Location: `skills/hex-create/SKILL.md — ## The path from nothing (Plan → Scaffold)`
- Evidence: The plan lands in {output_folder}/hex/ — outside the target repo — while Scaffold says 'git init and commit the plan first', inside the freshly initialized, required-empty target. Nothing says the plan gets copied into the repo, so the later stage cannot commit it without an inferred move.
- Recommendation: Make the handoff explicit in Scaffold: git init, copy the validated plan into the repo root, and commit it so a restore point exists.

#### architecture-3 — SKILL.md is over the configured desired token tier (warn band, not a block)

- Lens: architecture
- Location: `skills/hex-create/SKILL.md`
- Evidence: prepass-metrics.json: 1582 tiktoken tokens against the prepass tiers — inside the warn band the principles define. No section is a carve candidate: every section is paid on both modes or is the headless contract itself.
- Recommendation: Accept the warn or recover tokens through line-level trims (leanness's lane) rather than carving; do not restructure — the inline topology is correct for this skill.

#### enhancement-3 — Add: relay the seed sub-run's assumptions, not only citations, files, and gaps

- Lens: enhancement
- Location: `skills/hex-create/SKILL.md (Seed stage, Headless)`
- Evidence: Seed said 'relay its citations, files, and filed gaps', but hex-extend's headless return also carries assumptions (route, name, placement inferences made unattended). Dropping them means an automation caller sees a seeded aggregate whose unattended inferences are invisible.
- Recommendation: Extend the relay list to citations, files, assumptions, and filed gaps, folding hex-extend's assumptions into hex-create's assumptions array prefixed seed:.

#### leanness-1 — Supersedes-the-template line is meta-positioning, not an instruction

- Lens: leanness
- Location: `skills/hex-create/SKILL.md (intro paragraph)`
- Evidence: 'It supersedes the Hexalith.MyNewModule template and its rename script.' describes the system to itself — it changes no reader move where it stands. The one move it might deter (scaffolding by cloning the known template) is a real temptation the Shared machinery rule did not quite cover.
- Recommendation: Cut the sentence from the intro and spend its tokens where the rule lives: extend the Shared machinery KB clause to name the wrong move explicitly ('nor from the retired Hexalith.MyNewModule template').

#### leanness-2 — Verified-never-asserted rule stated twice within six lines

- Lens: leanness
- Location: `skills/hex-create/SKILL.md (intro bar + Non-negotiable 1)`
- Evidence: The intro's bar clause ended 'settled by machines, never asserted', and Non-negotiable 1 immediately restated it. The validated sibling hex-extend leaves verified-not-asserted to its non-negotiable alone.
- Recommendation: Keep Non-negotiable 1 — it carries the rule plus the gate mechanics — and end the intro bar at 'every shape cited from the KB', matching the sibling's division of labor.
