---
title: 'Module Plan — BMAD Hexalith Module'
status: 'complete'
module_name: 'BMAD Hexalith Module'
module_code: 'hex'
module_description: 'LLM skills to develop and maintain Hexalith modules: create, extend, migrate, and enforce framework conventions.'
architecture: 'six workflow skills over a shared knowledge base and audit core; no agents in v1'
standalone: true
expands_module: ''
skills_planned:
  - hex-create
  - hex-extend
  - hex-migrate
  - hex-enforce
  - hex-consult
  - hex-absorb
config_variables:
  - hex_framework_source
  - hex_fleet_manifest
  - hex_verbosity
created: '2026-07-13'
updated: '2026-07-13'
---

# Module Plan — BMAD Hexalith Module

**Source brief:** `_bmad-output/planning-artifacts/briefs/brief-bmadskills-2026-07-13/brief.md` (+ addendum) — status: final.

## Vision

A BMAD v6 module — peer of bmm and tea — that turns Hexalith's coding practices, architectural patterns, and development conventions into **executable knowledge**. Installed into any Hexalith module repository or workspace, it makes every AI-assisted session (human-plus-agent or agent-only) apply the framework's current conventions by default.

It kills consistency drift at both ends: sibling modules solving the same concern differently, and — the sharper pain — ~20 module repos lagging behind a framework that ships weekly. Six jobs: **Create** (scaffold correct-by-construction), **Extend** (add conformant pieces), **Migrate** (audit → tiered gap report → driven upgrade — the beating heart), **Enforce** (two-layer conformance gate), **Consult** (answer any conformance question from the skills alone), **Absorb** (eat each framework release so the module never lags the framework the way modules did).

Serves the framework author first (session velocity), the Itaneo team next (conformance without a year of context), and external adopters as the reason installation and documentation are real scope. End state: Hexalith.AI.Tools drained to a pointer, and conformance policing done by machines while humans make design decisions.

## Architecture

**Decision: six workflow skills. No agents, no orchestrator in v1.**

| Skill | Job |
| ----- | --- |
| `hex-create` | Scaffold a new technical or domain module, correct by construction |
| `hex-extend` | Add aggregate / command / event / projection / request handler / UI page to an existing module (routed capabilities) |
| `hex-migrate` | Audit repo against current conventions → tiered gap report → drive the upgrade |
| `hex-enforce` | Two-layer conformance gate: Roslyn analyzer (mechanical) + LLM review (judgment) |
| `hex-consult` | Q&A over the knowledge base, verbosity knob (terse / explain-as-you-go) |
| `hex-absorb` | Ingest a framework release → propose KB updates → verify KB against source → drive the AI.Tools drain |

**Why workflows, not agents:** every job is headless-first — CI, bmad-loop, and other sessions invoke them; none needs a persistent persona or learned per-user memory. The expertise lives in the versioned knowledge base, not in agent memory. The conversational surface is covered by `hex-consult` without a persona. An optional "Hexa" orchestrator agent remains a v2 idea if a conversational hub proves wanted.

**Why six skills, not families:** one trigger surface per job ("add a command to parties" → `hex-extend` routes internally). Fewer skills keeps the 4-platform maintenance matrix affordable. Split a skill only if it gets fat.

**Shared audit core.** A single audit engine — shared module asset (instructions + operational checklist projected from the KB) — is the one place "conformant" is defined operationally. Three consumers: `hex-migrate` runs it repo-wide, `hex-enforce` runs it diff-scoped, and the fleet report runs it per-repo then aggregates. Fix an audit bug once.

**Enforce is two-layer in v1 (scope amendment).** Mechanical conventions (EventStore-mandatory, ULIDs, package shape, …) are enforced at compile time by a Roslyn analyzer distributed through Hexalith.Builds — which every module repo already pulls. The LLM skill handles judgment calls only. This amends the brief's scope: Hexalith.Builds analyzer work is now IN scope for v1. The KB's mechanical/judgment tag decides which layer owns each rule; Enforce detects analyzer coverage and skips covered rules, so the two layers never double-report.

