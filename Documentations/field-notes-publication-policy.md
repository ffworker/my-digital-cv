# Field Notes: publication standard (editorial workflow, not a case report)

The /field-notes.html and /de/field-notes.html pages are linked from a tasteful bilingual CV teaser, but deliberately remain **noindex editorial previews** until a first approved case study exists. They contain **no real incident details**, customer data or production artifacts.

## Purpose

Short, grounded first-person reflections on unusual IT operations situations: a problem or decision, what can safely be explained, a verified result, and a useful lesson. This is **not** a security incident disclosure channel or a company status page.

## Confidentiality & approval gate — must pass before any real case

1. Identify employer, client, supplier and any third-party duties of confidentiality; get appropriate authorization where required, **before publishing**, not as an afterthought.
2. Assess whether even the combination of a technology, industry, timeframe and symptoms could identify the organisation or incident. Anonymising IP addresses alone is insufficient.
3. Never include names, customer counts, screenshots, internal tickets, topology, versions/CVEs, attack indicators, vulnerabilities, security controls, exact dates/timings, communications, credentials, logs, internal addresses or incident response chronology unless publicly disclosed and explicitly cleared.
4. Do not reveal detection mechanisms or unfinished remediation, and never imply the employer endorses the article.
5. Use only facts the author personally knows and can review. **Do not fabricate an attack path, root cause, impact, response procedure, recovery time or outcome**. If something is uncertain, say so or omit it.
6. Prefer a high-level lesson about decisions, verification, trade-offs or communication to technical detail that might help identify a target. If a sufficiently meaningful story cannot be told safely, **do not publish that case**.
7. Prefer a fresh fictional **composite learning scenario clearly labelled fictional** over laundering a sensitive case as supposedly anonymised fact. Do not falsely present a composite as actual personal experience.
8. Final author approval: confirm facts, confidentiality, timing, public context and intended audience. Review HTML, metadata, social previews and search-indexed links too.
9. Publish only after bilingual copy review, static site checks and a separate CV GitOps revision promotion. Keep a rollback path.

## Future article template — keep unapproved incident material OUT of this public repo

- **Working title / review owner:** privately tracked
- **Scenario / context:** broad technology category only, no employer-identifying context
- **What mattered:** a defensible decision or lesson, not an exploit narrative
- **My exact role:** first-person and verifiable, not organisation-wide claims
- **Response at a high level:** omit identifying techniques and time sequence
- **Result:** what the author actually observed, without inventing numbers
- **Limitations:** what was not verified, what cannot be discussed
- **Editorial check:** factual signoff; privacy/security/legal approval where needed
- **Publication:** a separate reviewable PR only after the above checks

Do not commit source notes containing confidential facts, even on an unmerged branch, because Git history is durable and this repository is public.

## Launch rule

The CV may link to the concept through a small non-identifying teaser, but the blog page remains **noindex** and absent from sitemap until a first fully reviewed article exists. The teaser must not claim that a real case report is published and must not identify any security incident. Once a verified case is approved, update indexing and sitemap in a separate deliberate change.
