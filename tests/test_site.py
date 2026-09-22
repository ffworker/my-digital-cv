from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SiteContractTests(unittest.TestCase):
    def test_german_home_heading_can_wrap_on_narrow_screens(self):
        page = (ROOT / "de" / "index.html").read_text(encoding="utf-8")
        self.assertIn("overflow-wrap: anywhere", page)
        self.assertIn("hyphens: auto", page)

    def test_skills_link_remains_visible_in_mobile_navigation(self):
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn('class="mobile-essential"', page)
            self.assertIn(".nav a.mobile-essential", page)

    def test_cluster_button_keeps_a_visible_focus_indicator(self):
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            focus_rule = page.split(".terminal-command-line:focus-visible {", 1)[1].split("}", 1)[0]
            self.assertIn("outline: 2px solid", focus_rule)
            self.assertNotIn("outline: 0", focus_rule)

    def test_early_automation_skills_use_context_instead_of_numeric_scores(self):
        english = (ROOT / "skills.html").read_text(encoding="utf-8")
        german = (ROOT / "de" / "skills.html").read_text(encoding="utf-8")
        self.assertNotIn(">0/10<", english)
        self.assertNotIn(">1/10<", english)
        self.assertNotIn(">0/10<", german)
        self.assertNotIn(">1/10<", german)
        self.assertIn("AI-guided", english)
        self.assertIn("KI-geführt", german)

    def test_learning_copy_does_not_use_stale_or_placeholder_durations(self):
        all_pages = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in ("index.html", "de/index.html", "skills.html", "de/skills.html")
        )
        for stale in ("two months", "zwei Monate", "day X", "Tag X"):
            self.assertNotIn(stale, all_pages)

    def test_all_public_pages_have_social_metadata(self):
        for relative in ("index.html", "de/index.html", "skills.html", "de/skills.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            for marker in ('property="og:title"', 'property="og:description"', 'property="og:url"', 'property="og:image"', 'name="twitter:card"'):
                self.assertIn(marker, page, f"{relative}: missing {marker}")

    def test_german_skills_page_has_canonical_and_language_alternates(self):
        page = (ROOT / "de" / "skills.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="canonical" href="https://cv.bytegeist.dev/de/skills.html"', page)
        self.assertIn('hreflang="en"', page)
        self.assertIn('hreflang="de"', page)

    def test_crawler_files_are_real_text_and_xml_files(self):
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Sitemap: https://cv.bytegeist.dev/sitemap.xml", robots)
        self.assertIn("<urlset", sitemap)
        for url in ("https://cv.bytegeist.dev/", "https://cv.bytegeist.dev/skills.html", "https://cv.bytegeist.dev/de/index.html", "https://cv.bytegeist.dev/de/skills.html"):
            self.assertIn(url, sitemap)

    def test_first_visit_build_finishes_within_1500ms(self):
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("window.setTimeout(finishBuild, 1500)", page)
            self.assertNotIn("window.setTimeout(finishBuild, 3050)", page)

    def test_primary_green_passes_normal_text_contrast(self):
        for relative in ("index.html", "de/index.html", "skills.html", "de/skills.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("#127654", page)

    def test_professional_brand_colors_pass_normal_text_contrast(self):
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(".tech.vmware { color: #3f7d35; }", page)
            self.assertIn(".tech.veeam { color: #007f28; }", page)
            self.assertNotIn("footer {\n      --green: var(--green-on-dark);", page)

    def test_skills_labels_pass_normal_text_contrast(self):
        for relative in ("skills.html", "de/skills.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(".rating-label{font-size:11px;color:#5f6964", page)
            self.assertNotIn("color:#77817c", page)

    def test_german_lab_tab_accessible_name_contains_visible_label(self):
        page = (ROOT / "de/index.html").read_text(encoding="utf-8")
        self.assertIn('aria-label="Privates Lab – Kontext anzeigen"', page)

    def test_automation_experience_is_explicitly_limited_and_ai_guided(self):
        english = (ROOT / "skills.html").read_text(encoding="utf-8")
        german = (ROOT / "de/skills.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(english.count("Limited hands-on, AI-guided"), 2)
        self.assertGreaterEqual(german.count("Begrenzte Praxis, KI-geführt"), 2)
    def test_animated_content_keeps_accessible_contrast(self):
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn(
                "transition:\n        opacity 360ms var(--ease),\n        transform 420ms var(--ease),",
                page,
            )
            self.assertIn("@keyframes detailIn {\n      from { transform: translateY(12px); }", page)
            self.assertIn(".tech.windows { color: #0067b8; }", page)


if __name__ == "__main__":
    unittest.main()
