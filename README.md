# Dennis Kappel — Digital CV

Source for **https://cv.bytegeist.dev**.

This is the human-readable side of my portfolio: current professional IT work, the infrastructure I run and learn from privately, and links to public repositories where there is useful technical evidence behind a claim.

[![Validate CV source](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml/badge.svg)](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml)

## Site structure

- `/` — English CV
- `/de/` — German CV
- `/skills.html` — public English **Editorial** skills page (canonical)
- `/de/skills.html` — public German **Editorial** skills page (canonical)
- `/skills-tech.html` — English original dark Console **Tech View** (noindex)
- `/de/skills-tech.html` — German original Console **Tech View** (noindex)
- `/field-notes.html` and `/de/field-notes.html` — **unlisted, noindex editorial previews** for future real-work case studies; no incidents published
- `/skills-professional.html` and `/de/skills-professional.html` — redirects from the earlier preview to the canonical pages

## Skills philosophy

The skills page separates what I can do myself, where I use documentation/search/AI, and how confident I would be making that kind of change on a real system.

**AI helps with professional research, troubleshooting, dashboard drafts, and iterative automation development.** It is not an autonomous operator of production systems: I make and carry out infrastructure decisions myself. I do not independently author scripts from scratch, and I don't present AI-generated code as proof of programming mastery. Autonomous AI-agent access is confined to disposable VMs/Pis in my private lab. The Editorial skills section foregrounds real professional administration; the Tech View retains separately labeled private lab self-assessments.

## Updating the bilingual skills matrix

The authoritative content lives in `data/skills.json`. The EN/DE pages are
checked-in, generated HTML so the runtime stays static and requires **no**
JavaScript or build step. Edit the relevant translated content there, keeping
both locales' skill IDs in the same order, then run:

```bash
python scripts/render_skills.py
python scripts/render_skills.py --check
python -m unittest discover -s tests -v
```

The Editorial hero now distinguishes **professional Windows/VDI/Microsoft 365 operations** from **private Linux/Proxmox/Kubernetes learning and automation**. This is presentation copy grounded in the existing CV, not a new certification or skill assessment. The methodology appears after the skills, and the original Tech View retains its old index and ordering.\n\nThe public `skills.html` / `de/skills.html` routes now use the **Editorial** style (`skills-professional.css`), while the dark Console pages remain available at `skills-tech.html` / `de/skills-tech.html` (`skills.css`). The editor and both views use only `data/skills.json` as the source of truth; `scripts/render_skills.py` generates **all four** views and the two legacy preview redirects. The Tech View is `noindex`, with a canonical link to the Editorial page. This is only a source-code route change; cluster deployment is a separately authorized revision pin in `homelab-talos`. To compare locally, run `python -m http.server 8765 --bind 127.0.0.1` and open the Editorial and Tech View URLs. Do not edit generated HTML by hand.

`templates/skills*.html` defines the shared native `<details>/<summary>`
cards. `skills.css` provides the compact dark console styling inspired by the
rest of the Bytegeist CV. The page requires no runtime JavaScript: the compact
bars show numeric ratings; a range is visualized with one uncertain segment,
and **not rated / AI-guided** has an unfilled dashed bar (no invented score).
Domain badges and subtle edge colors distinguish Linux, networking, platforms,
automation, storage, and monitoring. These colors **do not** indicate proficiency:
the same score-bar color and 0–10 scale are used everywhere. Domain identifiers
are shared between EN/DE; localized labels live in `data/skills.json`.
Click, tap or press Enter/Space on a card to inspect the existing full details.
The legacy `/sites/skills.html` links to the canonical `/skills.html`.

## Public technical evidence

- [CKA Lab](https://github.com/ffworker/cka-lab)
- [Bytegeist Docs](https://github.com/ffworker/bytegeist-docs)
- [GitHub profile](https://github.com/ffworker)

General infrastructure configuration remains private in `ffworker/infra-configs`. The current Talos deployment source is the separate private `ffworker/homelab-talos` repository.

## Skill evidence policy

The bilingual skills page now distinguishes a concrete **scenario/source reference** from a publicly captured runtime result. A source file or CI workflow definition is evidence of implementation, not proof that a deployment, restore, or test succeeded. Where evidence is private or absent, the skill card says so instead of linking to a repository homepage.

See the [skill evidence register](Documentations/skill-evidence-register.md) for scenario scope, evidence grade, missing proof and a reusable capture checklist. Self-ratings remain subjective; no score is automatically raised when a link is added. Both locales must reference the same concrete artifacts.

## Field Notes (unlisted preview)

The bilingual static pages `field-notes.html` and `de/field-notes.html` form the starting point for a carefully anonymised "diary of an IT administrator". The main EN/DE CV now includes a compact, deliberately non-identifying **Field Notes teaser** linking to those standalone blog-style previews. Both previews stay **`noindex` and absent from the sitemap**. There are no real case reports yet. Publishing even anonymised workplace/security incidents requires a separate factual, confidentiality and employer-approval review; the public repository must never contain an unreviewed draft or operational details. See [Field Notes publication standard](Documentations/field-notes-publication-policy.md).

## Validation and current deployment

This repository owns the CV content. It does not deploy directly to Kubernetes.

The CV now runs on Kubernetes with Talos Linux. The deployment source is the private `ffworker/homelab-talos` repository; the CV deployment pins an exact source commit for git-sync. Nginx serves that checkout through the existing Cloudflare Tunnel. The former Pi k3s/Argo CD route is historical, not the current deployment path.

The source workflow validates pull requests and relevant pushes to `main`. It
does not promote deployments. A content update needs separate approval, source
validation and an explicit revision update in the `homelab-talos` deployment
source, followed by rollout and browser verification.

```text
my-digital-cv exact source commit
  -> explicit revision pin in homelab-talos
  -> Talos Kubernetes / git-sync / nginx
  -> existing Cloudflare Tunnel
  -> cv.bytegeist.dev
```

GitHub Pages and Cloudflare Pages are not part of the production path. No
automatic CV-to-cluster promotion is implemented in this repository.

## Local verification

```bash
python -m unittest discover -s tests -v
python -m http.server 8765 --bind 127.0.0.1
```

Preview `/`, `/de/index.html`, `/skills.html`, `/de/skills.html`, `/skills-tech.html` and `/de/skills-tech.html`. The optional cluster peek requests `/lab-health.json`; the static preview has no telemetry backend and must show an unavailable state rather than invented live results.
