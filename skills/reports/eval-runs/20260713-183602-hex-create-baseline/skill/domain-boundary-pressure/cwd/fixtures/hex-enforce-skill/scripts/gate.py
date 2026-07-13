#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic operations for the Hexalith conformance gate.

Subcommands:
  rules      Enumerate KB entries (id, tag, since, until, verified, path) split
             into current and superseded, plus an index_drift flag comparing
             index.md against entries/. The audit pre-pass: consume this JSON
             instead of scanning frontmatter by hand.
  waivers    Parse and validate hex-waivers.yaml. Prints JSON: active and
             expired waivers, plus findings that name the file, the problem,
             and the fix. Exit 1 when the file is malformed.
  coverage   Cross the KB's mechanical conventions with the analyzer rules
             manifest. Prints JSON: covered / uncovered convention ids and
             manifest mappings that point at no mechanical KB entry.
             A missing manifest is zero coverage, not an error.
  staleness  Compare the KB's targets_framework floor with the repo's pinned
             Hexalith.* package version (Directory.Packages.props).
  verdict    Validate a findings JSON against the audit-core schema (with --kb,
             reject findings citing convention ids absent from the KB), apply
             waivers, move judgment-layer findings on analyzer-covered ids into
             a surfaced analyzer_owned bucket (with --manifest), attach
             staleness (with --kb and --repo), and settle pass/fail.
             --format annotations emits GitHub workflow commands instead of
             JSON. Exit 0 pass, 1 fail, 2 invalid input.

Waivers file (hex-waivers.yaml at the target repo root) is a constrained flat
list — one 'key: value' per line, no nesting, no inline comments:
  waivers:
    - id: <kb-entry-id>
      reason: <why this deviation is intentional>
      review: <YYYY-MM-DD>

Analyzer manifest (analyzer-rules.json, shipped by Hexalith.Builds):
  {"rules": [{"diagnostic": "HEX0001", "convention": "<kb-entry-id>"}]}
"""

import argparse
import datetime
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_RE = re.compile(r"(\d+(?:\.\d+)*)")
SEVERITIES = {"fail", "warn"}
SCOPES = {"diff", "repo"}
LAYERS = {"judgment", "full"}
WAIVER_FIELDS = ("id", "reason", "review")


def parse_frontmatter(path: Path):
    """Parse flat 'key: value' YAML frontmatter. Returns (fields, error)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if not lines or lines[0].strip() != "---":
        return None, "no frontmatter block (file must start with ---)"
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields, None
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None, f"frontmatter line is not 'key: value': {line!r}"
        fields[key.strip()] = value.strip().strip("'\"")
    return None, "frontmatter block never closed with ---"


def version_key(text: str):
    """Numeric tuple for comparison; prerelease suffixes are ignored."""
    m = VERSION_RE.search(text or "")
    return tuple(int(p) for p in m.group(1).split(".")) if m else None


def load_waivers(path: Path, today: datetime.date):
    """Returns (active, expired, findings). Parser for the constrained format."""
    findings = []

    def add(problem, fix):
        findings.append({"file": str(path), "problem": problem, "fix": fix})

    if not path.is_file():
        return [], [], findings  # absent file: nothing waived, not an error
    entries, current = [], None
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#") or line == "waivers:":
            continue
        if line.startswith("- "):
            current = {}
            entries.append((n, current))
            line = line[2:]
        if current is None:
            add(f"line {n}: entry outside a '- id:' item: {raw!r}", "start each waiver with '- id: <kb-entry-id>'")
            continue
        key, sep, value = line.partition(":")
        if not sep:
            add(f"line {n}: not 'key: value': {raw!r}", "use one 'key: value' per line (see assets/hex-waivers-template.yaml)")
            continue
        current[key.strip()] = value.strip().strip("'\"")
    active, expired = [], []
    for n, w in entries:
        missing = [f for f in WAIVER_FIELDS if not w.get(f)]
        if missing:
            add(f"waiver at line {n}: missing {', '.join(missing)}", "every waiver needs id, reason, review (YYYY-MM-DD)")
            continue
        if not DATE_RE.match(w["review"]):
            add(f"waiver '{w['id']}': review '{w['review']}' is not YYYY-MM-DD", "set review to an ISO date")
            continue
        w = {k: w[k] for k in WAIVER_FIELDS}
        (expired if datetime.date.fromisoformat(w["review"]) < today else active).append(w)
    return active, expired, findings


