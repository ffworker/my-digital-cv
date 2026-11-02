"""Render bilingual static, accessible skills dashboards from the curated source.

Usage:
    python scripts/render_skills.py
    python scripts/render_skills.py --check
"""
from __future__ import annotations

import argparse
import html
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


def render_editorial_variant(content: str, locale: dict) -> str:
    """Recruiter-first Editorial page; retain the technical cards as a separate index."""
    lang = locale["lang"]
    technical_path = "/skills-tech.html" if lang == "en" else "/de/skills-tech.html"
    if lang == "en":
        eyebrow = "PROFESSIONAL PROFILE"
        heading = "Infrastructure / Systems Engineer"
        intro = (
            "I run, maintain and troubleshoot inherited and evolving IT systems. "
            "VMware, Linux, Docker, Windows/identity, VDI, firewalls and real restores "
            "are part of my professional work. Kubernetes and other experimental "
            "platform tooling belong to my private lab."
        )
        view_label, technical_label = "View", "Tech View"
        context_label = "Two contexts"
        professional_label, private_label = "Professional IT operations", "Private infrastructure lab"
        professional_detail = "VMware · Linux / Docker · Windows / AD / Entra · Horizon / VDI · Veeam"
        private_detail = "Proxmox · Kubernetes / Talos · GitOps · Ansible / OpenTofu"
        career_label, career_url = "Read professional experience", "/#professional"
    else:
        eyebrow = "BERUFLICHES PROFIL"
        heading = "Infrastructure / Systems Engineer"
        intro = (
            "Ich betreibe, pflege und analysiere bestehende und wachsende IT-Systeme. "
            "VMware, Linux, Docker, Windows/Identity, VDI, Firewalls und echte Restores "
            "gehören zu meiner beruflichen Praxis. Kubernetes und andere experimentelle "
            "Plattformwerkzeuge nutze ich ausschließlich privat."
        )
        view_label, technical_label = "Ansicht", "Tech View"
        context_label = "Zwei Bereiche"
        professional_label, private_label = "Beruflicher IT-Betrieb", "Privates Infrastruktur-Lab"
        professional_detail = "VMware · Linux / Docker · Windows / AD / Entra · Horizon / VDI · Veeam"
        private_detail = "Proxmox · Kubernetes / Talos · GitOps · Ansible / OpenTofu"
        career_label, career_url = "Berufliche Erfahrung ansehen", "/de/index.html#professional"

    # Use hiring-oriented metadata and a clear professional header on Editorial.
    if lang == "en":
        page_title = "Dennis Kappel | Infrastructure / Systems Engineer skills"
        page_description = (
            "Hands-on professional VMware, Linux, Docker, AD, VDI, FortiGate and Veeam operations; "
            "private Kubernetes and IaC practice clearly separated."
        )
        og_title = "Dennis Kappel | Infrastructure & operations experience"
        old_brand, new_brand = "Dennis Kappel · technical depth", "Dennis Kappel · professional profile"
    else:
        page_title = "Dennis Kappel | Infrastructure / Systems Engineer · Kompetenzen"
        page_description = (
            "Berufliche Praxis mit VMware, Linux, Docker, AD, VDI, FortiGate und Veeam; "
            "private Kubernetes- und IaC-Projekte klar getrennt."
        )
        og_title = "Dennis Kappel | Infrastruktur & Betriebspraxis"
        old_brand, new_brand = "Dennis Kappel · technische Tiefe", "Dennis Kappel · Kompetenzprofil"
    content = content.replace(f'<title>{locale["page_title"]}</title>',
                              f'<title>{page_title}</title>', 1)
    content = content.replace(
        f'<meta name="description" content="{locale["description"]}" />',
        f'<meta name="description" content="{page_description}" />', 1,
    )
    content = content.replace(
        f'<meta property="og:title" content="{locale["og_title"]}" />',
        f'<meta property="og:title" content="{og_title}" />', 1,
    )
    content = content.replace(f'<strong>{old_brand}</strong>',
                              f'<strong>{new_brand}</strong>', 1)

    content = content.replace(
        '<link rel="stylesheet" href="/skills.css" />',
        '<link rel="stylesheet" href="/skills-professional.css" />', 1,
    )
    content = content.replace('<body class="skills-page">',
                              '<body class="skills-page skills-professional">', 1)
    content = content.replace(f'<p class="eyebrow">{locale["eyebrow"]}</p>',
                              f'<p class="eyebrow">{eyebrow}</p>', 1)
    content = content.replace(f'<h1 id="skills-title">{locale["headline"]}</h1>',
                              f'<h1 id="skills-title">{heading}</h1>', 1)
    content = content.replace(f'<p class="intro">{locale["intro"]}</p>',
                              f'<p class="intro">{intro}</p>', 1)

    # Replace résumé-irrelevant numeric counters with two clear work contexts.
    context = (
        '<aside class="experience-panel" aria-label="' + context_label + '">'
        '<p class="context-kicker">' + context_label + '</p>'
        '<div class="context-item"><strong>' + professional_label + '</strong>'
        '<p>' + professional_detail + '</p></div>'
        '<div class="context-item"><strong>' + private_label + '</strong>'
        '<p>' + private_detail + '</p></div>'
        f'<a class="context-link" href="{career_url}">{career_label} →</a>'
        '</aside>\n'
    )
    panel_start = content.index('<div class="index-panel"')
    panel_end = content.index('      </div>\n    </section>', panel_start)
    content = content[:panel_start] + context + content[panel_end:]

    # Show the skills immediately after the intro. Methodology remains available,
    # but no longer takes precedence over hands-on experience and evidence.
    method_start = content.index('    <details class="methodology">')
    method_end = content.index('    </details>\n', method_start) + len('    </details>\n')
    method_html = content[method_start:method_end]
    content = content[:method_start] + content[method_end:]
    footer_start = content.index('    <footer class="footer-note">')
    content = content[:footer_start] + method_html + content[footer_start:]

    practice = locale["editorial_practice"]
    practice_cards = "\n".join(
        '        <article class="practice-card">'
        f'<span class="practice-meta">{html.escape(item["tag"])}</span>'
        f'<h3>{html.escape(item["title"])}</h3>'
        f'<p>{html.escape(item["description"])}</p>'
        '</article>'
        for item in practice["items"]
    )
    practice_markup = (
        '\n    <section class="practice-section" aria-labelledby="practice-title">\n'
        '      <div class="practice-intro">'
        f'<p class="practice-kicker">{html.escape(practice["eyebrow"])}</p>'
        f'<h2 id="practice-title">{html.escape(practice["heading"])}</h2>'
        f'<p>{html.escape(practice["description"])}</p></div>\n'
        f'      <div class="practice-grid">\n{practice_cards}\n      </div>\n'
        '    </section>\n'
        '    <div class="lab-index-note">'
        f'<h2>{html.escape(practice["lab_heading"])}</h2>'
        f'<p>{html.escape(practice["lab_description"])}</p></div>\n'
    )
    content = content.replace('    <section class="skill-group"',
                              practice_markup + '    <section class="skill-group"', 1)

    switch = (
        '<nav class="theme-switch" aria-label="Skills view">'
        f'<span class="theme-label">{view_label}</span>'
        '<span class="theme-options">'
        '<span class="current" aria-current="page">Editorial</span>'
        f'<a href="{technical_path}">{technical_label}</a>'
        '</span></nav>'
    )
    return content.replace('</header>', f'</header>\n  {switch}', 1)


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
    switch = (
        '<nav class="tech-view-choice" aria-label="Skills view">'
        f'<a href="{canonical}">← {label}</a>'
        '<span aria-current="page">Tech View</span></nav>'
    )
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