**Single shared knowledge base, indexed.** One module-level knowledge folder is the single source of truth all six skills load from selectively via an index. Every entry carries: convention id, `mechanical | judgment` tag, since/until framework-version range (powers Migrate's from-state recognition), AI.Tools provenance (file#section — powers the drain ledger), and verified-against-source date (powers the monoculture countermeasure). Same entries, different projections: Migrate needs old+new, Consult needs the why, Enforce needs the check.

**Version coupling.** The module declares one `targets_framework: >= X.Y` per release; release notes state the pair. Enforce's staleness alarm compares the declared target against the repo's actual framework version and warns when the module lags.

**Waivers live in the target repo.** A versioned waivers file (convention id, reason, review date) in each module repo — reviewable in PRs, visible to CI Enforce, travels with the repo. The audit core reads it; the fleet report surfaces waiver counts so they can't silently accumulate.

### Memory Architecture

**No BMAD memory folders — deliberate.** All six skills are stateless workflows. State lives where it's versioned and reviewable instead:

| State | Home | Why |
| ----- | ---- | --- |
| Conventions knowledge base | Module assets (versioned, shipped) | Single source of truth; updated only via `hex-absorb`'s reviewable changes |
| Drain ledger | KB entry metadata (provenance fields) | "Fully drained" must be measurable, not remembered |
| Waivers / intentional deviations | Target repo (versioned file) | CI and every machine must see them |
| Audit outputs, gap reports, fleet report | `{output_folder}` | Session artifacts, not knowledge |

If a v2 "Hexa" orchestrator agent materializes, per-user memory can be revisited then.

### Memory Contract

Not applicable — no shared memory folder. The knowledge base contract (entry metadata schema above) serves the equivalent role and is documented in the Architecture section.

### Cross-Agent Patterns

No agents — these are cross-**skill** patterns:

- **The KB is the hub.** `hex-absorb` is the only writer; the other five are readers. All cross-skill consistency flows from this single-writer rule.
- **The audit core is the shared service.** Migrate (repo-wide), Enforce (diff-scoped), and the fleet aggregator (per-repo × N) are three invocations of one engine.
- **The user (or the loop) is the router.** Typical chains: `hex-migrate` audit → human approves tiers → `hex-migrate` drives → `hex-enforce` gates the PR. Unattended: bmad-loop runs Enforce (and later Migrate's mechanical tier) headlessly — mechanical fixes applied, judgment calls escalated.
- **Consult is everyone's fallback.** Any session (or skill) resolving a "why" question defers to `hex-consult` rather than re-deriving from raw KB entries.

## Skills

All six are **workflows** (no personas, no memory — see Memory Architecture). All are **interactive AND headless**; headless behavior is specified per skill. All load the shared KB selectively via its index and cite convention ids in their outputs. Every skill ships an eval suite (run by the repo's eval runner) — passing evals gates release AND gates the AI.Tools drain of the content it absorbed.

### hex-create

**Type:** workflow

**Purpose:** Scaffold a new Hexalith technical or domain module, correct by construction. Supersedes `Hexalith.MyNewModule` + `initialize.ps1`.

**Core Outcome:** Nothing → green build and passing tests in a single session, zero knowledge outside the installed skills (this is success criterion #1 verbatim).

**The Non-Negotiable:** The generated module passes the shared audit core with **zero gaps** — correct by construction is verified, never asserted.

**Capabilities:**

| Capability | Outcome | Inputs | Outputs |
| ---------- | ------- | ------ | ------- |
| Plan scaffold | Interview (interactive) or args (headless) → approved scaffold plan | Module name, type (technical/domain), domain concepts, target directory | Scaffold plan (name, packages, structure) |
| Scaffold solution | Complete repo skeleton: `.slnx`, per-layer NuGet packages (Domain `.Aggregates/.Abstractions/.Events`, Application `.Commands/.Requests/.Application/.Projections`, Infrastructure `.ApiServer/.WebServer/.WebApp`, Presentation `.UI.Components/.UI.Pages/.Localizations`, `test/`), central package management, Hexalith.Builds submodule, CI, semantic-release config | Approved plan | Buildable repo skeleton |
| Seed first aggregate | Optional: hand off to hex-extend for the first aggregate so the repo isn't empty | Aggregate name + behavior sketch | Conformant aggregate + tests |
| Verify | Green gate: build + tests + audit-core self-check | Scaffolded repo | Pass/fail + audit summary |

**Activation Modes:** Both. Headless takes all inputs as args, fails loudly on ambiguity (never guesses a module name).

**Tool Dependencies:** dotnet SDK 10+, git. Reads KB for structure/naming conventions.

**Design Notes:** Domain modules get domain code only — no AppHost, no Aspire wiring, no persistence (module boundary rule; boilerplate comes from Hexalith.EventStore's domain-service SDK). The audit-core self-check is the template-rot canary: when a framework release breaks scaffolding, evals catch it.

**Relationships:** Delegates first-aggregate seeding to hex-extend. Its output is hex-enforce-clean by definition. Built LAST — it composes conventions the other skills will have hardened.

---

### hex-extend

**Type:** workflow

**Purpose:** Add a conformant piece to an existing Hexalith module. One trigger surface, routed internally.

**Core Outcome:** The addition is indistinguishable from framework-author-written code — conformant by default, tests included, green build maintained.

**The Non-Negotiable:** Never adds code without its tests. An aggregate without per-aggregate xUnit tests is not "added".

**Capabilities:**

| Capability | Outcome | Inputs | Outputs |
| ---------- | ------- | ------ | ------- |
| Route intent | "Add a command to parties" → correct route + target location | Natural-language intent, target repo | Route + plan |
| Add aggregate | Pure-function aggregate (`Handle(Command, State?) → DomainResult`, `Apply(Event)`) + tests | Name, behavior, invariants | Aggregate, events, tests |
| Add command / event | Contract types in the right packages, ULID ids, tenant/partition fields, polymorphic serialization registration | Name, payload, owning aggregate | Contract code + handler wiring + tests |
| Add projection | Read-model handler wired per conventions | Source events, read model shape | Projection + tests |
| Add request handler | Query-side handler per conventions | Request/response shape | Handler + tests |
| Add UI page | Blazor Fluent UI V5 page composed via FrontComposer, localization stubs | Page purpose, backing requests | Page + components + localization entries |
| Verify | Green gate: build + tests + diff-scoped audit | The change | Pass/fail + citations |

**Activation Modes:** Both. Headless requires unambiguous route + names in args.

**Tool Dependencies:** dotnet SDK 10+, git. Reads KB per-route (patterns, package placement, naming).

**Design Notes:** Routes share a common skeleton (locate → generate → wire → test → verify) with per-route pattern references — this is where "one skill, routed capabilities" pays off. If one route grows fat (UI page is the candidate), split it in a later release.

**Relationships:** Called by hex-create for seeding. Its verify step is a thin wrapper over the shared audit core (diff-scoped) — same engine as hex-enforce.

---

### hex-migrate

**Type:** workflow — **the beating heart**

**Purpose:** Keep ~20 repos current with a framework that ships weekly: audit a module against current conventions, produce a tiered gap report, drive the upgrade.

**Core Outcome:** A lagging repo reaches the current framework conventions with every applied step landing on green build + passing tests.

**The Non-Negotiable:** **Never leaves a repo red.** Every applied step ends green or is rolled back. A half-migrated broken repo is worse than a lagging one.

**Capabilities:**

| Capability | Outcome | Inputs | Outputs |
| ---------- | ------- | ------ | ------- |
| Audit | Repo-wide audit-core run with from-state recognition (KB since/until ranges); reads waivers; staleness check | Target repo | **Gap report** (HTML + machine-readable): gaps tiered mechanical / structural / judgment, each citing convention ids |
| Plan migration | Ordered migration plan: step order, risk notes, checkpoint after each step | Gap report, human tier approvals (interactive) | Migration plan |
| Drive upgrade | Execute plan: mechanical auto-fixed; structural per approved plan; judgment prompts human (interactive) or escalates (headless). Green gate per step. | Approved plan | Migrated repo + migration log |
| Fleet audit | Audit across all fleet-manifest repos, aggregate | `hex_fleet_manifest` | **Fleet conformance report** (HTML): lag per repo, drift hot-spots, waiver counts |

**Activation Modes:** Both. Headless/loop: audit always allowed; drive applies the **mechanical tier only** and escalates the rest (bmad-loop escalation pattern).

**Tool Dependencies:** dotnet SDK 10+, git; gh for fleet operations (cloning/scanning manifest repos).

**Design Notes:** Needs the fullest KB of the six — old AND new conventions (the brief is explicit). The machine-readable gap report is the contract with the fleet aggregator and the loop. Rollback = git discipline: each step is a commit, red gate reverts it.

**Relationships:** Audit is the shared audit core run repo-wide — same engine as hex-enforce (diff-scoped). Fleet report consumes per-repo audits. Judgment escalations may cite hex-consult explanations to help the human decide.

---

### hex-enforce

**Type:** workflow

**Purpose:** Two-layer conformance gate: Roslyn analyzer (mechanical, compile-time, via Hexalith.Builds) + LLM review (judgment). Interactive, CI, and loop-invocable.

**Core Outcome:** Drift is caught at the PR, cited precisely, and the gate is cheap enough that it's still enabled three months later.

**The Non-Negotiable:** Every failure cites the specific KB convention id and the offending code. No vibes-based rejections — an uncitable objection is not a failure.

**Capabilities:**

| Capability | Outcome | Inputs | Outputs |
| ---------- | ------- | ------ | ------- |
| Review diff | Diff-scoped audit-core run, judgment layer only (skips analyzer-covered rules); reads waivers | Diff/PR, target repo | Verdict + cited findings |
| CI gate | Machine-readable verdict, PR annotations via gh, exit code | PR context | Pass/fail + annotations |
| Staleness alarm | Warn when module `targets_framework` lags the repo's actual framework version | Repo + module metadata | Warning in every verdict |
| Analyzer coverage map | Report which KB `mechanical` rules the current analyzer covers, which are gaps | KB + analyzer rule list | Coverage report (drives analyzer backlog) |
| Propose waiver | Draft a well-formed waiver entry (convention id, reason, review date) for human approval | Finding + justification | Waiver diff for the target repo |

**Activation Modes:** Both. CI/loop mode is the primary design target — headless is not the afterthought here, interactive is.

**Tool Dependencies:** gh (annotations), git. The Roslyn analyzer itself ships via Hexalith.Builds (separate deliverable, scope amendment); Enforce consumes its coverage.

**Design Notes:** Never double-reports: the KB mechanical/judgment tag + coverage map decide which layer owns each rule. Waivers suppress findings but are surfaced in the verdict summary (visible, not silent).

**Relationships:** Diff-scoped invocation of the shared audit core. hex-extend's verify step is the same call. Escalated judgment calls can pull hex-consult explanations. The analyzer backlog (coverage gaps) feeds framework-side work.

---

### hex-consult

**Type:** workflow

**Purpose:** Answer any Hexalith conformance question from the skills alone — the executable replacement for "ask Jérôme".

**Core Outcome:** A session resolves any conformance question without leaving the installed skills (success criterion verbatim). Verbosity matches the audience: terse for the expert, explain-as-you-go for the adopter.

**The Non-Negotiable:** Answers come ONLY from the KB and framework source — never from model memory. "Not in the KB" is a valid answer and files a KB gap; a confident hallucinated convention is the worst possible output.

**Capabilities:**

| Capability | Outcome | Inputs | Outputs |
| ---------- | ------- | ------ | ------- |
| Answer question | Cited answer (convention ids), at `hex_verbosity` level | Question, optional repo context | Answer + citations |
| Show conformant example | Working example: generated fresh or pointed to in framework source / reference modules | Concept ("a command handler") | Example + why-it's-shaped-this-way notes |
| Explain finding | Turn an audit/enforce finding into an explanation: what the convention is, why it exists, what conformant looks like here | Finding (convention id + code location) | Explanation |
| File KB gap | Unanswerable question → structured gap entry in hex-absorb's intake | The question + context | Gap entry |

**Activation Modes:** Both. Headless mode is the service surface other skills/sessions call.

**Tool Dependencies:** gh or local path for framework source lookups (`hex_framework_source`).

**Design Notes:** The verbosity knob dissolves the v1-audience tension (addendum idea, adopted). Gap-filing is how the module learns where it's blind — every unanswered question is absorb backlog, not a shrug.

**Relationships:** Reader of the KB, never a writer (single-writer rule: absorb). Called by migrate/enforce for judgment-call explanations. First real consumer that proves the KB's quality.

---

### hex-absorb

**Type:** workflow

**Purpose:** The module's metabolism: eat framework releases, keep the KB true, drive the AI.Tools drain. The meta-drift countermeasure as a skill.

**Core Outcome:** A convention-affecting framework release is reflected in the module within one release cycle — and the KB provably matches framework reality.

**The Non-Negotiable:** KB changes are always reviewable diffs with provenance — never silent edits. The KB is the fleet's single source of truth; corrupting it ships errors to twenty repos at machine speed.

**Capabilities:**

| Capability | Outcome | Inputs | Outputs |
| ---------- | ------- | ------ | ------- |
| Ingest release | Read framework release (notes, diffs, tags) → proposed KB updates as reviewable change → bump `targets_framework` | Release ref (or "latest") | KB update diff + impact note (which conventions changed) |
| Verify KB against source | Sample KB claims, check each directly against framework source/reference repos; stamp verified dates; flag mismatches | Sample size / specific entries | Verification report (the monoculture countermeasure) |
| Drain AI.Tools | For content whose absorbing skill passes evals: generate deletion PR against Hexalith.AI.Tools, update provenance ledger | Eval results, ledger state | Deletion PR + drain % report |
| Process gap intake | Turn filed gaps (from consult/enforce) into drafted KB entries for review | Gap queue | Drafted entries |
| Seed KB (first run) | Initial absorption: hexalith-llm-instructions.md + addendum inventory + framework source → the founding KB | AI.Tools content, framework source | Founding KB with full provenance |

**Activation Modes:** Both. Author-run per release at first; loop-runnable later (vision). Ingest + verify are headless-safe (they only propose); merging KB changes stays human.

**Tool Dependencies:** gh (release reading, drain PRs, framework source), git.

**Design Notes:** Owns the KB entry schema: id, statement, why, conformant example ref, `mechanical|judgment` tag, since/until framework range, AI.Tools provenance, verified date. The pre-release impact preview (run against a release candidate) is a creative use case that falls out for free.

**Relationships:** The ONLY KB writer. Everything downstream depends on it — which is why it's built first. Consumes gap filings from consult and enforce. Its verification capability is the independence check the monoculture risk demands.

## Configuration

Three custom variables collected at setup. Skills must have sensible fallbacks when config is absent (ask at runtime for the specific value needed).

| Variable | Prompt | Default | Result Template | User Setting |
| -------- | ------ | ------- | --------------- | ------------ |
| `hex_framework_source` | "Where should skills read Hexalith framework sources? (GitHub org name or local workspace path)" | `Hexalith` (GitHub org, via gh) | `hex_framework_source: "{value}"` | yes |
| `hex_fleet_manifest` | "Path to the fleet manifest listing your Hexalith module repos" | `{project-root}/hex-fleet.yaml` | `hex_fleet_manifest: "{value}"` | yes |
| `hex_verbosity` | "Default explanation style: terse (expert) or explain (adopter)?" | `explain` | `hex_verbosity: "{value}"` | yes |

Reports and audit artifacts go to the core `output_folder` — no additional variable.

## External Dependencies

Setup **checks and guides, never blocks** — skills re-check at runtime for the specific tool they need.

| Dependency | Needed by | Setup handling |
| ---------- | --------- | -------------- |
| .NET 10+ SDK | create/extend/migrate green-build gates; analyzer build | Check version, guide install if missing |
| git | all skills | Check presence |
| gh CLI (authenticated) | absorb (release reading, drain PRs), fleet operations, enforce CI annotations | Check presence + auth, guide install/login |

No MCP server dependencies in v1.

## UI and Visualization

Two HTML report artifacts, no web app in v1:

- **Gap report** (per repo) — output of hex-migrate's audit: tiered gaps (mechanical/structural/judgment), from-state recognition, waiver status, staleness alarm. The document a human reviews before approving a migration.
- **Fleet conformance report** — aggregation of per-repo audits across the fleet manifest: who lags, by how much, drift hot-spots, waiver counts. Aims the migration effort.

v2 candidate: interactive fleet dashboard (continuous conformance tracking).

## Setup Extensions

- **Fleet manifest scaffold:** if `hex-fleet.yaml` doesn't exist, offer to create a starter — pre-filled from the Hexalith GitHub org when gh is available, else a commented template.
- **Tool checks** with install guidance (see External Dependencies).
- Nothing else: no web app, no service configuration. Waivers files are created on demand by Enforce/Migrate, not at setup.

## Integration

**Standalone module** — a peer of bmm and tea, installable into any Hexalith module repo or workspace with no dependency on other BMAD modules.

Synergies (all optional, none required):

- **bmad-loop:** hex-enforce and hex-migrate's mechanical tier are designed to be loop-driven — mechanical fixes applied, judgment calls escalated. The loop wiring already in this repo is the intended harness.
- **tea:** testing conventions (xUnit v3 + Shouldly + NSubstitute) live in the KB; tea's skills can go deeper on test strategy — no overlap, hex owns *conformance*, tea owns *quality*.
- **bmm:** PRD/architecture/story skills operate upstream of hex; a story implemented via bmad-dev-story can be gated by hex-enforce downstream.
- **Hexalith.Builds (framework side):** carries the Roslyn analyzer that is Enforce's mechanical layer — the one deliberate framework-side deliverable (scope amendment).

## Creative Use Cases

- **Onboarding tour:** a new Itaneo developer's first session is `hex-consult` in explain mode against a real repo — "walk me through why this module is shaped this way."
- **Convention archaeology:** `hex-consult` + KB since/until ranges answer "when did we stop doing X, and why?" — release-by-release convention history.
- **Gap-driven KB growth:** every question Consult can't answer and every judgment call Enforce can't decide is filed as a KB gap → hex-absorb's intake queue. The module learns where it's blind from its own usage.
- **Pre-release impact preview:** run hex-absorb against a framework release *candidate* to see which conventions would change and how many fleet repos it would affect — before shipping it.
- **Template regression canary:** hex-create's output is itself audit-checked; if a framework release breaks correct-by-construction, the eval suite catches it before any user does.

## Ideas Captured

### From the brief (final, 2026-07-13)

- **The spark:** a BMAD v6 module — peer of bmm/tea — that ships the LLM skills to develop and maintain Hexalith technical and domain modules. Turns the framework's conventions into *executable* knowledge instead of descriptive docs that rot.
- **The pain:** consistency drift across ~20 independently-developed module repos, and (sharper) lag behind a fast-moving framework (162 core releases, still preview, weekly cadence).
- **Four jobs, in order of pain (not build order):**
  1. **Migrate** — the beating heart. Audit a module against current conventions → gap report → drive the upgrade.
  2. **Create** — scaffold a new technical/domain module, correct by construction. Supersedes `Hexalith.MyNewModule` + rename script.
  3. **Extend** — add aggregate/command/event/projection/request handler/UI page to an existing module, conformant by default.
  4. **Enforce** — review changes against conventions, fail on drift. Interactive, CI, and unattended bmad-loop.
- **Users:** framework author (Jérôme) → Itaneo team → external adopters. The *agent* is as much a user as the human — headless operation is first-class.
- **Standing rule (decided):** knowledge added here is drained from Hexalith.AI.Tools — deletion only after the absorbing skill passes evals. End state: AI.Tools is a pointer.
- **Conventions to encode:** EventStore-mandatory CQRS/ES, pure-function aggregates (`Handle(Command, State?) → DomainResult`, `Apply(Event)`), ULIDs, vertical-slice DDD, per-layer NuGet packages, module boundary rule (domain modules = domain code only), Blazor Fluent UI V5 via FrontComposer, xUnit v3 + Shouldly + NSubstitute, `.slnx`, Conventional Commits + semantic-release, SDK-built containers, central package management, Hexalith.Builds submodule.
- **Success signals worth designing for:** nothing→green-build in one session; two real migrations; AI.Tools fully drained; Enforce still enabled after 3 months; convention-affecting release reflected within one release cycle (×2); one non-author install produces a conformant module.
- **Risks to design against:** meta-drift (skills lag framework — staleness alarm: skills declare target framework version, Enforce warns); monoculture error (Migrate writes what Enforce checks — need ≥1 check not derived from the knowledge base — open); version coupling (open); platform matrix ×4 (tier or budget — open); distribution mechanics (open — first domino of adopter path).
- **Parked ideas from addendum:**
  - Machine-readable conventions manifest published by the framework per release — a skill that never memorized rules can't lag. Requires framework change (currently out of scope).
  - Enforce tiering: mechanical rules → Roslyn analyzer via Hexalith.Builds; LLM skill reserved for judgment calls. Lowers cost of keeping Enforce enabled.
  - Audience verbosity knob: terse for the author, explain-as-you-go for adopters — one skill, two modes.
  - Skill granularity: four skills vs. four *families* of finer-grained skills — deliberately not fixed in the brief; ours to decide here.
  - Unattended fleet maintenance via bmad-loop across all repos — vision, not v1.
  - Cheap migration as moral hazard — nothing pushes preview framework toward stable. Revisit at 1.0 planning.

### From ideation session

**Validated decisions (recommend-then-validate mode, 2026-07-13):**

- **Migrate UX — tiered audit-then-drive.** Audit ALWAYS runs first → gap report (HTML report candidate) tiering gaps into: *mechanical* (safe auto-fix), *structural* (proposed plan, needs approval), *judgment* (human decision). Interactive: review report, approve per tier, drive upgrade with green-build gates at each step. Headless/loop: apply mechanical tier only, escalate the rest — aligns with bmad-loop escalation patterns.
- **Consult is a fifth job — dedicated skill.** `hex-consult`: thin Q&A layer over the shared knowledge base, with the verbosity knob from the addendum (terse for the author, explain-as-you-go for adopters). Callable by humans and by other skills/sessions headlessly. Directly satisfies the "resolve any conformance question from the skills alone" success criterion.
- **Absorb is a sixth job — dedicated skill.** `hex-absorb`: reads a framework release (notes, diffs, tags) → proposes knowledge-base updates as a reviewable change → bumps the declared target framework version. Author-run per convention-affecting release at first; loop-runnable later. Makes the meta-drift ritual executable instead of remembered. Staleness alarm stays in Enforce.
- **Fleet visibility v1 — aggregated audit report.** Audit runs per-repo; a thin aggregator merges per-repo audit outputs into one fleet HTML report (who lags, by how much, drift hot-spots). Nearly free once audit exists; aims the two real migrations. Interactive dashboard/web app deferred to v2.
- **Enforce is two-layer in v1 — AMENDMENT, user went beyond recommendation.** Roslyn analyzer for mechanical conventions ships in v1, distributed via Hexalith.Builds (every module repo already pulls it). The LLM skill handles judgment calls only. **Scope amendment to the brief:** Hexalith.Builds analyzer work is now IN scope (the brief had framework changes out). Every KB convention is tagged `mechanical` or `judgment`; the tag decides which layer owns it. Enforce detects analyzer coverage and skips covered rules.
- **Monoculture countermeasure — KB verified against source.** A hex-absorb capability samples knowledge-base claims and verifies each directly against actual framework source and reference repos — checking the KB against reality, not repos against the KB. The eval suite (skills run against real fixture repos) is the second independent layer. Breaks the circle at its origin.
- **Granularity — six skills, routed capabilities.** hex-create, hex-extend, hex-migrate, hex-enforce, hex-consult, hex-absorb. Each routes internally (hex-extend routes aggregate/command/event/projection/request-handler/UI-page). One trigger surface per job; matrix stays affordable; split later only if a skill gets fat.
- **Platform matrix — Claude Code primary.** Claude Code is the verified, eval-gated platform; Codex/Gemini/Copilot are best-effort conversions from the same skill source via the repo's existing wiring. Evals run on Claude Code only in v1. External-adopter criterion demonstrated on Claude Code.
- **Drain mechanics — provenance ledger + absorb.** Every KB entry records its AI.Tools provenance (file#section). hex-absorb owns the drain capability: once the absorbing skill passes its evals, it generates the deletion PR against Hexalith.AI.Tools and updates the ledger. "Fully drained" becomes a measurable ledger state.
- **Version coupling — module-level pair + KB ranges.** The module declares ONE `targets_framework: >= X.Y` per release; release notes state the pair. KB entries carry since/until framework-version ranges (needed anyway for Migrate's from-state recognition). Enforce's staleness alarm compares declared target vs the repo's actual framework version.
- **Distribution — BMAD installer primary, artifact fallback.** BMAD installer pointed at this public repo IF v6 supports third-party module sources (verify during CM phase); fallback: versioned GitHub release + install script. Release tags carry the framework pair. Submodule pattern rejected (ergonomics tax).

## Build Roadmap

Knowledge-first: the brief warns Migrate needs the fullest KB, and everything reads the KB — so build the writer first, then cheap readers that prove KB quality, then the heavy hitters.

| # | Deliverable | Why this position |
| - | ----------- | ------------------ |
| 1 | **hex-absorb** (incl. KB schema + seed capability) | The only KB writer; its seed capability founds the KB from AI.Tools + framework source. Nothing else can be built honestly without it. |
| 2 | **hex-consult** | Cheapest skill, immediate daily value, and the first real consumer that pressure-tests KB quality. Early gap-filing starts growing the KB. |
| 3 | **Audit core + hex-enforce** (analyzer work starts in parallel, framework-side) | Defines "conformant" operationally. Enforce gates real PRs early — the 3-month criterion needs a long clock, start it now. |
| 4 | **hex-migrate** | Needs the fullest KB and the hardened audit core. The two real migrations (success criterion) happen here. Fleet report rides along. |
| 5 | **hex-extend** | Reuses audit core for verify; patterns hardened by migrations feed its routes. |
| 6 | **hex-create** | Built last — composes everything: extend's routes for seeding, audit core for self-check, hardened conventions throughout. |
| 7 | **Create Module (CM)** scaffold + setup skill + distribution verification | Package it: setup skill (config, tool checks, fleet manifest scaffold), verify BMAD third-party install path, first versioned release with framework pair. |

Eval suites are built WITH each skill, not after — evals gate both release and the corresponding AI.Tools drain step.

**Next steps:**

1. Build each skill using **Build an Agent (BA)** or **Build a Workflow (BW)** — share this plan document as context
2. When all skills are built, return to **Create Module (CM)** to scaffold the module infrastructure

**Next steps:**

1. Build each skill using **Build an Agent (BA)** or **Build a Workflow (BW)** — share this plan document as context
2. When all skills are built, return to **Create Module (CM)** to scaffold the module infrastructure
