#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for migrate.py. Run: uv run scripts/tests/test-migrate.py"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parent.parent / "migrate.py"
spec = importlib.util.spec_from_file_location("migrate", SCRIPT)
migrate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migrate)

RULES = {
    "ok": True,
    "current": [
        {"id": "ulid-identifiers", "tag": "mechanical", "until": ""},
        {"id": "aggregate-pure-functions", "tag": "mechanical", "until": ""},
        {"id": "module-boundary-domain-only", "tag": "judgment", "until": ""},
    ],
    "superseded": [{"id": "aggregate-mutable-apply", "tag": "mechanical", "until": "1.70.0"}],
    "index_drift": False,
}


def finding(cid="ulid-identifiers", severity="fail", tier="mechanical", **extra):
    f = {
        "id": cid,
        "severity": severity,
        "file": "src/Parties.Domain/PartyRegistration.cs",
        "line": 12,
        "evidence": "Guid.NewGuid().ToString()",
        "explanation": "GUID used where a ULID is required",
    }
    if tier is not None:
        f["tier"] = tier
    f.update(extra)
    return f


def verdict(findings, **extra):
    doc = {
        "ok": True,
        "verdict": "fail" if any(f["severity"] == "fail" for f in findings) else "pass",
        "scope": "repo",
        "layer": "full",
        "target": "fixtures/repo-lagging",
        "findings": findings,
        "waived": [],
        "analyzer_owned": [],
        "expired_waivers": [],
        "counts": {},
    }
    doc.update(extra)
    return doc


def run(func, **kwargs):
    out = io.StringIO()
    with redirect_stdout(out):
        code = func(SimpleNamespace(**kwargs))
    return code, json.loads(out.getvalue())


