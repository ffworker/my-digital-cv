"""Evidence contracts for the compact bilingual skills page.

These tests validate *specificity* and consistent claims, not whether an
external deployment has been run. Runtime proof must be reviewed separately.
"""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]


def skills(lang):
    return {item["id"]: item for section in DATA[lang]["sections"] for item in section["items"]}


def evidence_urls(item):
    return re.findall(r'href="([^"]+)"', item["evidence"])


class SkillEvidenceContracts(unittest.TestCase):
    def test_every_skill_has_a_concrete_scenario_or_honest_gap(self):
        for lang, label in (("en", "Scenario:"), ("de", "Szenario:")):
            for key, item in skills(lang).items():
                with self.subTest(lang=lang, skill=key):
                    value = item["evidence"]
                    is_scenario = f"<strong>{label}</strong>" in value
                    is_gap = f"<strong>{'Evidence gap:' if lang == 'en' else 'Nachweislücke:'}</strong>" in value
                    self.assertNotEqual(is_scenario, is_gap, "choose one evidence classification")
                    self.assertTrue(evidence_urls(item) if is_scenario else not evidence_urls(item))

    def test_public_links_point_to_specific_artifacts_not_repository_roots(self):
        for lang in DATA:
            for key, item in skills(lang).items():
                for url in evidence_urls(item):
                    with self.subTest(lang=lang, skill=key, url=url):
                        parts = urlsplit(url)
                        self.assertEqual(parts.scheme, "https")
                        self.assertEqual(parts.netloc, "github.com")
                        path = parts.path.strip("/").split("/")
                        self.assertGreaterEqual(len(path), 5, "file-level or run-level evidence required")
                        self.assertEqual(path[0], "ffworker")
                        if path[2] == "blob":
                            self.assertEqual(path[3], "main")
                            self.assertTrue("/".join(path[4:]), "empty file path is not evidence")
                        elif path[2] == "actions":
                            self.assertEqual(path[3], "runs")
                            self.assertTrue(path[4].isdigit(), "workflow evidence must reference one run")
                        else:
                            self.fail("use a concrete source file or completed CI run")

    def test_bilingual_scenarios_reference_identical_artifacts(self):
        self.assertEqual(set(skills("en")), set(skills("de")))
        for key in skills("en"):
            with self.subTest(skill=key):
                self.assertEqual(evidence_urls(skills("en")[key]),
                                 evidence_urls(skills("de")[key]))

    def test_retired_proxmox_lab_is_not_used_as_public_evidence(self):
        # Retiring a project from the public portfolio must not leave references
        # in the source-of-truth or generated EN/DE Tech View output.
        for lang in DATA:
            for item in skills(lang).values():
                self.assertNotIn("ffworker/proxmox-lab", item["evidence"])
        for relative in ("skills-tech.html", "de/skills-tech.html"):
            html = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("ffworker/proxmox-lab", html)

    def test_proof_levels_are_not_silently_upgraded(self):
        for lang in DATA:
            for key, item in skills(lang).items():
                text = item["evidence"].lower()
                with self.subTest(lang=lang, skill=key):
                    self.assertNotIn("100% proven", text)
                    self.assertNotIn("fully verified live", text)
                    self.assertNotIn("guaranteed", text)


if __name__ == "__main__":
    unittest.main()
