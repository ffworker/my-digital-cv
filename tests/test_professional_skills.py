"""Editorial is a short, warm professional profile; technical evidence stays in Tech View."""
from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EditorialSkillsTests(unittest.TestCase):
    def test_bilingual_editorial_is_canonical_and_linked(self):
        for path, tech, other in (
            ("skills.html", "/skills-tech.html", "/de/skills.html"),
            ("de/skills.html", "/de/skills-tech.html", "/skills.html"),
        ):
            with self.subTest(path=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('href="/skills-professional.css?v=', page)
                self.assertIn('name="robots" content="index, follow"', page)
                self.assertIn(f'href="{tech}"', page)
                self.assertIn(f'href="{other}"', page)
                self.assertIn('class="skills-page skills-professional"', page)
                self.assertIn('class="professional-story"', page)
                self.assertIn('class="hero-note-text"', page)
                self.assertEqual(page.count('class="practice-chapter"'), 3)
                self.assertEqual(page.count('class="capability"'), 9)
                self.assertIn('class="lab-gateway"', page)
                self.assertIn('class="context-item"', page)
                self.assertNotIn('<details class="skill-card"', page)
                self.assertNotIn('<details class="methodology"', page)
                self.assertNotIn('class="practice-grid"', page)
                self.assertNotIn('<script', page)
                self.assertLess(page.index('class="professional-story"'),
                                page.index('class="practice-section"'))
                self.assertLess(page.index('class="practice-section"'),
                                page.index('class="lab-gateway"'))

    def test_editorial_contains_real_lived_experience_and_not_generic_score_wall(self):
        english = (ROOT / "skills.html").read_text(encoding="utf-8")
        german = (ROOT / "de/skills.html").read_text(encoding="utf-8")
        for page in (english, german):
            self.assertIn("VMware vSphere / ESXi", page)
            self.assertIn("Debian / Ubuntu Linux", page)
            self.assertIn("Docker / Compose", page)
            self.assertIn("Veeam Backup", page)
            self.assertIn("PowerStore", page)
            self.assertNotIn('class="skill-score"', page)
        self.assertIn("The server nobody remembers.", english)
        self.assertIn("Der Server, den keiner mehr kennt.", german)
        self.assertIn("No autonomous AI actions at work.", english)
        self.assertIn("Keine autonomen KI-Eingriffe im Job.", german)

    def test_tech_view_keeps_console_design_and_original_13_skills(self):
        for path, editorial, other in (
            ("skills-tech.html", "/skills.html", "/de/skills-tech.html"),
            ("de/skills-tech.html", "/de/skills.html", "/skills-tech.html"),
        ):
            with self.subTest(path=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn('href="/skills.css?v=', page)
                self.assertNotIn('skills-professional.css', page)
                self.assertIn('name="robots" content="noindex, follow"', page)
                self.assertIn('rel="canonical" href="https://cv.bytegeist.dev' + editorial + '"', page)
                self.assertIn(f'href="{editorial}"', page)
                self.assertIn(f'href="{other}"', page)
                self.assertIn('class="skills-page skills-tech"', page)
                self.assertEqual(page.count('<details class="skill-card"'), 13)
                self.assertEqual(page.count('<summary class="skill-summary">'), 13)
                self.assertIn('class="index-panel"', page)

    def test_tech_view_is_readable_without_losing_evidence(self):
        css = (ROOT / "skills.css").read_text(encoding="utf-8")
        self.assertIn(".skills-tech .skill-grid", css)
        self.assertIn(".skills-tech .tech-reading-guide", css)
        self.assertIn(".skills-tech .skill-peek", css)
        self.assertIn(".skills-tech .detail-line", css)
        for path, intro in (
            ("skills-tech.html", "Technical depth, with context."),
            ("de/skills-tech.html", "Technische Praxis. Mit Kontext."),
        ):
            with self.subTest(path=path):
                page = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn(intro, page)
                self.assertIn('class="tech-reading-guide"', page)
                self.assertIn('href="#skills-infrastructure"', page)
                self.assertIn('href="#skills-delivery"', page)
                self.assertEqual(page.count('<details class="skill-card"'), 13)

    def test_deployed_stylesheets_have_content_fingerprint(self):
        """A new stylesheet must get a new URL, not a four-hour stale browser copy."""
        for stylesheet, pages in (
            ("skills-professional.css", ("skills.html", "de/skills.html")),
            ("skills.css", ("skills-tech.html", "de/skills-tech.html")),
        ):
            data = (ROOT / stylesheet).read_bytes()
            version = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()[:12]
            reference = f'href="/{stylesheet}?v={version}"'
            for path in pages:
                with self.subTest(stylesheet=stylesheet, page=path):
                    page = (ROOT / path).read_text(encoding="utf-8")
                    self.assertIn(reference, page)

    def test_mobile_reading_and_accessibility_requirements(self):
        css = (ROOT / "skills-professional.css").read_text(encoding="utf-8")
        for marker in ("a:focus-visible", "prefers-reduced-motion", ".practice-chapter",
                       ".capability", ".professional-story", "@media(max-width:640px)"):
            self.assertIn(marker, css)
        self.assertNotIn("@import", css)
        for path in ("skills.html", "de/skills.html"):
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn('<a class="skip-link" href="#skills-overview">', page)
            self.assertIn('id="practice-title"', page)
            self.assertIn('aria-labelledby="skills-title"', page)
            self.assertIn('id="lab-depth"', page)

    def test_former_preview_redirects_are_preserved(self):
        for path, target in (
            ("skills-professional.html", "/skills.html"),
            ("de/skills-professional.html", "/de/skills.html"),
        ):
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn('content="0; url=' + target + '"', page)
            self.assertIn('name="robots" content="noindex, follow"', page)


if __name__ == "__main__":
    unittest.main()