def kb_entries(kb: Path):
    """All parseable entries as dicts, or None when the KB is unreadable."""
    entries_dir = kb / "entries"
    if not entries_dir.is_dir():
        return None
    out = []
    for path in sorted(entries_dir.glob("*.md")):
        fm, _ = parse_frontmatter(path)
        if fm:
            out.append(
                {
                    "id": fm.get("id", path.stem),
                    "title": fm.get("title", ""),
                    "tag": fm.get("tag", ""),
                    "since": fm.get("since", ""),
                    "until": fm.get("until", ""),
                    "verified": fm.get("verified", ""),
                    "path": str(path),
                }
            )
    return out


def kb_mechanical_ids(kb: Path):
    """Current (until empty) mechanical entry ids, or None when the KB is unreadable."""
    entries = kb_entries(kb)
    if entries is None:
        return None
    return [e["id"] for e in entries if e["tag"] == "mechanical" and not e["until"]]


def cmd_rules(args) -> int:
    entries = kb_entries(Path(args.kb))
    if entries is None:
        print(json.dumps({"ok": False, "error": f"KB entries not found under {args.kb}", "fix": "pass --kb <kb-root>; hex-absorb's seed intent founds the KB"}, indent=2))
        return 1
    index = Path(args.kb) / "index.md"
    all_ids = {e["id"] for e in entries}
    if not index.is_file():
        drift = True
    else:
        listed = set(re.findall(r"^\| ([a-z0-9][a-z0-9-]*) \|", index.read_text(encoding="utf-8"), re.M)) - {"id", "file"}
        drift = listed != all_ids
    print(
        json.dumps(
            {
                "ok": True,
                "current": [e for e in entries if not e["until"]],
                "superseded": [e for e in entries if e["until"]],
                "index_drift": drift,
            },
            indent=2,
        )
    )
    return 0


def cmd_waivers(args) -> int:
    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    active, expired, findings = load_waivers(Path(args.file), today)
    print(json.dumps({"ok": not findings, "active": active, "expired": expired, "findings": findings}, indent=2))
    return 1 if findings else 0


def cmd_coverage(args) -> int:
    mechanical = kb_mechanical_ids(Path(args.kb))
    if mechanical is None:
        print(json.dumps({"ok": False, "error": f"KB entries not found under {args.kb}", "fix": "pass --kb <kb-root>; hex-absorb's seed intent founds the KB"}, indent=2))
        return 1
    manifest_path = Path(args.manifest)
    mapped, unknown = [], []
    manifest_absent = not manifest_path.is_file()
    if not manifest_absent:
        try:
            rules = json.loads(manifest_path.read_text(encoding="utf-8")).get("rules", [])
        except (json.JSONDecodeError, OSError) as exc:
            print(json.dumps({"ok": False, "error": f"manifest unreadable: {exc}", "fix": "analyzer-rules.json must be JSON with a 'rules' array"}, indent=2))
            return 1
        for r in rules:
            conv = r.get("convention", "")
            (mapped if conv in mechanical else unknown).append({"diagnostic": r.get("diagnostic", "?"), "convention": conv})
    covered = sorted({r["convention"] for r in mapped})
    print(
        json.dumps(
            {
                "ok": True,
                "manifest_absent": manifest_absent,
                "mechanical": len(mechanical),
                "covered": covered,
                "uncovered": sorted(set(mechanical) - set(covered)),
                "unknown_mappings": unknown,
            },
            indent=2,
        )
    )
    return 0


