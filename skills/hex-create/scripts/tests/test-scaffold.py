#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for scaffold.py. Run: uv run scripts/tests/test-scaffold.py"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scaffold.py"
spec = importlib.util.spec_from_file_location("scaffold", SCRIPT)
scaffold = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scaffold)


def good_plan(target: str) -> dict:
    return {
        "module": "Inventory",
        "type": "technical",
        "target": target,
        "solution": "Inventory.slnx",
        "projects": [
            {"path": "src/Inventory.Domain/Inventory.Domain.csproj", "role": "src"},
            {"path": "test/Inventory.Domain.Tests/Inventory.Domain.Tests.csproj", "role": "test"},
        ],
        "files": ["Directory.Packages.props", ".gitignore"],
        "constraints": {"forbidden_path_patterns": ["src/*.ApiServer*"]},
        "citations": ["module-skeleton-structure"],
    }


def run(command: str, plan: dict, tmp: Path) -> tuple[int, dict]:
    plan_file = tmp / "plan.json"
    plan_file.write_text(json.dumps(plan), encoding="utf-8")
    out = io.StringIO()
    with redirect_stdout(out):
        code = scaffold.main([command, "--file", str(plan_file)])
    return code, json.loads(out.getvalue())


def write_scaffold(plan: dict, base: Path, solution_projects: list[str] | None = None) -> None:
    target = base / plan["target"]
    for entry in plan["projects"]:
        p = target / entry["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<Project Sdk=\"Microsoft.NET.Sdk\" />", encoding="utf-8")
    for f in plan.get("files", []):
        p = target / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")
    refs = solution_projects if solution_projects is not None else [e["path"] for e in plan["projects"]]
    body = "".join(f'  <Project Path="{r}" />\n' for r in refs)
    (target / plan["solution"]).write_text(f"<Solution>\n{body}</Solution>\n", encoding="utf-8")


class PlanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_valid_plan_passes(self):
        code, out = run("plan", good_plan(str(self.tmp / "out")), self.tmp)
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["projects"], 2)

    def test_bad_module_name_fails(self):
        for bad in ("", "1Inventory", "In ventory", "Inventory.", "a/b"):
            plan = good_plan(str(self.tmp / "out"))
            plan["module"] = bad
            code, out = run("plan", plan, self.tmp)
            self.assertEqual(code, 1, bad)
            self.assertTrue(any("filesystem/msbuild-safe" in e for e in out["errors"]), bad)

    def test_bad_type_fails(self):
        plan = good_plan(str(self.tmp / "out"))
        plan["type"] = "hybrid"
        code, out = run("plan", plan, self.tmp)
        self.assertEqual(code, 1)

    def test_non_empty_target_fails_and_names_contents(self):
        target = self.tmp / "out"
        target.mkdir()
        (target / "stray.txt").write_text("x", encoding="utf-8")
        code, out = run("plan", good_plan(str(target)), self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("not empty" in e and "stray.txt" in e for e in out["errors"]))

    def test_missing_citations_fails(self):
        plan = good_plan(str(self.tmp / "out"))
        plan["citations"] = []
        code, out = run("plan", plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("cites no KB entries" in e for e in out["errors"]))

    def test_constraint_violation_in_plan_fails(self):
        plan = good_plan(str(self.tmp / "out"))
        plan["projects"].append(
            {"path": "src/Inventory.ApiServer/Inventory.ApiServer.csproj", "role": "src"}
        )
        code, out = run("plan", plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("forbidden pattern" in e for e in out["errors"]))

    def test_duplicate_and_escaping_paths_fail(self):
        plan = good_plan(str(self.tmp / "out"))
        plan["projects"].append(dict(plan["projects"][0]))
        plan["files"].append("../outside.txt")
        code, out = run("plan", plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("planned twice" in e for e in out["errors"]))
        self.assertTrue(any("escapes target" in e for e in out["errors"]))

    def test_unreadable_plan_exits_2(self):
        bad = self.tmp / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            code = scaffold.main(["plan", "--file", str(bad)])
        self.assertEqual(code, 2)


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.plan = good_plan(str(self.tmp / "out"))

    def test_complete_scaffold_passes(self):
        write_scaffold(self.plan, Path("/"))
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(out["files_present"], 5)  # 2 csproj + slnx + props + .gitignore

    def test_unplanned_csproj_on_disk_caught(self):
        write_scaffold(self.plan, Path("/"))
        stray = Path(self.plan["target"]) / "src/Inventory.Ghost/Inventory.Ghost.csproj"
        stray.parent.mkdir(parents=True)
        stray.write_text("<Project Sdk=\"Microsoft.NET.Sdk\" />", encoding="utf-8")
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertIn("src/Inventory.Ghost/Inventory.Ghost.csproj", out["unplanned_on_disk"])

    def test_missing_project_file_caught(self):
        write_scaffold(self.plan, Path("/"))
        (Path(self.plan["target"]) / self.plan["projects"][1]["path"]).unlink()
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertIn(self.plan["projects"][1]["path"], out["missing"])

    def test_planned_project_missing_from_solution_caught(self):
        write_scaffold(self.plan, Path("/"), solution_projects=[self.plan["projects"][0]["path"]])
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertIn(self.plan["projects"][1]["path"], out["missing_from_solution"])

    def test_unplanned_project_in_solution_caught(self):
        extra = "src/Ghost/Ghost.csproj"
        write_scaffold(
            self.plan, Path("/"),
            solution_projects=[e["path"] for e in self.plan["projects"]] + [extra],
        )
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertIn(extra, out["unplanned_in_solution"])

    def test_forbidden_dir_on_disk_caught(self):
        write_scaffold(self.plan, Path("/"))
        stray = Path(self.plan["target"]) / "src/Inventory.ApiServer/Program.cs"
        stray.parent.mkdir(parents=True)
        stray.write_text("// host", encoding="utf-8")
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("Inventory.ApiServer" in v for v in out["violations"]))

    def test_bin_obj_git_skipped_by_constraint_walk(self):
        write_scaffold(self.plan, Path("/"))
        buried = Path(self.plan["target"]) / "obj/src/Inventory.ApiServer/cache.txt"
        buried.parent.mkdir(parents=True)
        buried.write_text("x", encoding="utf-8")
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 0)
        self.assertEqual(out["violations"], [])

    def test_absent_target_fails(self):
        code, out = run("verify", self.plan, self.tmp)
        self.assertEqual(code, 1)
        self.assertTrue(any("does not exist" in e for e in out["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
