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
            title, description = short_skill(item)
            score, label, segments = rating_display(item)
            rows.append(fill(row, {
                "SKILL_ID": item["id"],
                "RATING_KIND": item["rating_kind"],
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
        "LEGEND": locale["legend"],
        "SECTIONS": "\n".join(rendered_sections), "FOOTER": locale["footer"],
    })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed HTML is stale")
    args = parser.parse_args()
    data = json.loads((ROOT / "data/skills.json").read_text(encoding="utf-8"))["locales"]
    ids = {
        lang: [(group["id"], [item["id"] for item in group["items"]]) for group in loc["sections"]]
        for lang, loc in data.items()
    }
    if set(data) != {"en", "de"} or ids["en"] != ids["de"]:
        raise ValueError("English and German skill IDs/order must match")
    templates = {
        name: (ROOT / f"templates/{name}").read_text(encoding="utf-8")
        for name in ("skills.html", "skills-section.html", "skills-row.html")
    }
    for lang, target in (("en", "skills.html"), ("de", "de/skills.html")):
        content = render(data[lang], templates["skills.html"],
                         templates["skills-section.html"], templates["skills-row.html"])
        path = ROOT / target
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                print(f"Out-of-date generated page: {target}", file=sys.stderr)
                return 1
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Rendered {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
