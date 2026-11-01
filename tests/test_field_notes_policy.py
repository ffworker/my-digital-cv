"""Field Notes preview privacy and professional AI-boundary regression."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FieldNotesPolicyTests(unittest.TestCase):
    def test_preview_is_bilingual_unlisted_and_not_promoted_as_a_case_report(self):
        paths = ("field-notes.html", "de/field-notes.html")
        for path in paths:
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('name="robots" content="noindex, follow"', text)
                self.assertIn('href="/field-notes.css"', text)
                self.assertIn('rel="canonical"', text)
                self.assertIn('hreflang="en"', text)
                self.assertIn('hreflang="de"', text)
                self.assertIn('class="notice"', text)
                self.assertIn('href="/skills.html"' if path == "field-notes.html"
                              else 'href="/de/skills.html"', text)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        german = (ROOT / "de/index.html").read_text(encoding="utf-8")
        self.assertNotIn("field-notes", sitemap)
        self.assertNotIn('href="/field-notes.html"', home)
        self.assertNotIn('href="/de/field-notes.html"', german)

    def test_professional_ai_boundary_is_explicit_in_both_languages(self):
        notes = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
        self.assertIn("do not use AI in day-to-day live IT operations",
                      notes["en"]["note"])
        self.assertIn("Im täglichen produktiven IT-Betrieb nutze ich keine KI",
                      notes["de"]["note"])
        for page in ("index.html", "de/index.html"):
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn("live IT operations" if page == "index.html"
                          else "produktiven IT-Betrieb", text)
        for path, phrase in (
            ("skills.html", "do not use AI in day-to-day live IT operations"),
            ("skills-tech.html", "do not use AI in day-to-day live IT operations"),
            ("de/skills.html", "Im täglichen produktiven IT-Betrieb nutze ich keine KI"),
            ("de/skills-tech.html", "Im täglichen produktiven IT-Betrieb nutze ich keine KI"),
        ):
            with self.subTest(path=path):
                self.assertIn(phrase, (ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
