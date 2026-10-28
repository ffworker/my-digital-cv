# Dennis Kappel — Digital CV

Source for **https://cv.bytegeist.dev**.

This is the human-readable side of my portfolio: current professional IT work, the infrastructure I run and learn from privately, and links to public repositories where there is useful technical evidence behind a claim.

[![Validate CV source](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml/badge.svg)](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml)

## Site structure

- `/` — English CV
- `/de/` — German CV
- `/skills.html` — detailed, self-assessed technical depth
- `/de/skills.html` — German self-assessment

## Skills philosophy

The skills page separates what I can do myself, where I use documentation/search/AI, and how confident I would be making that kind of change on a real system.

AI is useful in my workflow, but generated output is not treated as competence by itself. If I cannot explain and verify a change, it belongs in a lab or sandbox first.

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

`templates/skills*.html` defines the shared page/table markup, and
`skills.css` provides the matrix styling. A numeric score, an approximate
range, and **not rated / AI-guided** are deliberately different states; do
not fabricate a score for early-stage skills. The legacy `/sites/skills.html`
links to the current canonical `/skills.html`.

## Public technical evidence

- [CKA Lab](https://github.com/ffworker/cka-lab)
- [Proxmox Lab](https://github.com/ffworker/proxmox-lab)
- [Bytegeist Docs](https://github.com/ffworker/bytegeist-docs)
- [GitHub profile](https://github.com/ffworker)

General infrastructure configuration remains private in `ffworker/infra-configs`. The current Talos deployment source is the separate private `ffworker/homelab-talos` repository.

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

Preview `/`, `/de/index.html`, `/skills.html` and `/de/skills.html`. The optional cluster peek requests `/lab-health.json`; the static preview has no telemetry backend and must show an unavailable state rather than invented live results.
