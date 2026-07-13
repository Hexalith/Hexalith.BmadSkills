#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for gate.py. Run: uv run scripts/tests/test-gate.py"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parent.parent / "gate.py"
spec = importlib.util.spec_from_file_location("gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

WAIVERS = """# repo waivers
waivers:
  - id: ulid-identifiers
    reason: legacy import layer, rewrite scheduled HX-123
    review: 2099-01-01
  - id: module-boundary
    reason: transitional AppHost during split
    review: 2026-01-01
"""

ENTRY = """---
id: {id}
title: A rule
tag: {tag}
since: 1.40.0
until: '{until}'
supersedes: ''
provenance: framework:Hexalith@v1.40.0
verified: ''
drained: na
---

# A rule

## Statement

The rule.
"""

META = "---\ntargets_framework: '>= 1.72'\n---\n"

PROPS = """<Project>
  <ItemGroup>
    <PackageVersion Include="Hexalith.Domains" Version="{version}" />
    <PackageVersion Include="Other.Package" Version="9.9.9" />
  </ItemGroup>
</Project>
"""

FINDINGS = {
    "scope": "diff",
    "layer": "judgment",
    "target": "repo",
    "findings": [
        {"id": "ulid-identifiers", "severity": "fail", "file": "src/A.cs", "line": 3, "evidence": "Guid.NewGuid()", "explanation": "GUIDs are forbidden"},
        {"id": "projection-registration", "severity": "fail", "file": "src/B.cs", "line": 8, "evidence": "manual wiring", "explanation": "not registered per convention"},
    ],
}


def make_kb(root: Path, tags: dict):
    (root / "entries").mkdir(parents=True)
    (root / "meta.md").write_text(META, encoding="utf-8")
    for name, (tag, until) in tags.items():
        (root / "entries" / f"{name}.md").write_text(ENTRY.format(id=name, tag=tag, until=until), encoding="utf-8")


def run(func, args):
    out = io.StringIO()
    with redirect_stdout(out):
        code = func(SimpleNamespace(**args))
    return code, json.loads(out.getvalue()) if out.getvalue().lstrip().startswith("{") else out.getvalue()


class WaiversTest(unittest.TestCase):
    def test_active_and_expired_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hex-waivers.yaml"
            path.write_text(WAIVERS, encoding="utf-8")
            code, out = run(gate.cmd_waivers, {"file": str(path), "today": "2026-07-13"})
            self.assertEqual(code, 0)
            self.assertEqual([w["id"] for w in out["active"]], ["ulid-identifiers"])
            self.assertEqual([w["id"] for w in out["expired"]], ["module-boundary"])

    def test_absent_file_waives_nothing(self):
        code, out = run(gate.cmd_waivers, {"file": "/nowhere/hex-waivers.yaml", "today": "2026-07-13"})
        self.assertEqual(code, 0)
        self.assertEqual(out["active"], [])

    def test_malformed_names_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hex-waivers.yaml"
            path.write_text("waivers:\n  - id: x\n    reason: y\n", encoding="utf-8")
            code, out = run(gate.cmd_waivers, {"file": str(path), "today": "2026-07-13"})
            self.assertEqual(code, 1)
            self.assertIn("review", out["findings"][0]["problem"])


class CoverageTest(unittest.TestCase):
    def test_partition_and_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            make_kb(kb, {"ulid-identifiers": ("mechanical", ""), "slnx-solution": ("mechanical", ""), "module-boundary": ("judgment", ""), "old-rule": ("mechanical", "1.60.0")})
            manifest = Path(tmp) / "analyzer-rules.json"
            manifest.write_text(json.dumps({"rules": [
                {"diagnostic": "HEX0001", "convention": "ulid-identifiers"},
                {"diagnostic": "HEX0002", "convention": "no-such-entry"},
            ]}), encoding="utf-8")
            code, out = run(gate.cmd_coverage, {"kb": str(kb), "manifest": str(manifest)})
            self.assertEqual(code, 0)
            self.assertEqual(out["covered"], ["ulid-identifiers"])
            self.assertEqual(out["uncovered"], ["slnx-solution"])  # judgment + superseded excluded
            self.assertEqual(out["unknown_mappings"][0]["convention"], "no-such-entry")

    def test_absent_manifest_is_zero_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            make_kb(kb, {"ulid-identifiers": ("mechanical", "")})
            code, out = run(gate.cmd_coverage, {"kb": str(kb), "manifest": str(Path(tmp) / "missing.json")})
            self.assertEqual(code, 0)
            self.assertTrue(out["manifest_absent"])
            self.assertEqual(out["uncovered"], ["ulid-identifiers"])


class StalenessTest(unittest.TestCase):
    def check(self, version):
        with tempfile.TemporaryDirectory() as tmp:
            kb, repo = Path(tmp) / "kb", Path(tmp) / "repo"
            make_kb(kb, {})
            repo.mkdir()
            (repo / "Directory.Packages.props").write_text(PROPS.format(version=version), encoding="utf-8")
            return gate.staleness(kb, repo)

    def test_repo_ahead_means_kb_lags(self):
        out = self.check("1.80.1")
        self.assertTrue(out["kb_lags_repo"])
        self.assertFalse(out["repo_lags_target"])

    def test_repo_behind_means_repo_lags(self):
        out = self.check("1.65.2-preview.4")
        self.assertFalse(out["kb_lags_repo"])
        self.assertTrue(out["repo_lags_target"])

    def test_no_props_is_incomparable(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb, repo = Path(tmp) / "kb", Path(tmp) / "repo"
            make_kb(kb, {})
            repo.mkdir()
            self.assertFalse(gate.staleness(kb, repo)["comparable"])


class RulesTest(unittest.TestCase):
    def test_partition_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            make_kb(kb, {"ulid-identifiers": ("mechanical", ""), "old-rule": ("mechanical", "1.60.0")})
            code, out = run(gate.cmd_rules, {"kb": str(kb)})
            self.assertEqual(code, 0)
            self.assertEqual([e["id"] for e in out["current"]], ["ulid-identifiers"])
            self.assertEqual([e["id"] for e in out["superseded"]], ["old-rule"])
            self.assertTrue(out["index_drift"])  # no index.md
            (kb / "index.md").write_text("| id | title |\n| --- | --- |\n| ulid-identifiers | x |\n| old-rule | x |\n", encoding="utf-8")
            code, out = run(gate.cmd_rules, {"kb": str(kb)})
            self.assertFalse(out["index_drift"])


class VerdictTest(unittest.TestCase):
    def settle(self, tmp, findings=FINDINGS, waivers=WAIVERS, fmt="json", kb=None, manifest=None):
        f = Path(tmp) / "findings.json"
        f.write_text(json.dumps(findings), encoding="utf-8")
        w = Path(tmp) / "hex-waivers.yaml"
        w.write_text(waivers, encoding="utf-8")
        return run(gate.cmd_verdict, {"findings": str(f), "waivers": str(w), "kb": kb, "repo": None, "manifest": manifest, "format": fmt, "today": "2026-07-13"})

    def test_waiver_suppresses_expiry_bites(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.settle(tmp)
            self.assertEqual(code, 1)  # projection-registration still fails
            self.assertEqual(out["verdict"], "fail")
            self.assertEqual([w["id"] for w in out["waived"]], ["ulid-identifiers"])
            ids = [f["id"] for f in out["findings"]]
            self.assertIn("module-boundary", ids)  # expired waiver became a warn finding
            self.assertEqual(out["counts"], {"fail": 1, "warn": 1, "waived": 1, "analyzer_owned": 0})

    def test_all_waived_passes(self):
        doc = {**FINDINGS, "findings": [FINDINGS["findings"][0]]}
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.settle(tmp, findings=doc, waivers=WAIVERS.replace("2026-01-01", "2099-01-01"))
            self.assertEqual(code, 0)
            self.assertEqual(out["verdict"], "pass")

    def test_uncited_finding_rejected(self):
        doc = {**FINDINGS, "findings": [{"severity": "fail", "file": "a.cs", "evidence": "x", "explanation": "y"}]}
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.settle(tmp, findings=doc)
            self.assertEqual(code, 2)
            self.assertIn("id", out["problems"][0])

    def test_unknown_id_rejected_with_kb(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            make_kb(kb, {"ulid-identifiers": ("mechanical", "")})  # projection-registration absent
            code, out = self.settle(tmp, kb=str(kb))
            self.assertEqual(code, 2)
            self.assertIn("projection-registration", out["problems"][0])

    def test_known_ids_pass_with_kb(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            make_kb(kb, {"ulid-identifiers": ("mechanical", ""), "projection-registration": ("mechanical", ""), "module-boundary": ("judgment", "")})
            code, out = self.settle(tmp, kb=str(kb))
            self.assertEqual(out["verdict"], "fail")  # settled normally, no schema rejection

    def test_analyzer_owned_partition(self):
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp) / "kb"
            make_kb(kb, {"ulid-identifiers": ("mechanical", ""), "projection-registration": ("mechanical", ""), "module-boundary": ("judgment", "")})
            manifest = Path(tmp) / "analyzer-rules.json"
            manifest.write_text(json.dumps({"rules": [{"diagnostic": "HEX0001", "convention": "ulid-identifiers"}]}), encoding="utf-8")
            code, out = self.settle(tmp, waivers="waivers:\n", kb=str(kb), manifest=str(manifest))
            self.assertEqual([f["id"] for f in out["analyzer_owned"]], ["ulid-identifiers"])
            self.assertEqual([f["id"] for f in out["findings"]], ["projection-registration"])
            self.assertEqual(out["counts"]["analyzer_owned"], 1)

    def test_manifest_without_kb_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.settle(tmp, manifest=str(Path(tmp) / "analyzer-rules.json"))
            self.assertEqual(code, 2)

    def test_annotations_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.settle(tmp, fmt="annotations")
            self.assertEqual(code, 1)
            self.assertIn("::error file=src/B.cs,line=8,title=hex-enforce projection-registration::", out)
            self.assertIn("::warning", out)  # expired waiver annotates too


if __name__ == "__main__":
    unittest.main(verbosity=2)
