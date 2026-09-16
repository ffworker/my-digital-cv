# Dennis Kappel — Digital CV

Source for **https://cv.bytegeist.dev**.

This is the human-readable side of my portfolio: current professional IT work, the infrastructure I run and learn from privately, and links to public repositories where there is useful technical evidence behind a claim.

[![Validate CV and promote GitOps revision](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml/badge.svg)](https://github.com/ffworker/my-digital-cv/actions/workflows/validate.yml)

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

`ffworker/infra-configs` remains private as the deployment source-of-truth.

## CI/CD and GitOps deployment

This repository owns the CV content. It does not deploy directly to Kubernetes.

Pull requests validate only. A validated push to `main` sends the exact source commit SHA to `ffworker/infra-configs` using `repository_dispatch`.

`infra-configs` validates that exact revision, pins the SHA in the CV Kubernetes desired state, renders the Kustomize application and commits the promotion. GitHub Actions stops there.

Argo CD runs inside the Pi k3s cluster, watches `infra-configs`, and reconciles the isolated CV application automatically. The public hostname continues to use the existing Cloudflare Tunnel:

```text
my-digital-cv
  -> validation
  -> infra-configs desired-state commit
  -> Argo CD
  -> Pi k3s
  -> existing Cloudflare Tunnel
  -> cv.bytegeist.dev
```

GitHub Pages and Cloudflare Pages are not part of the production path.
