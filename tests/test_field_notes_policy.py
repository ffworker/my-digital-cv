"""Retired preview and professional AI-boundary regressions."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FieldNotesPolicyTests(unittest.TestCase):
    def test_retired_field_notes_do_not_compete_with_canonical_blog(self):
        for path in ("field-notes.html", "de/field-notes.html", "field-notes.css"):
            self.assertFalse((ROOT / path).exists(), f"obsolete CV journal asset: {path}")
        for path in ("index.html", "de/index.html"):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertNotIn("field-notes", text)
            self.assertIn("https://blog.bytegeist.dev/artikel/signaturee/", text)
            self.assertIn("https://blog.bytegeist.dev/", text)
        self.assertNotIn("field-notes", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

    def test_professional_ai_boundary_is_explicit_in_both_languages(self):
        notes = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
        self.assertIn("AI agents do not autonomously access or change production systems",
                      notes["en"]["note"])
        self.assertIn("KI-Agenten greifen nicht autonom auf Produktivsysteme zu",
                      notes["de"]["note"])
        for page in ("index.html", "de/index.html"):
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn("AI" if page == "index.html" else "KI", text)
            self.assertIn("production" if page == "index.html" else "Produktivsysteme", text)
        for path, phrase in (
            ("skills.html", "No autonomous AI actions at work."),
            ("skills-tech.html", "AI agents do not autonomously access or change production systems"),
            ("de/skills.html", "Keine autonomen KI-Eingriffe im Job."),
            ("de/skills-tech.html", "KI-Agenten greifen nicht autonom auf Produktivsysteme zu"),
        ):
            with self.subTest(path=path):
                self.assertIn(phrase, (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
