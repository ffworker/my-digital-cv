# Skill evidence register — first audit (2026-11-01)

This is a **public, evidence-first inventory**, not a certificate and not a live infrastructure report. It informs the EN/DE source at `data/skills.json`; the rendered `skills.html` and `de/skills.html` are checked in and generated from that source.

## Evidence grades (do not conflate them)

| Grade | What it can demonstrate | What it cannot establish |
| --- | --- | --- |
| **Source** | Specific, inspectable implementation of a scenario | That it has ever been run |
| **Static validation defined** | A CI workflow, syntax check or automated assertion exists | That the latest run passed; that a real host worked |
| **Documented manual result** | The repo describes a test and its claimed outcome | Independent reproduction or a dated raw transcript |
| **Captured execution** | Dated run, exact source revision, sanitized command/result, observable success/failure | Broad competence outside the tested scope |
| **Private / gap** | Evidence is withheld or not yet collected | A publicly verified skill |

**Current state:** public CKA source and other selected implementation references exist; several infrastructure skills intentionally have no current public proof. This audit **does not assert a new successful deployment, CI run, restore, or failover test**. Do not upgrade a self-rating merely because a source link was added.

## Concrete scenarios and gaps

| Skill | Bounded scenario & source of evidence | Level now | Missing to demonstrate runtime behavior |
| --- | --- | --- | --- |
| Linux & shell | No public example selected; experience described, not independently documented | Private / gap | Sanitized real operations trace showing diagnosis and post-change checks |
| Networking | No public networking scenario selected; work examples remain private | Private / gap | Sanitized routing, DNS or firewall test with before/after verification |
| Docker / Compose | [Signaturee Linux test container](https://github.com/ffworker/signaturee-linux/blob/main/compose.yaml) has non-root, read-only root FS and runtime limits | Source | `docker compose config`, isolated run, functional test and sanitized logs |
| Kubernetes / Talos | [Service Endpoints mission](https://github.com/ffworker/cka-lab/blob/main/scenarios/service-endpoints/scenario.json) and [EndpointSlice validator](https://github.com/ffworker/cka-lab/blob/main/scenarios/service-endpoints/validate.sh); **not** proof of Talos operational expertise | Source + executable validation script | Captured inject → diagnose → fix → validator output; Talos live proof stays private until safely sanitized |
| Proxmox VE | Active private Proxmox operation; no publicly reproducible live evidence | Private / gap | Controlled VM/lifecycle test with anonymized results and explicit rollback |
| Terraform / OpenTofu | Lab experiments with AI-assisted IaC; no public scenario promoted | Private / gap | Isolated plan/apply/destroy evidence with bounded ownership checks |
| Ansible | Private Ansible use; no public reproducible scenario promoted | Private / gap | Sanitized playbook execution with independent outcome validation |
| SMB / NAS | Private operational setup; **no public test artifact** | Gap | Sanitized share/ACL test showing expected read/write/deny behavior and preservation after restart |
| NFS | Private NAS exports and mounts; **no public test artifact** | Gap | Allowed-client and denied-client checks, reboot/remount, read/write verification, measured restoration |
| Prometheus / Grafana | **No public alert-to-recovery artifact** | Gap | Test service stopped → alert triggered/delivered → service recovered → alert resolved; timestamps and rule link |
| NetBird / VPN | Private deployment; **no public connectivity/failover artifact** | Gap | Sanitized peer/ACL/routing connectivity test plus independent recovery-path demonstration |
| Git / GitHub Actions | [CV validation pipeline](https://github.com/ffworker/my-digital-cv/blob/main/.github/workflows/validate.yml), [regression suite](https://github.com/ffworker/my-digital-cv/blob/main/tests/test_site.py) and [successful run #41345106566](https://github.com/ffworker/my-digital-cv/actions/runs/41345106566) (generated EN/DE check + unit tests) | Source + **captured successful CI run** | Link the exact run to its source revision; production Talos promotion remains separate and unproven |
| Bash / scripting | Shell automation in practice; no publicly verified end-to-end example | Private / gap | Small auditable script plus actual result, error handling and test evidence |

## Capture one actual skill proof

Before marking a scenario as **captured execution**, record all of:

1. **Scope & question:** e.g. "Will the CKA factory refuse destroy when VM ID 320 is not owned by it?"
2. **Environment:** isolated test/lab; sanitized technology versions and architecture; confirm ownership/permission. No private addresses, hostnames or tokens.
3. **Starting state:** baseline snapshot/state and rollback path. Never provoke a failure on a production gateway/NAS/etcd control plane.
4. **Reproducible action:** exact command or linked test script, pinned source commit SHA and date.
5. **Observed evidence:** sanitized exit status, key output, expected vs actual checks, optional screenshot, relevant workflow run URL and whether it actually succeeded.
6. **Recovery and limit:** how the lab was returned to normal and what was **not** tested.
7. **Review:** separate privacy/security check before public link; the original operational proof may remain private.

**Strong example (future acceptance criterion, not a completed test):** intentionally give an isolated CKA test VM an unexpected ownership tag; run the safe preflight of `lab-down`; verify it refuses destruction, logs the guard condition, and the VM remains present. Record the actual return code, Git SHA and sanitized output. Do **not** do this test on a real unrelated VM.

## Publication workflow

- Project evidence lives next to the owning source/test wherever possible; avoid copying secrets or internal infra topology into this CV repository.
- Linear [BYT-91](https://linear.app/bytegeist/issue/BYT-91) tracks evidence promotion. Evidence is reviewed **per skill and per scenario**, not globally per repository.
- In `data/skills.json`, the EN and DE evidence fields must point to the **same concrete public resources** and describe the same status.
- `python scripts/render_skills.py`, `python scripts/render_skills.py --check`, then `python -m unittest discover -s tests -v` must pass before PR review.
- A merged CV source PR is **not** live: production still requires a separately approved commit pin in private `homelab-talos`, rollout and EN/DE browser verification.
- No automatic scoring or score promotion is proposed. Scores remain clearly marked subjective and need separate reassessment based on observed practice.
