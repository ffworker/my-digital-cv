# Dennis Kappel — Digital CV

Source for **https://cv.bytegeist.dev**.

This is the human-readable side of my portfolio: current professional IT work, the infrastructure I run and learn from privately, and links to public repositories where there is useful technical evidence behind a claim.

[![Validate and deploy website](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml/badge.svg)](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml)

## Site structure

- `/` — English CV
- `/de/` — German CV
- `/skills.html` — detailed, self-assessed technical depth
- `/de/skills.html` — German self-assessment

## Skills philosophy

The skills page separates what I can do myself, where I use documentation/search/AI, and how confident I would be making that kind of change on a real system.

AI is useful in my workflow, but generated output is not treated as competence by itself. If I cannot explain and verify a change, it belongs in a lab or sandbox first.

## Public technical evidence

- [CKA Lab](https://github.com/ffworker/cka-lab)
- [Proxmox Lab](https://github.com/ffworker/proxmox-lab)
- [Bytegeist Docs](https://github.com/ffworker/bytegeist-docs)
- [GitHub profile](https://github.com/ffworker)

`ffworker/infra-configs` remains private as operational source-of-truth.

## Deployment

Pull requests validate. Every push to `main` validates and then deploys that exact commit to GitHub Pages.
