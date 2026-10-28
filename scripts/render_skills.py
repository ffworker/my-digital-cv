"""Render bilingual static skills pages from one content source (stdlib only).

Usage:
    python scripts/render_skills.py
    python scripts/render_skills.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def fill(template: str, values: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise ValueError(f"missing template value: {key}")
        return str(values[key])
    return TOKEN.sub(replace, template)


def render(locale: dict, page: str, section: str, row: str) -> str:
    rendered_sections = []
    for group in locale["sections"]:
        cols = group["columns"]
        if len(cols) != 5:
            raise ValueError("skills sections must have exactly five columns")
        rows = [
            fill(row, {
                "SKILL_ID": item["id"], "SKILL": item["skill"],
                "RATING": item["rating"], "RATING_KIND": item["rating_kind"],
                "ASSIST": item["assist"], "PRODUCTION": item["production"],
                "EVIDENCE": item["evidence"],
                **{f"C{i}": cols[i] for i in range(1, 5)},
            })
            for item in group["items"]
        ]
        rendered_sections.append(fill(section, {
            "SECTION_ID": group["id"], "SECTION_TITLE": group["title"],
            "ROWS": "\n".join(rows),
            **{f"C{i}": cols[i] for i in range(5)},
        }))
    return fill(page, {
        "LANG": locale["lang"], "PAGE_TITLE": locale["page_title"],
        "PAGE_PATH": "skills.html" if locale["lang"] == "en" else "de/skills.html",
        "DESCRIPTION": locale["description"], "OG_TITLE": locale["og_title"],
        "OG_DESCRIPTION": locale["og_description"], "HEADER": locale["header"],
        "EYEBROW": locale["eyebrow"], "HEADLINE": locale["headline"],
        "INTRO": locale["intro"], "NOTE": locale["note"],
        "LEGEND": locale["legend"], "SECTIONS": "\n".join(rendered_sections),
        "FOOTER": locale["footer"],
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed HTML is stale")
    args = parser.parse_args()
    data = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
    section_ids = {
        lang: [(group["id"], [item["id"] for item in group["items"]]) for group in locale["sections"]]
        for lang, locale in data.items()
    }
    if set(data) != {"en", "de"} or section_ids["en"] != section_ids["de"]:
        raise ValueError("English and German skills IDs/order must match")
    templates = {
        name: (ROOT / f"templates/{name}").read_text(encoding="utf-8")
        for name in ("skills.html", "skills-section.html", "skills-row.html")
    }
    for lang, target in (("en", "skills.html"), ("de", "de/skills.html")):
        html = render(data[lang], templates["skills.html"],
                      templates["skills-section.html"], templates["skills-row.html"])
        path = ROOT / target
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != html:
                print(f"Out-of-date generated page: {target}", file=sys.stderr)
                return 1
        else:
            path.write_text(html, encoding="utf-8")
            print(f"Rendered {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
