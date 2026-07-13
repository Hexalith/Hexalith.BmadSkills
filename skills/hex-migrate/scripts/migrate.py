#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""hex-migrate deterministic core.

Subcommands:
  tiers   validate finding tiers in a settled verdict against KB tags (input: gate.py rules output)
  report  render a settled tiered verdict as a gap report (HTML + machine-readable JSON beside it)
  fleet   aggregate a directory of settled tiered verdicts into a fleet report (HTML + JSON)

The settled verdict is gate.py verdict's output (hex-enforce skill); hex-migrate adds a
`tier` field per finding: mechanical | structural | judgment.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

TIERS = ("mechanical", "structural", "judgment")


def load_json(path: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"{path}: {exc}"


def is_settled_verdict(doc) -> bool:
    return isinstance(doc, dict) and "verdict" in doc and isinstance(doc.get("findings"), list)


def validate_tiers(verdict: dict, rules: dict):
    """Problems (empty = valid) and failing-finding counts per tier."""
    tag_by_id = {e["id"]: e.get("tag", "") for e in rules.get("current", []) + rules.get("superseded", [])}
    problems, counts = [], {t: 0 for t in TIERS}
    for i, f in enumerate(verdict.get("findings", [])):
        where = f"findings[{i}] ({f.get('id', '?')})"
        tier = f.get("tier")
        if tier is None:
            if f.get("severity") == "fail":
                problems.append(f"{where}: failing finding carries no tier — add mechanical | structural | judgment")
            continue
        if tier not in TIERS:
            problems.append(f"{where}: unknown tier '{tier}' — use mechanical | structural | judgment")
            continue
        tag = tag_by_id.get(f.get("id"))
        if tag is None:
            problems.append(f"{where}: convention id not in the rules output — settle with gate.py verdict --kb before tiering")
        elif tag == "judgment" and tier != "judgment":
            problems.append(f"{where}: '{f['id']}' is judgment-tagged; its tier must be judgment — a machine must not settle a human call")
        elif tag == "mechanical" and tier == "judgment":
            problems.append(f"{where}: '{f['id']}' is mechanical-tagged; use mechanical or structural — intentional deviations are waived, not escalated")
        elif f.get("severity") == "fail":
            counts[tier] += 1
    return problems, counts


def cmd_tiers(args) -> int:
    verdict, err = load_json(args.verdict)
    if err or not is_settled_verdict(verdict):
        print(json.dumps({"ok": False, "error": err or f"{args.verdict} is not a settled verdict", "fix": "settle findings with gate.py verdict first"}, indent=2))
        return 2
    rules, err = load_json(args.rules)
    if err or not isinstance(rules, dict) or "current" not in rules:
        print(json.dumps({"ok": False, "error": err or f"{args.rules} is not a rules listing", "fix": "produce it with gate.py rules --kb <kb-root>"}, indent=2))
        return 2
    problems, counts = validate_tiers(verdict, rules)
    print(json.dumps({"ok": not problems, "problems": problems, "counts": counts}, indent=2))
    return 2 if problems else 0


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "repo"


def staleness_phrase(s) -> str:
    if not isinstance(s, dict):
        return "not checked"
    if not s.get("comparable"):
        return s.get("note") or "not comparable"
    if s.get("repo_lags_target"):
        return f"repo {s.get('repo_version')} lags KB target {s.get('targets_framework')} — migrate"
    if s.get("kb_lags_repo"):
        return f"KB target {s.get('targets_framework')} lags repo {s.get('repo_version')} — run hex-absorb"
    return "current"


CSS = """
:root { --bg:#fff; --fg:#1a1a1a; --muted:#666; --line:#ddd; --code:#f5f5f5;
        --fail:#b3261e; --warn:#9a6a00; --ok:#1a7f37; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#161616; --fg:#e6e6e6; --muted:#999; --line:#333; --code:#242424;
          --fail:#ff6b61; --warn:#e0a800; --ok:#4cc38a; } }
body { font: 15px/1.5 system-ui, sans-serif; color: var(--fg); background: var(--bg);
       max-width: 72rem; margin: 2rem auto; padding: 0 1rem; }
h1 { font-size: 1.4rem; } h2 { font-size: 1.1rem; margin-top: 2rem; }
table { border-collapse: collapse; width: 100%; margin: .5rem 0 1rem; }
th, td { border: 1px solid var(--line); padding: .4rem .6rem; text-align: left;
         vertical-align: top; }
th { background: var(--code); }
code { background: var(--code); padding: .1rem .3rem; border-radius: 3px;
       font-size: .9em; white-space: pre-wrap; word-break: break-word; }
.muted { color: var(--muted); }
.badge { display: inline-block; padding: .1rem .5rem; border-radius: 1rem;
         font-weight: 600; }
.fail { color: var(--fail); } .warn { color: var(--warn); } .pass { color: var(--ok); }
"""


def page(title: str, body: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>{html.escape(title)}</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n{body}\n"
        "<p class=\"muted\">Generated by hex-migrate.</p>\n</body>\n</html>\n"
    )


def findings_table(findings) -> str:
    rows = []
    for f in findings:
        location = html.escape(f.get("file", ""))
        if isinstance(f.get("line"), int):
            location += f":{f['line']}"
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(f.get('id', ''))}</code></td>"
            f"<td class=\"{html.escape(f.get('severity', ''))}\">{html.escape(f.get('severity', ''))}</td>"
            f"<td>{location}</td>"
            f"<td><code>{html.escape(f.get('evidence', ''))}</code></td>"
            f"<td>{html.escape(f.get('explanation', ''))}</td>"
            "</tr>"
        )
    return (
        "<table><tr><th>convention</th><th>severity</th><th>location</th><th>evidence</th><th>explanation</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def cmd_report(args) -> int:
    doc, err = load_json(args.verdict)
    if err or not is_settled_verdict(doc):
        print(json.dumps({"ok": False, "error": err or f"{args.verdict} is not a settled verdict", "fix": "settle findings with gate.py verdict first"}, indent=2))
        return 2
    untiered = [f.get("id", "?") for f in doc["findings"] if f.get("severity") == "fail" and f.get("tier") not in TIERS]
    if untiered:
        print(json.dumps({"ok": False, "error": "failing findings without a valid tier", "problems": untiered, "fix": "tier every failing finding and validate with migrate.py tiers"}, indent=2))
        return 2
    today = args.today or datetime.date.today().isoformat()
    slug = slugify(Path(doc.get("target") or "repo").name)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html_path, json_path = out / f"gap-report-{slug}-{today}.html", out / f"gap-report-{slug}-{today}.json"

    counts = Counter(f["tier"] for f in doc["findings"] if f.get("severity") == "fail")
    verdict = doc.get("verdict", "")
    body = [f"<h1>Hexalith gap report — {html.escape(doc.get('target', ''))}</h1>"]
    body.append(
        f"<p><span class=\"badge {html.escape(verdict)}\">{html.escape(verdict)}</span> · {today} · scope {html.escape(str(doc.get('scope', '')))}, "
        f"layer {html.escape(str(doc.get('layer', '')))} · gaps: {counts.get('mechanical', 0)} mechanical, {counts.get('structural', 0)} structural, "
        f"{counts.get('judgment', 0)} judgment · waived: {len(doc.get('waived', []))} · staleness: {html.escape(staleness_phrase(doc.get('staleness')))}</p>"
    )
    tier_blurb = {
        "mechanical": "safe, local, deterministic fixes — auto-applied by drive (including headless)",
        "structural": "reshapes files or projects — applied only from an approved plan",
        "judgment": "the KB marks these a human call — never auto-fixed",
    }
    for tier in TIERS:
        tiered = [f for f in doc["findings"] if f.get("tier") == tier]
        if tiered:
            body.append(f"<h2>{tier.capitalize()} ({len(tiered)})</h2><p class=\"muted\">{tier_blurb[tier]}</p>")
            body.append(findings_table(tiered))
    untiered_warns = [f for f in doc["findings"] if f.get("tier") not in TIERS]
    if untiered_warns:
        body.append(f"<h2>Advisories ({len(untiered_warns)})</h2>")
        body.append(findings_table(untiered_warns))
    if doc.get("waived"):
        body.append(f"<h2>Waived ({len(doc['waived'])})</h2><table><tr><th>convention</th><th>reason</th><th>review</th></tr>")
        for w in doc["waived"]:
            waiver = w.get("waiver", {})
            body.append(
                f"<tr><td><code>{html.escape(w.get('id', ''))}</code></td><td>{html.escape(str(waiver.get('reason', '')))}</td>"
                f"<td>{html.escape(str(waiver.get('review', '')))}</td></tr>"
            )
        body.append("</table>")
    if doc.get("analyzer_owned"):
        body.append(f"<h2>Analyzer-owned ({len(doc['analyzer_owned'])})</h2>")
        body.append(findings_table(doc["analyzer_owned"]))

    html_path.write_text(page(f"Gap report — {doc.get('target', '')}", "\n".join(body)), encoding="utf-8")
    json_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "html": str(html_path), "json": str(json_path), "verdict": verdict, "counts": {t: counts.get(t, 0) for t in TIERS}}, indent=2))
    return 0