def repo_hexalith_version(repo: Path):
    """Highest pinned Hexalith.* package version from Directory.Packages.props."""
    props = repo / "Directory.Packages.props"
    if not props.is_file():
        hits = [p for p in repo.rglob("Directory.Packages.props") if "bin" not in p.parts and "obj" not in p.parts]
        if not hits:
            return None, None
        props = hits[0]
    try:
        root = ET.parse(props).getroot()
    except ET.ParseError:
        return None, str(props)
    versions = [
        pv.get("Version")
        for pv in root.iter("PackageVersion")
        if (pv.get("Include") or "").startswith("Hexalith.") and pv.get("Version")
    ]
    return (max(versions, key=version_key) if versions else None), str(props)


def staleness(kb: Path, repo: Path):
    fm, err = parse_frontmatter(kb / "meta.md") if (kb / "meta.md").is_file() else (None, "meta.md missing")
    target_raw = (fm or {}).get("targets_framework", "")
    repo_version, props = repo_hexalith_version(repo)
    target, actual = version_key(target_raw), version_key(repo_version or "")
    result = {"targets_framework": target_raw or None, "repo_version": repo_version, "packages_props": props}
    if target is None or actual is None:
        result["comparable"] = False
        result["note"] = err or ("no pinned Hexalith.* package found" if repo_version is None else "targets_framework unparseable")
    else:
        pad = max(len(target), len(actual))
        t, a = target + (0,) * (pad - len(target)), actual + (0,) * (pad - len(actual))
        result.update(comparable=True, kb_lags_repo=a > t, repo_lags_target=a < t)
    return result


def cmd_staleness(args) -> int:
    print(json.dumps({"ok": True, **staleness(Path(args.kb), Path(args.repo))}, indent=2))
    return 0


def validate_findings(doc):
    problems = []
    if doc.get("scope") not in SCOPES:
        problems.append("scope must be 'diff' or 'repo'")
    if doc.get("layer") not in LAYERS:
        problems.append("layer must be 'judgment' or 'full'")
    findings = doc.get("findings")
    if not isinstance(findings, list):
        problems.append("findings must be an array (empty is fine)")
        return problems
    for i, f in enumerate(findings):
        where = f"findings[{i}]"
        for field in ("id", "file", "evidence", "explanation"):
            if not isinstance(f.get(field), str) or not f.get(field).strip():
                problems.append(f"{where}: '{field}' missing or empty — an uncited finding is not a finding")
        if f.get("severity") not in SEVERITIES:
            problems.append(f"{where}: severity must be 'fail' or 'warn'")
        if "line" in f and not isinstance(f["line"], int):
            problems.append(f"{where}: line must be an integer")
    return problems


