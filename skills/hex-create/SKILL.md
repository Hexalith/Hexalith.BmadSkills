---
name: hex-create
description: Scaffolds new Hexalith module repos correct by construction. Use when the user says 'create a hexalith module', 'scaffold a new module', 'new domain module', 'new technical module', or 'start a new hexalith module repo'.
---

# hex-create

This skill turns nothing into a working Hexalith module repository — green build, passing tests, zero-gap audit, in one session. Act as the founding engineer for three consumers: the framework author spinning up the next module, the adopter whose only Hexalith knowledge is the installed skills, and automation calling headlessly. The bar all three share: the newborn repo is indistinguishable from one the framework author shaped by hand — every shape cited from the KB.

**Non-negotiables:**

- "Created" is never claimed without the full green gate: build, tests, completeness, and a zero-gap audit verdict. Correct by construction is verified, never asserted.
- The module's name and type are user intent, not conventions — never guessed. Interactive asks; headless returns blocked.

Converse in `{communication_language}`; write plans and run summaries in `{document_output_language}`.

## Resolution rules

- Bare paths (e.g. `scripts/scaffold.py`) resolve from this skill's installed directory.
- `{project-root}` → the project working directory.

## Shared machinery

KB root defaults to `{project-root}/_bmad/hex/knowledge/`; an explicit path in the invocation overrides it. Start from `index.md` and load the structure, packaging, and naming entries — the skeleton's shape comes entirely from there, never from model memory of how .NET repos usually look nor from the retired Hexalith.MyNewModule template: a memorized layout is exactly the drift this module exists to kill. Where the KB is silent on something the skeleton needs, file the gap to `intake/` (source: create — shape from the sibling hex-absorb skill's `assets/intake-template.md`, checked with its `scripts/kb.py validate`) and surface the hole in the plan rather than improvising. No KB → blocked (hex-absorb's seed intent founds it).

The audit gate is the shared audit core shipped with the sibling hex-enforce skill, installed beside this one: load its `references/audit-core.md` and run its `scripts/gate.py` from that skill's directory — scope `repo`, layer `full`, because a newborn repo's analyzer wiring is unproven, so no rule is presumed covered. An explicit audit-core path in the invocation overrides the sibling lookup. `scripts/scaffold.py` owns this skill's deterministic work — `plan` (schema-validate the scaffold plan: name legality, internal consistency, declared constraints, empty target) and `verify` (planned projects and files all exist on disk and the solution references exactly the planned set — solution parsing is `.slnx`-only, so plans must declare a `.slnx` solution). Interface and plan schema: `uv run scripts/scaffold.py --help`. When the audit core cannot be resolved, interactive proceeds with the verdict marked `unsettled — run hex-enforce`; when it resolves but script execution is unavailable, do the checks by hand against its schemas and mark the result `unsettled by gate.py` or `unsettled by scaffold.py`. When dotnet or git is unavailable, interactive delivers the scaffold with the gates it blocks named and the result marked unsettled. Headless returns blocked in every one of these cases — an unsettled verdict cannot claim correct-by-construction.

## The path from nothing

**Plan** — capture what only the user knows: module name, type (technical or domain), target directory, and any first domain concepts; mine whatever they point at (a brief, a PRD) before asking. Then build the skeleton inventory from the KB's structure entries into a machine-readable scaffold plan — every project, file, and wiring step carrying its convention citation — plus the checks the KB imposes on this module type as declared constraints (a domain module excludes hosting and persistence per the KB's boundary entry; a request that crosses the boundary is excluded with the citation named, not obeyed). Validate with `scaffold.py plan`. The plan lands in `{output_folder}/hex/` unless the user points elsewhere, and is a deliverable on its own — stopping here is fine. Interactive approval gates scaffolding; headless proceeds on a plan that validates.

**Scaffold** — input: a validated scaffold plan (a path in the invocation, or the one Plan just produced); when absent, run Plan first — plan always precedes scaffold, and a resumed plan is re-validated with `scaffold.py plan` on entry. The target directory must be empty or absent: adding to an existing module is hex-extend's job and bringing an old repo current is hex-migrate's — surface the collision rather than write into it (headless: blocked). `git init`, copy the plan into the repo root, and commit it — that plan-only commit is the gate: not one file is generated until it exists, because a generation with no restore point cannot be safely abandoned. Then generate exactly the plan, every file's shape from its cited KB entry. Wiring that reaches outside the repo (a submodule fetch, a package restore) can fail without network — surface the failure and mark the checks it blocks, never silently skip.

**Seed** — optional first aggregate, so the repo is not born empty: delegate headlessly to the sibling hex-extend skill with the aggregate name and behavior sketch from the plan, and relay its citations, files, assumptions, and filed gaps into this run's summary — the sub-run's assumptions land in this run's `assumptions` prefixed `seed:`. hex-extend unresolvable or blocked → interactive offers proceeding unseeded; headless returns blocked only when seeding was explicitly requested.

**Verify** — the green gate, in order: `dotnet build`, `dotnet test`, `scaffold.py verify` (completeness — a green build cannot catch a planned-but-never-created project), then the audit core settled with `gate.py verdict`: zero gaps, and a newborn repo has nothing to waive. Iterate to green interactively — a gap means the scaffold, the plan, or the KB is wrong, and which one it is goes in the summary. Headless, a gate that will not settle leaves the scaffold in place for inspection and returns blocked naming the failing gate. Once green, commit the scaffold as the founding commit and deliver the repo with a summary citing its convention ids.

## Headless

`--headless` / `-H`: never ask — the automation surface. Requires module name and type in the invocation; the target directory defaults to `./<module-name>` and the default is recorded in `assumptions`, as is every other inference made without the user. An existing plan path in the invocation supersedes rebuilding the plan (recorded in `assumptions`); `files_created` comes from `scaffold.py verify`'s `files_present`, never a hand tally. When the KB's `intake/` is not durably writable, each `gaps_filed` entry carries the gap's full content inline instead of a path, so the caller can re-file it. Return blocked when the KB or the audit core cannot be resolved, the module name or type is missing or ambiguous, the target directory is non-empty, dotnet or git is unavailable, seeding was requested but hex-extend cannot run or returns blocked, any gate will not settle (build, tests, `scaffold.py verify`, the zero-gap audit), or script execution is unavailable. End with:

```json
{"status": "complete|blocked", "module": "", "type": "technical|domain", "path": "", "plan": "", "files_created": 0, "verdict": "pass|n/a", "seeded": false, "citations": [], "assumptions": [], "gaps_filed": [], "reason": "<only when blocked>"}
```

## Module handoff

module-code: hex · phase: authoring · after: hex-extend · is-required: true · composability: calls the sibling hex-extend headlessly to seed the first aggregate; verify runs the sibling hex-enforce audit core repo-scoped (scope `repo`, layer `full`) plus `scripts/scaffold.py` completeness; reads KB `entries/` and `index.md`, writes only `intake/` (source: create).
