from pathlib import Path
import unittest
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class SiteContractTests(unittest.TestCase):
    def test_home_describes_completed_talos_migration(self):
        for relative, node_phrase in (
            ("index.html", "three control-plane/etcd nodes"),
            ("de/index.html", "drei Control-Plane-/etcd-Nodes"),
        ):
            with self.subTest(page=relative):
                page = (ROOT / relative).read_text(encoding="utf-8")
                self.assertNotRegex(page, r"CP03[^<]*(?:in progress|im Aufbau)")
                for marker in (node_phrase, "AMD64", "ARM64", "Kustomize", "SOPS", "age", "Teddycloud"):
                    self.assertIn(marker, page)

    def test_skills_describe_current_talos_practice_without_pending_cp03(self):
        for relative, node_phrase in (
            ("skills.html", "three control-plane/etcd nodes"),
            ("de/skills.html", "drei Control-Plane-/etcd-Nodes"),
        ):
            with self.subTest(page=relative):
                page = (ROOT / relative).read_text(encoding="utf-8")
                self.assertNotRegex(page, r"CP03[^<]*(?:in progress|im Aufbau)")
                for marker in (node_phrase, "AMD64", "ARM64", "Kustomize", "SOPS"):
                    self.assertIn(marker, page)

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
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("#127654", page)
        stylesheet = (ROOT / "skills.css").read_text(encoding="utf-8")
        self.assertIn("--green:#127654", stylesheet)

    def test_professional_brand_colors_pass_normal_text_contrast(self):
        for relative in ("index.html", "de/index.html"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn(".tech.vmware { color: #3f7d35; }", page)
            self.assertIn(".tech.veeam { color: #007f28; }", page)
            self.assertNotIn("footer {\n      --green: var(--green-on-dark);", page)

    def test_skills_labels_pass_normal_text_contrast(self):
        stylesheet = (ROOT / "skills.css").read_text(encoding="utf-8")
        self.assertIn("--muted:#9daea4", stylesheet)
        self.assertIn("--accent:#42d49a", stylesheet)
        self.assertIn("a:focus-visible,summary:focus-visible", stylesheet)

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



    def test_bilingual_skills_use_compact_semantic_disclosures(self):
        for relative in ("skills.html", "de/skills.html"):
            with self.subTest(page=relative):
                page = (ROOT / relative).read_text(encoding="utf-8")
                self.assertEqual(page.count('<details class="skill-card"'), 13)
                self.assertEqual(page.count('<summary class="skill-summary">'), 13)
                self.assertEqual(page.count('class="segment-bar" aria-hidden="true"'), 13)
                self.assertEqual(page.count('<i class="segment '), 130)
                self.assertEqual(page.count('data-rating-kind='), 13)
                self.assertEqual(page.count('data-rating-kind="unrated"'), 2)
                self.assertEqual(page.count('data-rating-kind="range"'), 1)
                self.assertEqual(page.count('<section class="skill-group"'), 2)
                self.assertIn('<details class="methodology">', page)
                self.assertIn('<a class="skip-link" href="#skills-overview">', page)
                self.assertIn('<link rel="stylesheet" href="/skills.css"', page)
                self.assertNotIn('<style>', page)
                self.assertNotIn('<script', page)
                self.assertNotIn('<table class="matrix"', page)
        css = (ROOT / "skills.css").read_text(encoding="utf-8")
        self.assertIn(".skill-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))", css)
        self.assertIn(".skill-card[open]", css)
        self.assertIn("@media(max-width:940px)", css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", css)

    def test_skill_bar_levels_match_source_in_both_languages(self):
        data = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
        for lang, path in (("en", "skills.html"), ("de", "de/skills.html")):
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("5–6/10", page)
            self.assertIn("9/10", page)
            self.assertIn("4/10", page)
            # The two explicitly AI-guided skills have no fabricated numeric bar.
            for section in data[lang]["sections"]:
                for skill in section["items"]:
                    if skill["rating_kind"] == "unrated":
                        self.assertIn(f'id="skill-{skill["id"]}" data-rating-kind="unrated"', page)
            self.assertEqual(page.count('class="segment possible"'), 1)

    def test_domain_accents_are_localized_and_not_rating_levels(self):
        data = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
        expected = {"linux", "network", "platform", "automation", "storage", "monitoring"}
        domains_by_lang = {}
        for lang, path in (("en", "skills.html"), ("de", "de/skills.html")):
            page = (ROOT / path).read_text(encoding="utf-8")
            domains = [(item["id"], item["domain"])
                       for group in data[lang]["sections"] for item in group["items"]]
            self.assertEqual(len(domains), 13)
            self.assertEqual({domain for _, domain in domains}, expected)
            self.assertEqual(page.count('class="skill-domain"'), 13)
            self.assertIn('class="category-note"', page)
            for id_, domain in domains:
                self.assertIn(f'id="skill-{id_}"', page)
                self.assertIn(f'data-domain="{domain}"', page)
                self.assertIn(f'class="skill-domain">{data[lang]["ui"]["domains"][domain]}</span>', page)
            domains_by_lang[lang] = domains
        self.assertEqual(domains_by_lang["en"], domains_by_lang["de"])
        css = (ROOT / "skills.css").read_text(encoding="utf-8")
        for domain in expected:
            self.assertIn(f'.skill-card[data-domain="{domain}"]', css)
        # Colors distinguish category only; the proficiency segments keep their shared color.
        self.assertIn(".segment.filled{background:#3bcc8e", css)
        self.assertIn("border-left:2px solid var(--domain-accent)", css)

    def test_skills_have_one_ordered_bilingual_source(self):
        data = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
        for lang in ("en", "de"):
            self.assertEqual(sum(len(s["items"]) for s in data[lang]["sections"]), 13)
        ids = lambda lang: [(s["id"], [i["id"] for i in s["items"]]) for s in data[lang]["sections"]]
        self.assertEqual(ids("en"), ids("de"))
        for lang in ("en", "de"):
            ratings = [i["rating_kind"] for section in data[lang]["sections"] for i in section["items"]]
            self.assertEqual(ratings.count("unrated"), 2)
            self.assertEqual(ratings.count("range"), 1)
            self.assertEqual(ratings.count("score"), 10)

    def test_committed_skills_pages_are_generated_without_drift(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/render_skills.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_old_skills_page_is_non_competing_redirect(self):
        legacy = (ROOT / "sites/skills.html").read_text(encoding="utf-8")
        self.assertIn('content="0; url=/skills.html"', legacy)
        self.assertIn('rel="canonical" href="https://cv.bytegeist.dev/skills.html"', legacy)
        self.assertIn('name="robots" content="noindex, follow"', legacy)
        projects = (ROOT / "sites/projects.html").read_text(encoding="utf-8")
        self.assertIn('href="/skills.html"', projects)

if __name__ == "__main__":
    unittest.main()
