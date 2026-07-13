#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""scaffold — deterministic checks for hex-create's plan-validate-execute flow.

Two subcommands, each reading a scaffold plan JSON and printing one line of JSON:

  plan   --file <plan.json>   Validate the plan before anything is generated:
                              schema, name legality, internal consistency,
                              declared constraints, and that the target
                              directory is empty or absent.
  verify --file <plan.json>   Check the scaffolded result for completeness:
                              every planned project and file exists on disk,
                              no unplanned .csproj hides on disk outside the
                              plan, the solution references exactly the planned
                              project set, and no on-disk path violates a
                              declared constraint. A green build cannot catch
                              a planned-but-never-created project or a stray
                              never-referenced one; this can. Also emits
                              files_present — a machine count of files under
                              target — so callers never hand-tally.

Plan schema (all paths relative to `target`, forward slashes):

  {
    "module":    "Inventory",                  # letters/digits/dots/underscores,
                                               # starts with a letter
    "type":      "technical" | "domain",
    "target":    "out/Inventory",              # resolved against the cwd
    "solution":  "Inventory.slnx",             # .slnx only (what verify parses)
    "projects":  [{"path": "src/Inventory.Domain/Inventory.Domain.csproj",
                   "role": "src" | "test"}],
    "files":     ["Directory.Packages.props", ".gitignore"],       # optional
    "constraints": {"forbidden_path_patterns": ["src/*.ApiServer*"]},  # optional,
                                               # KB-derived, fnmatch syntax
    "citations": ["module-skeleton-structure"] # KB entry ids the plan is built from
  }

The script is convention-free by design: rules live in the KB and travel inside
the plan as citations and declared constraints; this script only enforces what
the plan itself declares. Exit codes: 0 ok, 1 findings, 2 usage/plan unreadable.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

MODULE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._]*$")
VALID_TYPES = {"technical", "domain"}
VALID_ROLES = {"src", "test"}
SKIP_DIRS = {".git", "bin", "obj"}


def _emit(payload: dict, exit_code: int) -> int:
    print(json.dumps(payload, separators=(", ", ": ")))
    return exit_code


def _rel_path_errors(raw: str, label: str) -> list[str]:
    """Path-shape checks shared by solution, project, and file entries."""
    errors = []
    if not isinstance(raw, str) or not raw.strip():
        return [f"{label} path is empty — give a path relative to target"]
    p = PurePosixPath(raw)
    if "\\" in raw:
        errors.append(f"{label} '{raw}' uses backslashes — use forward slashes")
    if p.is_absolute() or (len(raw) > 1 and raw[1] == ":"):
        errors.append(f"{label} '{raw}' is absolute — use a path relative to target")
    if ".." in p.parts:
        errors.append(f"{label} '{raw}' escapes target via '..' — keep it inside target")
    return errors