class TiersTests(unittest.TestCase):
    def check(self, findings, tmp):
        vp, rp = Path(tmp) / "verdict.json", Path(tmp) / "rules.json"
        vp.write_text(json.dumps(verdict(findings)), encoding="utf-8")
        rp.write_text(json.dumps(RULES), encoding="utf-8")
        return run(migrate.cmd_tiers, verdict=str(vp), rules=str(rp))

    def test_valid_tiers_pass_with_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            findings = [
                finding(),
                finding("aggregate-pure-functions", tier="structural"),
                finding("module-boundary-domain-only", tier="judgment"),
            ]
            code, out = self.check(findings, tmp)
            self.assertEqual(code, 0)
            self.assertTrue(out["ok"])
            self.assertEqual(out["counts"], {"mechanical": 1, "structural": 1, "judgment": 1})

    def test_failing_finding_without_tier_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.check([finding(tier=None)], tmp)
            self.assertEqual(code, 2)
            self.assertIn("no tier", out["problems"][0])

    def test_warn_without_tier_is_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.check([finding(severity="warn", tier=None)], tmp)
            self.assertEqual(code, 0)

    def test_unknown_tier_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.check([finding(tier="cosmetic")], tmp)
            self.assertEqual(code, 2)
            self.assertIn("unknown tier", out["problems"][0])

    def test_judgment_tagged_rule_must_be_judgment_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.check([finding("module-boundary-domain-only", tier="mechanical")], tmp)
            self.assertEqual(code, 2)
            self.assertIn("human call", out["problems"][0])

    def test_mechanical_tagged_rule_cannot_be_judgment_tier(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.check([finding(tier="judgment")], tmp)
            self.assertEqual(code, 2)
            self.assertIn("mechanical or structural", out["problems"][0])

    def test_unknown_convention_id_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.check([finding("no-such-rule")], tmp)
            self.assertEqual(code, 2)
            self.assertIn("not in the rules output", out["problems"][0])

    def test_unsettled_verdict_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            vp, rp = Path(tmp) / "v.json", Path(tmp) / "r.json"
            vp.write_text(json.dumps({"findings": []}), encoding="utf-8")
            rp.write_text(json.dumps(RULES), encoding="utf-8")
            code, out = run(migrate.cmd_tiers, verdict=str(vp), rules=str(rp))
            self.assertEqual(code, 2)
            self.assertIn("gate.py verdict", out["fix"])


class ReportTests(unittest.TestCase):
    def render(self, doc, tmp):
        vp = Path(tmp) / "verdict.json"
        vp.write_text(json.dumps(doc), encoding="utf-8")
        return run(migrate.cmd_report, verdict=str(vp), out=str(Path(tmp) / "reports"), today="2026-07-13")

    def test_writes_html_and_json_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = verdict(
                [finding(), finding("module-boundary-domain-only", tier="judgment")],
                staleness={"comparable": True, "repo_lags_target": True, "kb_lags_repo": False, "repo_version": "1.68.0", "targets_framework": ">= 1.72"},
                waived=[{"id": "ulid-identifiers", "waiver": {"reason": "HX-123 rewrite", "review": "2099-01-01"}}],
            )
            code, out = self.render(doc, tmp)
            self.assertEqual(code, 0)
            html_text = Path(out["html"]).read_text(encoding="utf-8")
            self.assertIn("gap-report-repo-lagging-2026-07-13.html", out["html"])
            self.assertIn("ulid-identifiers", html_text)
            self.assertIn("Guid.NewGuid().ToString()", html_text)
            self.assertIn("lags KB target", html_text)
            self.assertIn("HX-123 rewrite", html_text)
            self.assertEqual(json.loads(Path(out["json"]).read_text(encoding="utf-8"))["verdict"], "fail")
            self.assertEqual(out["counts"], {"mechanical": 1, "structural": 0, "judgment": 1})

    def test_html_escapes_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.render(verdict([finding(evidence="new List<Guid>() // <script>")]), tmp)
            self.assertEqual(code, 0)
            html_text = Path(out["html"]).read_text(encoding="utf-8")
            self.assertIn("new List&lt;Guid&gt;()", html_text)
            self.assertNotIn("<script>", html_text)

    def test_untiered_fail_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.render(verdict([finding(tier=None)]), tmp)
            self.assertEqual(code, 2)
            self.assertIn("migrate.py tiers", out["fix"])

    def test_unsettled_doc_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            vp = Path(tmp) / "v.json"
            vp.write_text(json.dumps({"findings": []}), encoding="utf-8")
            code, out = run(migrate.cmd_report, verdict=str(vp), out=tmp, today=None)
            self.assertEqual(code, 2)


class FleetTests(unittest.TestCase):
    def test_aggregates_and_finds_hot_spots(self):
        with tempfile.TemporaryDirectory() as tmp:
            vdir = Path(tmp) / "verdicts"
            vdir.mkdir()
            (vdir / "parties.json").write_text(
                json.dumps(
                    verdict(
                        [finding(), finding("aggregate-pure-functions", tier="structural")],
                        target="repos/Hexalith.Parties",
                        staleness={"comparable": True, "repo_lags_target": True, "kb_lags_repo": False, "repo_version": "1.68.0", "targets_framework": ">= 1.72"},
                    )
                ),
                encoding="utf-8",
            )
            (vdir / "inventory.json").write_text(
                json.dumps(
                    verdict(
                        [finding()],
                        target="repos/Hexalith.Inventory",
                        waived=[{"id": "module-boundary-domain-only", "waiver": {"reason": "transitional", "review": "2099-01-01"}}],
                        staleness={"comparable": True, "repo_lags_target": False, "kb_lags_repo": False, "repo_version": "1.72.0", "targets_framework": ">= 1.72"},
                    )
                ),
                encoding="utf-8",
            )
            code, out = run(migrate.cmd_fleet, dir=str(vdir), out=str(Path(tmp) / "reports"), today="2026-07-13")
            self.assertEqual(code, 0)
            result = json.loads(Path(out["json"]).read_text(encoding="utf-8"))
            self.assertEqual(result["totals"], {"repos": 2, "failing_repos": 2, "gaps": 3, "waived": 1})
            self.assertEqual(result["hot_spots"][0], {"id": "ulid-identifiers", "repos": 2})
            rows = {r["repo"]: r for r in result["repos"]}
            self.assertIn("lags KB target", rows["Hexalith.Parties"]["staleness"])
            self.assertEqual(rows["Hexalith.Inventory"]["staleness"], "current")
            html_text = Path(out["html"]).read_text(encoding="utf-8")
            self.assertIn("Hexalith.Parties", html_text)
            self.assertIn("hot-spots", html_text)

    def test_malformed_verdict_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            vdir = Path(tmp) / "verdicts"
            vdir.mkdir()
            (vdir / "broken.json").write_text("{not json", encoding="utf-8")
            code, out = run(migrate.cmd_fleet, dir=str(vdir), out=tmp, today=None)
            self.assertEqual(code, 2)
            self.assertIn("broken.json", out["error"])

    def test_empty_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run(migrate.cmd_fleet, dir=tmp, out=tmp, today=None)
            self.assertEqual(code, 2)
            self.assertIn("no *.json", out["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
