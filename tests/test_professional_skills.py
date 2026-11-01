"""The editorial view is only a different presentation of existing skill evidence."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def skill_cards(text):
    result = {}
    parts = re.split(r'(?=<details class="skill-card")', text)
    for part in parts:
        match = re.match(r'<details class="skill-card" id="skill-([^"]+)"', part)
        if match:
            result[match.group(1)] = part.split("</details>", 1)[0]
    return result


class AlternateSkillsThemeTests(unittest.TestCase):
    def test_original_console_theme_stays_default(self):
        for path in ("skills.html", "de/skills.html"):
            with self.subTest(page=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('href="/skills.css"', page)
                self.assertNotIn('skills-professional.css', page)
                self.assertIn('name="robots" content="index, follow"', page)

    def test_editorial_theme_has_bilingual_preview_routes_and_canonical(self):
        pairs = (
            ("skills-professional.html", "/skills.html", "/de/skills-professional.html"),
            ("de/skills-professional.html", "/de/skills.html", "/skills-professional.html"),
        )
        for path, original, language_url in pairs:
            with self.subTest(page=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('href="/skills-professional.css"', page)
                self.assertIn('name="robots" content="noindex, follow"', page)
                self.assertIn('rel="canonical" href="https://cv.bytegeist.dev' + original + '"', page)
                self.assertIn('class="theme-switch"', page)
                self.assertIn('href="' + original + '"', page)
                self.assertIn('href="' + language_url + '"', page)
                self.assertIn('class="skills-page skills-professional"', page)

    def test_same_skill_ids_scores_evidence_and_source_order(self):
        for original, alternate in (
            ("skills.html", "skills-professional.html"),
            ("de/skills.html", "de/skills-professional.html"),
        ):
            a = skill_cards((ROOT / original).read_text(encoding="utf-8"))
            b = skill_cards((ROOT / alternate).read_text(encoding="utf-8"))
            self.assertEqual(len(a), 13)
            self.assertEqual(list(a), list(b))
            for skill in a:
                with self.subTest(page=alternate, skill=skill):
                    self.assertEqual(a[skill], b[skill])

    def test_editorial_uses_accessible_details_without_remote_assets(self):
        css = (ROOT / "skills-professional.css").read_text(encoding="utf-8")
        self.assertIn(".skill-card[open]", css)
        self.assertIn("a:focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertNotIn("@import", css)
        for path in ("skills-professional.html", "de/skills-professional.html"):
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(page.count('<details class="skill-card"'), 13)
            self.assertEqual(page.count('<summary class="skill-summary">'), 13)
            self.assertNotIn("<script", page)


if __name__ == "__main__":
    unittest.main()