def cmd_fleet(args) -> int:
    files = sorted(Path(args.dir).glob("*.json"))
    if not files:
        print(json.dumps({"ok": False, "error": f"no *.json verdicts under {args.dir}", "fix": "write each repo's settled tiered verdict into that directory first"}, indent=2))
        return 2
    rows, hot = [], Counter()
    for path in files:
        doc, err = load_json(str(path))
        if err or not is_settled_verdict(doc):
            print(json.dumps({"ok": False, "error": err or f"{path} is not a settled verdict", "fix": "every file in the directory must be gate.py verdict output (plus tiers); move anything else out"}, indent=2))
            return 2
        fails = [f for f in doc["findings"] if f.get("severity") == "fail"]
        tiers = Counter(f.get("tier") for f in fails)
        for cid in {f.get("id") for f in fails}:
            hot[cid] += 1
        rows.append(
            {
                "repo": Path(doc.get("target") or path.stem).name,
                "verdict": doc.get("verdict", ""),
                "mechanical": tiers.get("mechanical", 0),
                "structural": tiers.get("structural", 0),
                "judgment": tiers.get("judgment", 0),
                "warn": sum(1 for f in doc["findings"] if f.get("severity") == "warn"),
                "waived": len(doc.get("waived", [])),
                "staleness": staleness_phrase(doc.get("staleness")),
            }
        )
    today = args.today or datetime.date.today().isoformat()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    html_path, json_path = out / f"fleet-report-{today}.html", out / f"fleet-report-{today}.json"
    hot_spots = [{"id": cid, "repos": n} for cid, n in hot.most_common()]
    result = {
        "generated": today,
        "repos": rows,
        "hot_spots": hot_spots,
        "totals": {
            "repos": len(rows),
            "failing_repos": sum(1 for r in rows if r["verdict"] == "fail"),
            "gaps": sum(r["mechanical"] + r["structural"] + r["judgment"] for r in rows),
            "waived": sum(r["waived"] for r in rows),
        },
    }
    body = [f"<h1>Hexalith fleet conformance report</h1>"]
    t = result["totals"]
    body.append(f"<p>{today} · {t['repos']} repos, {t['failing_repos']} failing · {t['gaps']} gaps · {t['waived']} waived</p>")
    body.append("<h2>Repos</h2><table><tr><th>repo</th><th>verdict</th><th>mechanical</th><th>structural</th><th>judgment</th><th>warn</th><th>waived</th><th>staleness</th></tr>")
    for r in rows:
        body.append(
            f"<tr><td>{html.escape(r['repo'])}</td><td class=\"{html.escape(r['verdict'])}\">{html.escape(r['verdict'])}</td>"
            f"<td>{r['mechanical']}</td><td>{r['structural']}</td><td>{r['judgment']}</td><td>{r['warn']}</td><td>{r['waived']}</td>"
            f"<td>{html.escape(r['staleness'])}</td></tr>"
        )
    body.append("</table>")
    body.append("<h2>Drift hot-spots</h2><p class=\"muted\">Conventions failing across repos — fix the framework-wide cause once, not per repo.</p>")
    body.append("<table><tr><th>convention</th><th>failing repos</th></tr>")
    for h in hot_spots:
        body.append(f"<tr><td><code>{html.escape(str(h['id']))}</code></td><td>{h['repos']}</td></tr>")
    body.append("</table>")
    html_path.write_text(page("Hexalith fleet conformance report", "\n".join(body)), encoding="utf-8")
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "html": str(html_path), "json": str(json_path), "totals": result["totals"]}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("tiers", help="validate finding tiers against KB tags")
    p.add_argument("--verdict", required=True, help="settled verdict JSON (gate.py verdict output, tier added per finding)")
    p.add_argument("--rules", required=True, help="rules JSON (gate.py rules output)")
    p.set_defaults(func=cmd_tiers)

    p = sub.add_parser("report", help="render a settled tiered verdict as a gap report")
    p.add_argument("--verdict", required=True, help="settled tiered verdict JSON")
    p.add_argument("--out", required=True, help="directory the HTML + JSON report pair is written to")
    p.add_argument("--today", help="override today's date (YYYY-MM-DD), for reproducible output")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("fleet", help="aggregate settled per-repo verdicts into a fleet report")
    p.add_argument("--dir", required=True, help="directory holding one settled tiered verdict JSON per repo")
    p.add_argument("--out", required=True, help="directory the HTML + JSON report pair is written to")
    p.add_argument("--today", help="override today's date (YYYY-MM-DD), for reproducible output")
    p.set_defaults(func=cmd_fleet)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
