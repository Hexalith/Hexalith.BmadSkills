---
title: "BMAD Hexalith Module (Hexalith.BmadSkills)"
status: final
created: 2026-07-13
updated: 2026-07-13
---

# Product Brief: BMAD Hexalith Module

## Executive Summary

The BMAD Hexalith Module is a BMAD v6 module — a peer of bmm and tea — that ships the LLM skills needed to develop and maintain Hexalith technical and domain modules. Installed into any Hexalith module repository or workspace, it turns the framework's coding practices, architectural patterns, and development conventions into executable knowledge that every AI-assisted development session applies by default.

The problem it solves is consistency drift: twenty-odd independently developed modules drift from each other and — more painfully — lag behind a fast-moving framework, because its conventions live only in scattered, aging artifacts and the author's memory.

Why now: Hexalith development is already AI-driven across four agent platforms (Claude Code, Codex, Gemini, GitHub Copilot — this module's repo is wired for all of them), and BMAD v6 provides the module and skill infrastructure to package the method. Every week without a single executable source of conventions, the drift compounds.

## The Problem

Hexalith modules — technical (`eventstore`, `memories`, `frontcomposer`, …) and domain (`tenants`, `parties`, …) — are developed independently, each in its own repository. Two failure modes result:

- **Drift between modules:** the same concern solved differently in sibling repos.
- **Lag behind the framework** (the sharper pain): the framework's conventions evolve release by release — 160+ core releases, still in preview — and existing modules are not brought forward with them.

Today's coping mechanisms are `hexalith-llm-instructions.md` in Hexalith.AI.Tools (descriptive, not executable), the `Hexalith.MyNewModule` template with its PowerShell rename script (covers creation only, and rots), stale documentation, and the author answering the same questions from memory session after session. The cost: migrations are manual, review is memory-bound, and conformance knowledge cannot be handed to anyone — one barrier among several (preview status, stale docs) behind the framework's zero external adopters today. This product removes that barrier; it does not claim to remove the others.

## The Solution

A BMAD module providing skills for four jobs, in order of pain — which is not build order: Migrate needs the fullest knowledge base of the four (old *and* new conventions), and build sequencing belongs to the PRD:

1. **Migrate** — the beating heart. Audit a module against the *current* framework conventions, produce a gap report, and drive the upgrade. This is what keeps twenty repos current with a framework that ships weekly.
2. **Create** — scaffold a new technical or domain module with its per-layer NuGet packages, correct by construction. Supersedes the `Hexalith.MyNewModule` template and its rename script.
3. **Extend** — add an aggregate, command, event, projection, request handler, or UI page to an existing module, conformant by default.
4. **Enforce** — review a change against the conventions and fail it when it drifts; invocable interactively, in CI, and by unattended bmad-loop runs — the loop wiring already present in this module's repo is deliberate.

The skills encode the conventions that define a conformant Hexalith module: EventStore-mandatory CQRS/event sourcing, pure-function aggregates, ULID identifiers, per-layer NuGet packages, Blazor Fluent UI V5 via FrontComposer, xUnit v3 + Shouldly + NSubstitute testing, `.slnx` solutions, Conventional Commits with semantic-release. (Full inventory in the addendum.)

Standing rule, decided: **knowledge added to the BMAD Hexalith Module is removed from Hexalith.AI.Tools.** The drain is itself a scoped deliverable, sequenced so its primary user is never worse-resourced mid-migration: content is deleted from AI.Tools only once the absorbing skill passes its evals — a brief, deliberate overlap instead of a gap. End state: Hexalith.AI.Tools reduced to a pointer to this module.

## Who This Serves

1. **The framework author** (Jérôme) — primary user today; the immediate payoff is session velocity and not having to re-answer solved questions.
2. **The Itaneo team** — developers joining Hexalith work who need to produce conformant code without a year of context.
3. **External Hexalith adopters** — must be able to install this module and produce a conformant Hexalith module with zero tribal knowledge. They are the reason installation, versioning, and documentation are in scope rather than nice-to-haves.

In all three cases the working unit is a human-plus-agent session — and sometimes agent-only (bmad-loop). The agent is as much a user as the human: skills must work headlessly.

## What Makes This Different

The alternatives already tried (see The Problem) share one failure: they describe or scaffold but do not execute, and they rot silently. A BMAD module is versioned, installed from one place, updated in one place, and *does the work* rather than describing it.

There is no technical moat and none is claimed. The actual advantage is structural: the framework and its conventions are owned by the same person building this module, so convention capture is feasible here in a way it rarely is — nothing needs to be reverse-engineered or negotiated.

## Success Criteria

- A new domain module goes from nothing to green build and passing tests in a single session, without consulting anything outside the installed skills.
- At least two real lagging modules are migrated to current conventions via the Migrate skill's audit-and-upgrade flow.
- Hexalith.AI.Tools reaches zero convention content — fully drained.
- Convention questions stop being answered from memory: a session can resolve any conformance question from the skills alone.
- Every shipped skill passes its eval suite before release — "the skill works" is verified by the repo's eval runner, not asserted.
- The Enforce skill gates real pull requests across module repositories — and is still enabled three months later. A gate developers turn off is a failed gate.
- A convention-affecting framework release is reflected in this module within one release cycle — demonstrated at least twice before v1 is declared done.
- One person who is not the author installs the module and produces a conformant Hexalith module without contacting him.

## Scope

**In (v1):** the four skill families targeting the current framework release; recognition of older conventions as migration *from*-states — Migrate cannot compute a gap it cannot recognize; installation into Hexalith module repos and workspaces; the module's own installation and usage documentation; the conventions knowledge base as skill assets; the AI.Tools drain; operation across the four already-wired agent platforms; the meta-drift update ritual, coupled to framework releases — a v1 deliverable, not a parked design.

**Out:** changes to the Hexalith framework itself; general-purpose BMAD improvements; CI infrastructure beyond what invoking Enforce requires; documentation-site generation for the Hexalith framework; old framework versions as migration *targets* — skills bring modules to the current release, and adopters on older releases upgrade first.

## Risks & Open Questions

- **Meta-drift** — the central irony to design against: these skills can lag the framework exactly the way modules did. Countered in v1 by the in-scope update ritual and a staleness alarm — skills declare the framework version they target, and Enforce warns when they lag. The residual risk is the ritual being skipped; the staleness success criterion exists to catch that.
- **Monoculture error** — Migrate writes and Enforce checks from the same knowledge base, so a wrong convention no longer drifts into one repo: it ships to all twenty at machine speed, validated by its own author. The fleet needs at least one check that does not derive from the knowledge base. *Open.*
- **Version coupling** — how a skill version maps to a framework version (pinned pairs? skills declare a minimum?). *Open.*
- **BMAD platform churn** — v6-to-v7 deprecations are already visible in the installed skills; this module inherits that treadmill.
- **Platform matrix** — four agent platforms multiply every skill's verification and maintenance cost by four. Either tier them (one primary, the rest best-effort) or budget the full matrix. *Open.*
- **Bus factor** — capture happens only if the author feeds the module; it reduces dependence on his memory but its upkeep currently depends on him.
- **Distribution mechanics** — how an external adopter actually installs this module (BMAD installer against a public repo? released artifact?). *Open* — and while it is, the external-adopter success criterion cannot be verified. It is also the first domino of the entire adopter path: channel, then version signal, then install docs.
- **Upstream onboarding** — the external-adopter criterion runs through Hexalith's own getting-started path (templates and docs, currently stale), which this module does not fix. A module-development skill set cannot rescue a broken first hour with the framework. *External dependency.*

## Vision

If this works, Hexalith development becomes agent-first: a fleet of modules kept convention-current by unattended bmad-loop runs driving Migrate and Enforce, with humans making design decisions rather than policing conformance. An external adopter gets the framework and its working method as one install — Hexalith stops being a solo project not by hiring, but by making its method executable.
