"""Render bilingual static, accessible skills dashboards from the curated source.

Usage:
    python scripts/render_skills.py
    python scripts/render_skills.py --check
"""
from __future__ import annotations

import argparse
import html
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
SKILL = re.compile(r"<strong>(.*?)</strong><span>(.*?)</span>", re.DOTALL)
SCORE = re.compile(r'<span class="score-number(?: score-unrated)?">([^<]+)</span>')
RATING_LABEL = re.compile(r'<span class="rating-label">([^<]+)</span>')


def fill(template: str, values: dict[str, object]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise ValueError(f"missing template value: {key}")
        return str(values[key])
    return TOKEN.sub(replace, template)


def short_skill(item: dict) -> tuple[str, str]:
    match = SKILL.fullmatch(item["skill"])
    if not match:
        raise ValueError(f"invalid skill title/description for {item['id']}")
    return tuple(html.escape(html.unescape(part), quote=False) for part in match.groups())


def rating_display(item: dict) -> tuple[str, str, str]:
    score_match = SCORE.search(item["rating"])
    label_match = RATING_LABEL.search(item["rating"])
    if not score_match or not label_match:
        raise ValueError(f"invalid rating for {item['id']}")
    score, label = score_match.group(1), label_match.group(1)
    kind = item["rating_kind"]
    if kind == "score":
        match = re.fullmatch(r"(\d+)/10", score)
        if not match:
            raise ValueError(f"invalid numeric rating for {item['id']}")
        filled, possible = int(match.group(1)), 0
    elif kind == "range":
        match = re.fullmatch(r"(\d+)[–-](\d+)/10", score)
        if not match:
            raise ValueError(f"invalid range rating for {item['id']}")
        filled, possible = map(int, match.groups())
        possible -= filled
    elif kind == "unrated":
        filled, possible = 0, 0
    else:
        raise ValueError(f"unknown rating kind: {kind}")
    if not 0 <= filled <= 10 or not 0 <= possible <= 10 - filled:
        raise ValueError(f"out-of-range self-rating for {item['id']}")
    segments = "".join(
        f'<i class="segment {"filled" if i < filled else "possible" if i < filled + possible else "empty"}"></i>'
        for i in range(10)
    )
    return html.escape(score), html.escape(label), segments


def render(locale: dict, page: str, section: str, row: str) -> str:
    ui = locale["ui"]
    rendered_sections = []
    all_items = [item for group in locale["sections"] for item in group["items"]]
    for group in locale["sections"]:
        rows = []
        for item in group["items"]:
            domain = item["domain"]
            if domain not in ui["domains"]:
                raise ValueError(f"unknown skill domain: {domain}")
            title, description = short_skill(item)
            score, label, segments = rating_display(item)
            rows.append(fill(row, {
                "SKILL_ID": item["id"],
                "RATING_KIND": item["rating_kind"],
                "DOMAIN": domain, "DOMAIN_LABEL": html.escape(ui["domains"][domain]),
                "SKILL_TITLE": title, "SKILL_DESCRIPTION": description,
                "SCORE": score, "RATING_LABEL": label, "SEGMENTS": segments,
                "ASSIST": item["assist"], "PRODUCTION": item["production"],
                "EVIDENCE": item["evidence"],
                "WORK_LABEL": ui["work_label"], "PROD_LABEL": ui["prod_label"],
                "EVIDENCE_LABEL": ui["evidence_label"],
            }))
        rendered_sections.append(fill(section, {
            "SECTION_ID": group["id"], "SECTION_TITLE": group["title"],
            "GROUP_COUNT": len(group["items"]), "COUNT_LABEL": ui["count_label"],
            "ROWS": "\n".join(rows),
        }))
    return fill(page, {
        "LANG": locale["lang"],
        "PAGE_TITLE": locale["page_title"],
        "PAGE_PATH": "skills.html" if locale["lang"] == "en" else "de/skills.html",
        "DESCRIPTION": locale["description"], "OG_TITLE": locale["og_title"],
        "OG_DESCRIPTION": locale["og_description"],
        "SKIP_LABEL": ui["skip_label"], "HEADER": locale["header"],
        "EYEBROW": locale["eyebrow"], "HEADLINE": locale["headline"],
        "INTRO": locale["intro"], "INDEX_LABEL": ui["index_label"],
        "TOTAL_COUNT": len(all_items),
        "SCORED_COUNT": sum(item["rating_kind"] in ("score", "range") for item in all_items),
        "UNRATED_COUNT": sum(item["rating_kind"] == "unrated" for item in all_items),
        "TOTAL_LABEL": ui["total_label"], "SCORED_LABEL": ui["scored_label"],
        "UNRATED_LABEL": ui["unrated_label"], "INDEX_HINT": ui["index_hint"],
        "METHOD_LABEL": ui["method_label"], "NOTE": locale["note"],
        "CATEGORY_HINT": ui["category_hint"],
        "LEGEND": locale["legend"],
        "SECTIONS": "\n".join(rendered_sections), "FOOTER": locale["footer"],
    })


def stylesheet_version(filename: str) -> str:
    """Fingerprint stylesheet content to avoid stale browser CSS after releases."""
    data = (ROOT / filename).read_bytes()
    # Git object hash matches the blob SHA for this stylesheet in GitHub.
    git_header = f"blob {len(data)}\\0".encode()
    return hashlib.sha1(git_header + data).hexdigest()[:12]


def render_editorial_variant(content: str, locale: dict) -> str:
    """A short human editorial profile. Full self-assessment lives in Tech View."""
    lang = locale["lang"]
    de = lang == "de"
    practice = locale["editorial_practice"]
    escape = html.escape

    technical_path = "/de/skills-tech.html" if de else "/skills-tech.html"
    career_url = "/de/index.html#professional" if de else "/#professional"
    role = "BERUFLICH / INFRASTRUKTUR" if de else "PROFESSIONAL / INFRASTRUCTURE"
    context_label = "Zwei Welten" if de else "Two contexts"
    professional_label = "Im Beruf" if de else "At work"
    private_label = "Im eigenen Lab" if de else "In my lab"
    professional_detail = "VMware · Linux / Docker · AD / Entra · VDI · Veeam"
    private_detail = "Proxmox · Talos / Kubernetes · GitOps · IaC"
    scroll_label = "Meine Arbeit ansehen" if de else "See what I do"
    view_label = "Ansicht" if de else "View"
    technical_label = "Tech View"
    career_label = "Zur beruflichen Erfahrung" if de else "Back to my experience"
    page_title = (
        "Dennis Kappel | Infrastructure / Systems Engineer · Praxis"
        if de else "Dennis Kappel | Infrastructure / Systems Engineer · Practical skills"
    )
    page_description = (
        "Ein persönlicher Einblick in berufliche VMware-, Linux-, Docker-, AD-, "
        "VDI- und Backup-Praxis. Private Kubernetes-/GitOps-Projekte separat."
        if de else
        "A human look at real VMware, Linux, Docker, identity, VDI and backup "
        "work, with private Kubernetes and GitOps experiments kept separate."
    )
    brand = "Dennis Kappel · Kompetenzprofil" if de else "Dennis Kappel · professional profile"

    # Keep the generated, accessible header/canonical language links. Replace
    # only editorial metadata; Tech View stays the canonical technical source.
    prefix = content[:content.index('    <section class="masthead"')]
    prefix = prefix.replace(f'<title>{locale["page_title"]}</title>',
                            f'<title>{escape(page_title)}</title>', 1)
    prefix = prefix.replace(
        f'<meta name="description" content="{locale["description"]}" />',
        f'<meta name="description" content="{escape(page_description)}" />', 1)
    prefix = prefix.replace(
        f'<meta property="og:title" content="{locale["og_title"]}" />',
        f'<meta property="og:title" content="{escape(page_title)}" />', 1)
    prefix = prefix.replace(
        f'<meta property="og:description" content="{locale["og_description"]}" />',
        f'<meta property="og:description" content="{escape(page_description)}" />', 1)
    old_brand = "Dennis Kappel · technische Tiefe" if de else "Dennis Kappel · technical depth"
    prefix = prefix.replace(f'<strong>{old_brand}</strong>',
                            f'<strong>{brand}</strong>', 1)
    prefix = prefix.replace(
        '<link rel="stylesheet" href="/skills.css" />',
        f'<link rel="stylesheet" href="/skills-professional.css?v={stylesheet_version("skills-professional.css")}" />', 1)
    prefix = prefix.replace('<body class="skills-page">',
                            '<body class="skills-page skills-professional">', 1)
    switch = (
        '<nav class="theme-switch" aria-label="Skills view">'
        f'<span class="theme-label">{view_label}</span>'
        '<span class="theme-options">'
        '<span class="current" aria-current="page">Editorial</span>'
        f'<a href="{technical_path}">{technical_label}</a>'
        '</span></nav>'
    )
    prefix = prefix.replace('</header>', f'</header>\n  {switch}', 1)

    hero = (
        '    <section class="masthead" aria-labelledby="skills-title">\n'
        '      <div class="hero-layout">\n'
        '        <div class="hero-copy">'
        f'<p class="eyebrow">{role}</p>'
        f'<h1 id="skills-title">{escape(practice["hero_title"])}</h1>'
        f'<p class="intro">{escape(practice["hero_lead"])}</p>'
        f'<a class="scroll-link" href="#practice-title">{scroll_label}<span aria-hidden="true"> ↓</span></a>'
        '</div>\n'
        f'        <aside class="experience-panel" aria-label="{context_label}">'
        f'<p class="context-kicker">{escape(practice["hero_note_label"])}</p>'
        f'<p class="hero-note-text">{escape(practice["hero_note"])}</p>'
        '<div class="contexts">'
        f'<div class="context-item"><strong>{professional_label}</strong>'
        f'<p>{professional_detail}</p></div>'
        f'<div class="context-item"><strong>{private_label}</strong>'
        f'<p>{private_detail}</p></div></div>'
        '</aside>\n'
        '      </div>\n'
        '    </section>\n'
    )
    story = (
        '    <section class="professional-story" aria-labelledby="story-title">\n'
        '      <div class="story-heading">'
        f'<p class="story-kicker">{escape(practice["story_kicker"])}</p>'
        f'<h2 id="story-title">{escape(practice["story_title"])}</h2>'
        '</div>'
        '<div class="story-body">'
        f'<p>{escape(practice["story_text"])}</p>'
        '<div class="story-note">'
        f'<span>{escape(practice["story_note_label"])}</span>'
        f'<p>{escape(practice["story_note"])}</p></div>'
        '</div>\n'
        '    </section>\n'
    )
    section_head = (
        '    <section class="practice-section" aria-labelledby="practice-title">\n'
        '      <div class="practice-intro">'
        f'<p class="practice-kicker">{escape(practice["section_kicker"])}</p>'
        f'<h2 id="practice-title">{escape(practice["section_title"])}</h2>'
        f'<p>{escape(practice["section_description"])}</p>'
        '</div>\n'
    )
    items = {item["id"]: item for item in practice["items"]}
    seen = []
    chapters = []
    for group in practice["groups"]:
        rows = []
        for key in group["ids"]:
            item = items[key]
            seen.append(key)
            rows.append(
                '          <article class="capability">'
                '<div class="capability-heading">'
                f'<h3>{escape(item["title"])}</h3>'
                f'<span class="capability-tag">{escape(item["tag"])}</span>'
                '</div>'
                f'<p>{escape(item["description"])}</p>'
                '</article>'
            )
        chapters.append(
            f'      <section class="practice-chapter" aria-labelledby="chapter-{group["id"]}">'
            '<div class="chapter-rail">'
            f'<span class="chapter-number">{escape(group["number"])} / 03</span>'
            f'<h3 id="chapter-{group["id"]}">{escape(group["title"])}</h3>'
            f'<p>{escape(group["intro"])}</p>'
            '</div>'
            '<div class="chapter-list">\n'
            + '\n'.join(rows) + '\n'
            '</div></section>\n'
        )
    if len(seen) != len(items) or set(seen) != set(items) or len(set(seen)) != len(seen):
        raise ValueError("Editorial group items must cover each skill exactly once")
    chapter_content = section_head + ''.join(chapters) + '    </section>\n'

    lab = (
        '    <aside class="lab-gateway" id="lab-depth">'
        '<div class="lab-gateway-copy">'
        f'<p class="lab-kicker">{escape(practice["lab_kicker"])}</p>'
        f'<h2>{escape(practice["lab_heading"])}</h2>'
        f'<p>{escape(practice["lab_description"])}</p>'
        '</div>'
        '<div class="lab-gateway-actions">'
        f'<a href="{technical_path}">{escape(practice["lab_action"])}<span aria-hidden="true"> ↗</span></a>'
        f'<a class="quiet-link" href="{career_url}">{career_label}</a>'
        '</div></aside>\n'
    )
    footer = (
        '    <footer class="footer-note">'
        f'{escape(practice["footer"])}</footer>\n'
        '  </main>\n</div>\n</body>\n</html>\n'
    )
    return prefix + hero + story + chapter_content + lab + footer


def render_tech_variant(content: str, locale: dict) -> str:
    """Original console design, kept as an alternate non-indexed view."""
    lang = locale["lang"]
    canonical = "/skills.html" if lang == "en" else "/de/skills.html"
    original_other = "/de/skills.html" if lang == "en" else "/skills.html"
    tech_other = "/de/skills-tech.html" if lang == "en" else "/skills-tech.html"
    label = "Editorial view" if lang == "en" else "Professionelle Ansicht"
    content = content.replace(
        '<meta name="robots" content="index, follow" />',
        '<meta name="robots" content="noindex, follow" />', 1,
    )
    content = content.replace(f'href="{original_other}"',
                              f'href="{tech_other}"', 1)
    content = content.replace('<body class="skills-page">',
                              '<body class="skills-page skills-tech">', 1)
    content = content.replace(
        '<link rel="stylesheet" href="/skills.css" />',
        f'<link rel="stylesheet" href="/skills.css?v={stylesheet_version("skills.css")}" />', 1,
    )
    switch = (
        '<nav class="tech-view-choice" aria-label="Skills view">'
        f'<a href="{canonical}">← {label}</a>'
        '<span aria-current="page">Tech View</span></nav>'
    )
    if lang == "de":
        guide = (
            '<div class="tech-reading-guide">'
            '<p>Berufspraxis und privates Homelab sind klar getrennt. '
            'Die Zahlen sind subjektive Selbsteinschätzungen, keine Zertifikate.</p>'
            '<nav aria-label="Kapitelübersicht">'
            '<a href="#skills-infrastructure">Infrastruktur</a>'
            '<a href="#skills-delivery">Tooling</a>'
            '</nav></div>\n'
        )
    else:
        guide = (
            '<div class="tech-reading-guide">'
            '<p>Professional work and private lab practice are distinct. '
            'Numbers are subjective self-ratings, not certifications.</p>'
            '<nav aria-label="Section navigation">'
            '<a href="#skills-infrastructure">Infrastructure</a>'
            '<a href="#skills-delivery">Tooling</a>'
            '</nav></div>\n'
        )
    content = content.replace('    <details class="methodology">',
                              '    ' + guide + '    <details class="methodology">', 1)
    return content.replace('</header>', f'</header>\n  {switch}', 1)


def render_preview_redirect(lang: str) -> str:
    """Legacy preview URLs resolve to the new canonical editorial URL."""
    target = "/skills.html" if lang == "en" else "/de/skills.html"
    title = "Skills moved" if lang == "en" else "Kompetenzen umgezogen"
    label = "Open skills" if lang == "en" else "Kompetenzen öffnen"
    return (
        f'<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n'
        '<meta charset="UTF-8" />\n'
        f'<meta http-equiv="refresh" content="0; url={target}" />\n'
        '<meta name="robots" content="noindex, follow" />\n'
        f'<link rel="canonical" href="https://cv.bytegeist.dev{target}" />\n'
        f'<title>{title}</title>\n'
        '</head>\n<body>\n'
        f'<p><a href="{target}">{label}</a></p>\n'
        '</body>\n</html>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed HTML is stale")
    args = parser.parse_args()
    data = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
    ids = {
        lang: [(group["id"], [item["id"] for item in group["items"]]) for group in loc["sections"]]
        for lang, loc in data.items()
    }
    domains = {
        lang: [(item["id"], item["domain"]) for section in loc["sections"]
               for item in section["items"]]
        for lang, loc in data.items()
    }
    if set(data) != {"en", "de"} or ids["en"] != ids["de"] or domains["en"] != domains["de"]:
        raise ValueError("English and German skill IDs/order must match")
    templates = {
        name: (ROOT / f"templates/{name}").read_text(encoding="utf-8")
        for name in ("skills.html", "skills-section.html", "skills-row.html")
    }
    for lang, target in (("en", "skills.html"), ("de", "de/skills.html")):
        content = render(data[lang], templates["skills.html"],
                         templates["skills-section.html"], templates["skills-row.html"])
        tech_target = target.replace("skills.html", "skills-tech.html")
        preview_alias = target.replace("skills.html", "skills-professional.html")
        editorial = render_editorial_variant(content, data[lang])
        tech = render_tech_variant(content, data[lang])
        alias = render_preview_redirect(lang)
        for output, rendered in ((target, editorial), (tech_target, tech), (preview_alias, alias)):
            output_path = ROOT / output
            if args.check:
                if not output_path.is_file() or output_path.read_text(encoding="utf-8") != rendered:
                    print(f"Out-of-date generated page: {output}", file=sys.stderr)
                    return 1
            else:
                output_path.write_text(rendered, encoding="utf-8")
                print(f"Rendered {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
