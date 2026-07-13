# Audit Core

The one place "conformant" is defined operationally for Hexalith modules. Three consumers run it: hex-enforce (diff-scoped, judgment layer), hex-migrate (repo-wide, full KB including superseded from-states), and the fleet report (repo-wide per manifest repo, aggregated). Fix an audit bug here and every consumer inherits the fix. This file stands alone — do not assume any other skill file is loaded. Converse in `{communication_language}`; write finding evidence, explanations, and narrative reports in `{document_output_language}`.

An audit run is parameterized by two axes; the invoking skill states both:

- **scope** — `diff` (only the changed lines and the code they touch) or `repo` (every source file).
- **layer** — `judgment` (skip mechanical rules the analyzer covers; hex-enforce's default) or `full` (every applicable rule; hex-migrate's default — a lagging repo's analyzer lags too, so nothing is presumed covered).

## Inputs

| Input | Where | Absent means |
| --- | --- | --- |
| KB | `{project-root}/_bmad/hex/knowledge/` — an explicit KB path in the invocation overrides it | Blocked. There is no auditing without the KB; hex-absorb's seed intent founds it. |
| Target | the repo (repo scope) or a diff plus its repo (diff scope) | Blocked — nothing to audit. |
| Waivers | `hex-waivers.yaml` at the target repo root | Nothing is waived. |
| Coverage manifest | `analyzer-rules.json` at the target repo root or inside its `Hexalith.Builds/` submodule — JSON `{"rules": [{"diagnostic": "HEX0001", "convention": "<kb-entry-id>"}]}`, shipped by Hexalith.Builds | Zero analyzer coverage: every mechanical rule falls to the LLM layer and the verdict names the manifest as missing. |

## Procedure

1. **Select the applicable rules.** Run `uv run scripts/gate.py rules --kb <kb-root>` (from the hex-enforce skill directory) — it returns every entry's id/tag/since/until plus an `index_drift` flag (when drifted, note it in the run summary; hex-absorb regenerates the index). Open Statement bodies only for the rules the target can touch. Current entries (`until` empty) always apply. Superseded entries apply only under `full` layer with repo scope — they are from-states for recognizing what version of a convention the code follows, never grounds for a finding on their own.
2. **Assign each rule to its layer.** Run `uv run scripts/gate.py coverage --kb <kb-root> --manifest <path>`. Under `judgment` layer, skip the covered mechanical ids — the analyzer already fails the build on those, and double-reporting erodes trust in both layers (step 5 re-enforces this skip deterministically). Uncovered mechanical rules are yours in every layer: a rule nobody checks is not a rule. Judgment rules are always yours.
3. **Examine the target.** Diff scope: read the diff, then read enough surrounding code to judge what the diff touches — a conformant-looking hunk can violate a convention only visible in the file it lands in. Repo scope: sweep the source tree; skip generated code (`obj/`, `bin/`, `*.g.cs`).
4. **Write findings.** A finding exists only when you can state all four: the convention id, the file and line, the offending code (evidence), and why it violates the Statement. Anything less is not a finding — if the KB is ambiguous or silent on something that looks wrong, file a gap to the KB's `intake/` (frontmatter `source: enforce`, `filed: <YYYY-MM-DD>`, `status: open`) instead of rejecting. Severity: `fail` for a violated convention, `warn` for advisory signals (coverage gaps, staleness, expired waivers).
5. **Settle the verdict deterministically.** Emit the findings JSON below, then run `uv run scripts/gate.py verdict --findings <file> --waivers <path> --kb <kb-root> --repo <path> --manifest <path>`. The script validates the schema (an uncited finding is rejected, not shipped; a finding citing an id absent from the KB is rejected), applies waivers, moves judgment-layer findings on analyzer-covered ids into the surfaced `analyzer_owned` bucket, appends the staleness check, and computes the verdict and exit code. Never apply waivers or settle pass/fail by hand while the script is available.

## Findings JSON — the machine contract

What the auditing model produces (input to `gate.py verdict`). hex-migrate's gap report is this same shape with a `tier` field added per finding (`mechanical | structural | judgment`); the fleet aggregator consumes the settled verdicts.

```json
{
  "scope": "diff | repo",
  "layer": "judgment | full",
  "target": "<repo path or PR ref>",
  "findings": [
    {
      "id": "<kb-entry-id>",
      "severity": "fail | warn",
      "file": "src/Example/Thing.cs",
      "line": 42,
      "evidence": "<the offending code, quoted>",
      "explanation": "<why this violates the convention's Statement>"
    }
  ]
}
```

The settled verdict adds: `verdict` (pass|fail), `waived` (findings suppressed by an active waiver, with the waiver's reason and review date — surfaced, never silent), `analyzer_owned` (judgment-layer findings on analyzer-covered ids — the analyzer's to report, listed so the skip is visible), `expired_waivers` (each becomes a `warn` finding: renew or fix), `staleness`, and `counts`. `verdict` is `fail` when any unwaived `fail` finding remains.

## Waivers

`hex-waivers.yaml` at the target repo root — one entry per intentional deviation: `id` (the convention id), `reason`, `review` (YYYY-MM-DD). Parsed by `gate.py waivers`; format template in the hex-enforce skill's `assets/hex-waivers-template.yaml`. An active waiver suppresses matching findings but stays visible in the verdict. A waiver past its review date suppresses nothing and surfaces as its own `warn` finding — waivers age out; they do not accumulate.

## Staleness

Every verdict carries the version check: the KB's `targets_framework` floor against the repo's pinned `Hexalith.*` package version (`Directory.Packages.props`). Repo above the floor → the KB may not have absorbed recent releases (warn: run hex-absorb). Repo below the floor → the repo lags the conventions (warn: run hex-migrate). `gate.py staleness` computes it; `gate.py verdict` attaches it when given `--kb` and `--repo`.