def load_plan(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_schema(plan: dict) -> list[str]:
    """Everything checkable without touching the filesystem."""
    errors = []

    module = plan.get("module")
    if not isinstance(module, str) or not MODULE_NAME_RE.match(module or "") or module.endswith("."):
        errors.append(
            f"module name {module!r} is not filesystem/msbuild-safe — use letters, "
            "digits, dots, or underscores, starting with a letter, not ending with a dot"
        )

    if plan.get("type") not in VALID_TYPES:
        errors.append(f"type {plan.get('type')!r} is not one of {sorted(VALID_TYPES)}")

    target = plan.get("target")
    if not isinstance(target, str) or not target.strip():
        errors.append("target is missing — name the directory to scaffold into")

    solution = plan.get("solution")
    errors += _rel_path_errors(solution, "solution")
    if isinstance(solution, str) and solution.strip() and not solution.endswith(".slnx"):
        errors.append(f"solution '{solution}' is not a .slnx file — verify can only parse .slnx")

    projects = plan.get("projects")
    if not isinstance(projects, list) or not projects:
        errors.append("projects is empty — a scaffold plan must plan at least one project")
        projects = []
    seen: set[str] = set()
    for entry in projects:
        if not isinstance(entry, dict):
            errors.append(f"project entry {entry!r} is not an object with 'path' and 'role'")
            continue
        p = entry.get("path", "")
        errors += _rel_path_errors(p, "project")
        if isinstance(p, str) and p and not p.endswith(".csproj"):
            errors.append(f"project '{p}' does not end in .csproj")
        if p in seen:
            errors.append(f"project '{p}' is planned twice — remove the duplicate")
        seen.add(p)
        if entry.get("role") not in VALID_ROLES:
            errors.append(f"project '{p}' role {entry.get('role')!r} is not one of {sorted(VALID_ROLES)}")

    files = plan.get("files", [])
    if not isinstance(files, list):
        errors.append("files must be a list of paths relative to target")
        files = []
    seen_files: set[str] = set()
    for f in files:
        errors += _rel_path_errors(f, "file")
        if f in seen_files:
            errors.append(f"file '{f}' is planned twice — remove the duplicate")
        if f in seen:
            errors.append(f"file '{f}' is already planned as a project — remove one")
        seen_files.add(f)

    citations = plan.get("citations")
    if not isinstance(citations, list) or not citations or not all(
        isinstance(c, str) and c.strip() for c in citations
    ):
        errors.append(
            "plan cites no KB entries — every scaffold shape must come from a cited "
            "convention; fill 'citations' with the KB entry ids the plan is built from"
        )

    patterns = (plan.get("constraints") or {}).get("forbidden_path_patterns", [])
    if not isinstance(patterns, list) or not all(isinstance(x, str) for x in patterns):
        errors.append("constraints.forbidden_path_patterns must be a list of fnmatch patterns")
        patterns = []
    for pattern in patterns:
        for p in list(seen) + list(seen_files) + ([solution] if isinstance(solution, str) else []):
            if p and fnmatch.fnmatch(p, pattern):
                errors.append(
                    f"'{p}' matches forbidden pattern '{pattern}' declared by the plan's "
                    "constraints — drop it or drop the constraint with its citation"
                )
    return errors


def cmd_plan(plan: dict) -> int:
    errors = validate_schema(plan)

    target = plan.get("target")
    if isinstance(target, str) and target.strip():
        t = Path(target)
        if t.is_file():
            errors.append(f"target '{target}' is an existing file — name a directory")
        elif t.is_dir():
            entries = sorted(e.name for e in t.iterdir())
            if entries:
                shown = ", ".join(entries[:5]) + ("…" if len(entries) > 5 else "")
                errors.append(
                    f"target '{target}' is not empty ({shown}) — scaffold into an empty or "
                    "absent directory; an existing module is hex-extend's or hex-migrate's job"
                )

    if errors:
        return _emit({"ok": False, "errors": errors}, 1)
    return _emit(
        {"ok": True, "module": plan["module"], "type": plan["type"],
         "projects": len(plan["projects"]), "files": len(plan.get("files", []))},
        0,
    )


def _solution_projects(solution_path: Path) -> list[str]:
    root = ET.parse(solution_path).getroot()
    return [
        el.get("Path").replace("\\", "/")
        for el in root.iter("Project")
        if el.get("Path")
    ]


def cmd_verify(plan: dict) -> int:
    errors = validate_schema(plan)
    if errors:
        return _emit({"ok": False, "errors": errors}, 1)

    target = Path(plan["target"])
    if not target.is_dir():
        return _emit(
            {"ok": False, "errors": [f"target '{plan['target']}' does not exist — nothing to verify"]},
            1,
        )

    planned_projects = [e["path"] for e in plan["projects"]]
    planned_files = list(plan.get("files", []))

    missing = [p for p in planned_projects + planned_files + [plan["solution"]]
               if not (target / p).is_file()]

    missing_from_solution: list[str] = []
    unplanned_in_solution: list[str] = []
    solution_file = target / plan["solution"]
    if solution_file.is_file():
        try:
            referenced = set(_solution_projects(solution_file))
        except ET.ParseError as exc:
            return _emit(
                {"ok": False, "errors": [f"solution '{plan['solution']}' is not parseable XML: {exc}"]},
                1,
            )
        missing_from_solution = sorted(set(planned_projects) - referenced)
        unplanned_in_solution = sorted(referenced - set(planned_projects))

    patterns = (plan.get("constraints") or {}).get("forbidden_path_patterns", [])
    violations = []
    on_disk_projects = []
    files_present = 0
    for path in sorted(target.rglob("*")):
        rel_parts = path.relative_to(target).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        rel = "/".join(rel_parts)
        if path.is_file():
            files_present += 1
            if rel.endswith(".csproj"):
                on_disk_projects.append(rel)
        for pattern in patterns:
            if fnmatch.fnmatch(rel, pattern):
                violations.append(f"'{rel}' matches forbidden pattern '{pattern}'")
    unplanned_on_disk = sorted(set(on_disk_projects) - set(planned_projects))

    ok = not (missing or missing_from_solution or unplanned_in_solution
              or unplanned_on_disk or violations)
    return _emit(
        {"ok": ok, "files_present": files_present, "missing": missing,
         "missing_from_solution": missing_from_solution,
         "unplanned_in_solution": unplanned_in_solution,
         "unplanned_on_disk": unplanned_on_disk, "violations": violations},
        0 if ok else 1,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scaffold",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--file", required=True, help="path to the scaffold plan JSON")
    args = parser.parse_args(argv)

    try:
        plan = load_plan(args.file)
    except (OSError, json.JSONDecodeError) as exc:
        return _emit({"ok": False, "errors": [f"plan '{args.file}' unreadable: {exc}"]}, 2)
    if not isinstance(plan, dict):
        return _emit({"ok": False, "errors": ["plan JSON must be an object"]}, 2)

    return cmd_plan(plan) if args.command == "plan" else cmd_verify(plan)


if __name__ == "__main__":
    sys.exit(main())
