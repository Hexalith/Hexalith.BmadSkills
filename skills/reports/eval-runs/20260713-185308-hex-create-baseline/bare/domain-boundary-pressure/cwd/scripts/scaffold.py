#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Deterministic operations for scaffolding a Hexalith module repo.

Standing in for hex-create's own scaffold.py (not installed here). Mirrors
gate.py's philosophy: the boundary decision and the structural check are made
by a script, not eyeballed, so they are reproducible and machine-checked.

Subcommands:
  plan    Given a module name, type, target dir, and requested extra project
          layers, emit the minimal skeleton (module-skeleton-structure) and
          test which requested extras violate module-boundary-domain-only for
          a 'domain' type module. Excluded requests are never silently
          dropped -- they come back in the 'excluded' list with a citation.
          Writes no files.
  verify  Walk an already-scaffolded target dir and check it against the
          KB's mechanical conventions (module-skeleton-structure,
          central-package-management) plus the domain-only boundary
          (module-boundary-domain-only) by project-name pattern. Prints a
          gaps list; exit 0 when empty, 1 otherwise.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Project-name substrings that indicate hosting/persistence/infrastructure --
# out of bounds for a 'domain' type module per module-boundary-domain-only.
DOMAIN_ONLY_EXCLUDE_PATTERNS = (
    "apiserver", "apphost", "aspire", "host", "web", "worker",
    "function", "infrastructure", "persistence", "dbcontext", "repository",
)


