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

The skills page deliberately separates three things:

1. what I can do myself,
2. where I use documentation, search or AI assistance,
3. how confident I would be making that kind of change on a real system.

AI is useful in my workflow, but generated output is not treated as competence by itself. If I cannot explain and verify a change, it belongs in a lab or sandbox first.

## Public technical evidence

- [CKA Lab](https://github.com/ffworker/cka-lab) — Kubernetes break/fix learning against real cluster state.
- [Proxmox Lab](https://github.com/ffworker/proxmox-lab) — disposable infrastructure using Terraform/OpenTofu, Ansible and Cloud-Init.
- [Bytegeist Docs](https://github.com/ffworker/bytegeist-docs) — documentation validation and controlled delivery.
- [GitHub profile](https://github.com/ffworker) — technical entry point to the public work.

`ffworker/infra-configs` remains private as operational source-of-truth. Public portfolio evidence is intentionally split into focused repositories instead of publishing live infrastructure configuration.

## Deployment

Pull requests run validation. Every push to `main` runs the same validation and, if it passes, deploys that exact commit to GitHub Pages.
