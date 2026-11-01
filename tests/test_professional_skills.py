"""Both styles show identical bilingual skill content, with editorial canonical."""
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
    def test_editorial_is_canonical_default_for_both_languages(self):
        for path, tech, other in (
            ("skills.html", "/skills-tech.html", "/de/skills.html"),
            ("de/skills.html", "/de/skills-tech.html", "/skills.html"),
        ):
            with self.subTest(page=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('href="/skills-professional.css"', page)
                self.assertNotIn('href="/skills.css"', page)
                self.assertIn('name="robots" content="index, follow"', page)
                self.assertIn('class="theme-switch"', page)
                self.assertIn(f'href="{tech}"', page)
                self.assertIn(f'href="{other}"', page)
                self.assertIn('class="skills-page skills-professional"', page)

    def test_tech_view_preserves_the_old_console_style(self):
        for path, original, other in (
            ("skills-tech.html", "/skills.html", "/de/skills-tech.html"),
            ("de/skills-tech.html", "/de/skills.html", "/skills-tech.html"),
        ):
            with self.subTest(page=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('href="/skills.css"', page)
                self.assertNotIn('skills-professional.css', page)
                self.assertIn('name="robots" content="noindex, follow"', page)
                self.assertIn('rel="canonical" href="https://cv.bytegeist.dev' + original + '"', page)
                self.assertIn('class="tech-view-choice"', page)
                self.assertIn(f'href="{original}"', page)
                self.assertIn(f'href="{other}"', page)
                self.assertIn('class="skills-page skills-tech"', page)

    def test_same_skill_ids_scores_evidence_and_source_order(self):
        for editorial, technical in (
            ("skills.html", "skills-tech.html"),
            ("de/skills.html", "de/skills-tech.html"),
        ):
            a = skill_cards((ROOT / editorial).read_text(encoding="utf-8"))
            b = skill_cards((ROOT / technical).read_text(encoding="utf-8"))
            self.assertEqual(len(a), 13)
            self.assertEqual(list(a), list(b))
            for skill in a:
                with self.subTest(page=editorial, skill=skill):
                    self.assertEqual(a[skill], b[skill])

    def test_professional_context_precedes_skill_list(self):
        for path, labels in (
            ("skills.html", ("Professional IT operations", "Private infrastructure lab")),
            ("de/skills.html", ("Beruflicher IT-Betrieb", "Privates Infrastruktur-Lab")),
        ):
            with self.subTest(page=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('class="experience-panel"', page)
                self.assertNotIn('class="index-panel"', page)
                self.assertIn('class="context-link"', page)
                for label in labels:
                    self.assertIn(label, page)
                self.assertLess(page.index('class="experience-panel"'),
                                page.index('<section class="skill-group"'))
                self.assertLess(page.index('<section class="skill-group"'),
                                page.index('<details class="methodology">'))
        for tech in ("skills-tech.html", "de/skills-tech.html"):
            with self.subTest(page=tech):
                page = (ROOT / tech).read_text(encoding="utf-8")
                self.assertIn('class="index-panel"', page)
                self.assertLess(page.index('<details class="methodology">'),
                                page.index('<section class="skill-group"'))

    def test_former_previews_redirect_to_canonical_urls(self):
        for path, target in (
            ("skills-professional.html", "/skills.html"),
            ("de/skills-professional.html", "/de/skills.html"),
        ):
            with self.subTest(page=path):
                html = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('content="0; url=' + target + '"', html)
                self.assertIn('name="robots" content="noindex, follow"', html)
                self.assertIn('rel="canonical" href="https://cv.bytegeist.dev' + target + '"', html)

    def test_accessible_disclosures_and_no_external_fonts_or_scripts(self):
        css = (ROOT / "skills-professional.css").read_text(encoding="utf-8")
        self.assertIn(".skill-card[open]", css)
        self.assertIn("a:focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertNotIn("@import", css)
        for path in ("skills.html", "de/skills.html", "skills-tech.html", "de/skills-tech.html"):
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(page.count('<details class="skill-card"'), 13)
            self.assertEqual(page.count('<summary class="skill-summary">'), 13)
            self.assertNotIn("<script", page)


if __name__ == "__main__":
    unittest.main()