def parse_frontmatter(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


def kb_entries(kb: Path):
    entries_dir = kb / "entries"
    if not entries_dir.is_dir():
        return None
    out = []
    for path in sorted(entries_dir.glob("*.md")):
        fm = parse_frontmatter(path)
        if fm:
            out.append({"id": fm.get("id", path.stem), "tag": fm.get("tag", ""), "until": fm.get("until", "")})
    return out


def cmd_plan(args) -> int:
    kb = Path(args.kb)
    entries = kb_entries(kb)
    if entries is None:
        print(json.dumps({"ok": False, "error": f"KB entries not found under {args.kb}"}, indent=2))
        return 1
    known_ids = {e["id"] for e in entries}
    module = args.module

    minimal = [
        {"name": f"{module}.Domain", "kind": "src", "path": f"src/{module}.Domain/{module}.Domain.csproj"},
        {"name": f"{module}.Domain.Tests", "kind": "test", "path": f"test/{module}.Domain.Tests/{module}.Domain.Tests.csproj"},
    ]

    excluded, included_extra = [], []
    for requested in args.include:
        low = requested.lower()
        if args.type == "domain" and any(p in low for p in DOMAIN_ONLY_EXCLUDE_PATTERNS):
            citation = "module-boundary-domain-only"
            excluded.append(
                {
                    "requested": requested,
                    "reason": "a domain module carries aggregates, commands, events, projections, and request "
                    "handlers only -- no AppHost, no Aspire wiring, no persistence infrastructure; hosting "
                    "comes from Hexalith.EventStore's domain-service SDK, not a project in this repo",
                    "citation": citation,
                    "citation_known": citation in known_ids,
                }
            )
        else:
            included_extra.append(requested)

    plan = {
        "ok": True,
        "module": module,
        "type": args.type,
        "target": args.target,
        "kb": args.kb,
        "projects": minimal + [
            {"name": f"{module}.{ex}", "kind": "src", "path": f"src/{module}.{ex}/{module}.{ex}.csproj"}
            for ex in included_extra
        ],
        "excluded": excluded,
        "constraints": ["module-boundary-domain-only applies: type=domain modules get the Domain/Domain.Tests pair only"],
    }
    print(json.dumps(plan, indent=2))
    return 0


def gap(gaps, rule, detail):
    gaps.append({"rule": rule, "detail": detail})


def cmd_verify(args) -> int:
    target = Path(args.target)
    gaps = []

    slnx_candidates = list(target.glob("*.slnx"))
    if len(slnx_candidates) != 1:
        gap(gaps, "module-skeleton-structure", f"expected exactly one {{Module}}.slnx at {target}, found {len(slnx_candidates)}")
        print(json.dumps({"ok": False, "gaps": gaps}, indent=2))
        return 1
    slnx = slnx_candidates[0]
    module = slnx.stem

    try:
        root = ET.parse(slnx).getroot()
        listed = {p.get("Path") for p in root.iter("Project") if p.get("Path")}
    except ET.ParseError as exc:
        gap(gaps, "module-skeleton-structure", f"{slnx} is not well-formed XML: {exc}")
        listed = set()

    on_disk = sorted(
        str(p.relative_to(target))
        for p in list(target.glob("src/*/*.csproj")) + list(target.glob("test/*/*.csproj"))
    )

    for path in on_disk:
        if path not in listed:
            gap(gaps, "module-skeleton-structure", f"{path} exists on disk but is absent from {slnx.name}")
    for path in listed:
        if path not in on_disk:
            gap(gaps, "module-skeleton-structure", f"{path} is listed in {slnx.name} but absent on disk")

    for rel in on_disk:
        csproj = target / rel
        try:
            croot = ET.parse(csproj).getroot()
        except ET.ParseError as exc:
            gap(gaps, "module-skeleton-structure", f"{rel} is not well-formed XML: {exc}")
            continue
        props = {}
        for pg in croot.findall("PropertyGroup"):
            for child in pg:
                props[child.tag] = (child.text or "").strip()
        if props.get("TargetFramework") != "net10.0":
            gap(gaps, "module-skeleton-structure", f"{rel}: TargetFramework is {props.get('TargetFramework')!r}, expected 'net10.0'")
        if props.get("ImplicitUsings") != "enable":
            gap(gaps, "module-skeleton-structure", f"{rel}: ImplicitUsings is {props.get('ImplicitUsings')!r}, expected 'enable'")
        if props.get("Nullable") != "enable":
            gap(gaps, "module-skeleton-structure", f"{rel}: Nullable is {props.get('Nullable')!r}, expected 'enable'")

        is_test = rel.startswith("test" + "/")
        refs = [pr.get("Include", "") for pr in croot.iter("ProjectReference")]
        if is_test and not refs:
            gap(gaps, "module-skeleton-structure", f"{rel}: test project has no ProjectReference to the project under test")

        for pr in croot.iter("PackageReference"):
            if pr.get("Version"):
                gap(gaps, "central-package-management", f"{rel}: <PackageReference Include=\"{pr.get('Include')}\" Version=...> pins a version inline; versions belong only in Directory.Packages.props")

        if args.type == "domain" and rel.startswith("src" + "/"):
            proj_name = Path(rel).stem.lower()
            hit = next((p for p in DOMAIN_ONLY_EXCLUDE_PATTERNS if p in proj_name), None)
            if hit:
                gap(gaps, "module-boundary-domain-only", f"{rel}: project name matches hosting/infrastructure pattern {hit!r} inside a domain-only module")

    props_path = target / "Directory.Packages.props"
    if not props_path.is_file():
        gap(gaps, "central-package-management", f"{props_path} is missing")
    else:
        try:
            proot = ET.parse(props_path).getroot()
            managed = None
            for pg in proot.findall("PropertyGroup"):
                for child in pg:
                    if child.tag == "ManagePackageVersionsCentrally":
                        managed = (child.text or "").strip()
            if managed != "true":
                gap(gaps, "central-package-management", f"{props_path}: ManagePackageVersionsCentrally is {managed!r}, expected 'true'")
        except ET.ParseError as exc:
            gap(gaps, "central-package-management", f"{props_path} is not well-formed XML: {exc}")

    gitignore = target / ".gitignore"
    if not gitignore.is_file():
        gap(gaps, "module-skeleton-structure", f"{gitignore} is missing")
    else:
        text = gitignore.read_text(encoding="utf-8")
        for needed in ("bin/", "obj/"):
            if needed not in text:
                gap(gaps, "module-skeleton-structure", f"{gitignore} does not cover {needed}")

    print(json.dumps({"ok": not gaps, "module": module, "target": str(target), "gaps": gaps}, indent=2))
    return 1 if gaps else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="declare the module skeleton and any boundary exclusions")
    p.add_argument("--module", required=True)
    p.add_argument("--type", default="domain", choices=["domain"])
    p.add_argument("--target", required=True)
    p.add_argument("--kb", required=True)
    p.add_argument("--include", action="append", default=[], help="extra requested project layer, e.g. ApiServer (repeatable)")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("verify", help="check a scaffolded target dir against the KB's mechanical rules")
    p.add_argument("--target", required=True)
    p.add_argument("--kb", required=True)
    p.add_argument("--type", default="domain", choices=["domain"])
    p.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