def cmd_verdict(args) -> int:
    try:
        doc = json.loads(Path(args.findings).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"ok": False, "error": f"findings unreadable: {exc}"}, indent=2))
        return 2
    problems = validate_findings(doc)
    if problems:
        print(json.dumps({"ok": False, "error": "findings do not satisfy the audit-core schema", "problems": problems}, indent=2))
        return 2
    if args.kb:
        entries = kb_entries(Path(args.kb))
        if entries is not None:
            known = {e["id"] for e in entries}
            unknown = sorted({f["id"] for f in doc["findings"] if f["id"] not in known})
            if unknown:
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "error": "findings cite convention ids that do not exist in the KB",
                            "problems": [f"unknown convention id '{u}' — cite an existing entry id or file a KB gap instead" for u in unknown],
                        },
                        indent=2,
                    )
                )
                return 2
    if args.manifest and not args.kb:
        print(json.dumps({"ok": False, "error": "--manifest requires --kb", "problems": ["the covered set is manifest conventions ∩ KB mechanical ids; pass --kb <kb-root>"]}, indent=2))
        return 2
    covered = set()
    if args.manifest and Path(args.manifest).is_file():
        try:
            manifest_rules = json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("rules", [])
        except (json.JSONDecodeError, OSError) as exc:
            print(json.dumps({"ok": False, "error": f"manifest unreadable: {exc}", "problems": ["analyzer-rules.json must be JSON with a 'rules' array"]}, indent=2))
            return 2
        covered = {r.get("convention") for r in manifest_rules} & set(kb_mechanical_ids(Path(args.kb)) or [])
    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    active, expired, waiver_findings = load_waivers(Path(args.waivers), today) if args.waivers else ([], [], [])
    if waiver_findings:
        print(json.dumps({"ok": False, "error": "waivers file malformed", "problems": waiver_findings}, indent=2))
        return 2
    by_id = {w["id"]: w for w in active}
    kept, waived, analyzer_owned = [], [], []
    for f in doc["findings"]:
        if doc["layer"] == "judgment" and f["id"] in covered:
            analyzer_owned.append(f)
        elif f["id"] in by_id:
            waived.append({**f, "waiver": by_id[f["id"]]})
        else:
            kept.append(f)
    for w in expired:
        kept.append(
            {
                "id": w["id"],
                "severity": "warn",
                "file": args.waivers,
                "evidence": f"waiver expired {w['review']}: {w['reason']}",
                "explanation": "an expired waiver suppresses nothing — renew it with a new review date or fix the deviation",
            }
        )
    result = {
        "ok": True,
        "verdict": "fail" if any(f["severity"] == "fail" for f in kept) else "pass",
        "scope": doc["scope"],
        "layer": doc["layer"],
        "target": doc.get("target", ""),
        "findings": kept,
        "waived": waived,
        "analyzer_owned": analyzer_owned,
        "expired_waivers": expired,
        "counts": {
            "fail": sum(1 for f in kept if f["severity"] == "fail"),
            "warn": sum(1 for f in kept if f["severity"] == "warn"),
            "waived": len(waived),
            "analyzer_owned": len(analyzer_owned),
        },
    }
    if args.kb and args.repo:
        result["staleness"] = staleness(Path(args.kb), Path(args.repo))
    if args.format == "annotations":
        for f in kept:
            level = "error" if f["severity"] == "fail" else "warning"
            location = f"file={f['file']}" + (f",line={f['line']}" if isinstance(f.get("line"), int) else "")
            print(f"::{level} {location},title=hex-enforce {f['id']}::{f['explanation']}")
    else:
        print(json.dumps(result, indent=2))
    return 1 if result["verdict"] == "fail" else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("rules", help="enumerate KB entries and detect index drift")
    p.add_argument("--kb", default="_bmad/hex/knowledge", help="KB root (default: _bmad/hex/knowledge under the cwd)")
    p.set_defaults(func=cmd_rules)

    p = sub.add_parser("waivers", help="parse and validate a hex-waivers.yaml")
    p.add_argument("--file", required=True, help="path to hex-waivers.yaml")
    p.add_argument("--today", help="override today (YYYY-MM-DD) for reproducible runs")
    p.set_defaults(func=cmd_waivers)

    p = sub.add_parser("coverage", help="cross KB mechanical rules with the analyzer manifest")
    p.add_argument("--kb", default="_bmad/hex/knowledge", help="KB root (default: _bmad/hex/knowledge under the cwd)")
    p.add_argument("--manifest", required=True, help="path to analyzer-rules.json (may not exist yet)")
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("staleness", help="compare KB targets_framework with the repo's Hexalith version")
    p.add_argument("--kb", default="_bmad/hex/knowledge", help="KB root")
    p.add_argument("--repo", required=True, help="target repo root")
    p.set_defaults(func=cmd_staleness)

    p = sub.add_parser("verdict", help="validate findings, apply waivers, settle pass/fail")
    p.add_argument("--findings", required=True, help="findings JSON per the audit-core schema")
    p.add_argument("--waivers", help="path to hex-waivers.yaml (optional)")
    p.add_argument("--kb", help="KB root — rejects unknown convention ids; with --repo, attaches the staleness check")
    p.add_argument("--repo", help="target repo root")
    p.add_argument("--manifest", help="analyzer-rules.json — judgment-layer findings on covered ids move to analyzer_owned (requires --kb)")
    p.add_argument("--format", choices=["json", "annotations"], default="json", help="annotations = GitHub workflow commands")
    p.add_argument("--today", help="override today (YYYY-MM-DD) for reproducible runs")
    p.set_defaults(func=cmd_verdict)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
