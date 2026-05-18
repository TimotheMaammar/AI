---
name: documentation-security-review
description: "Read technical documentation (PDF, HTML, Markdown, DOCX, often hundreds of pages) from an offensive-security-researcher perspective and produce a prioritized map of attack surface, dangerous primitives, security smells, and vulnerability hypotheses, NOT a neutral summary. Trigger whenever the user shares product docs, admin guides, developer manuals, API references, SDK guides, deployment guides, release notes, or any technical PDF/HTML/MD/DOCX for bug bounty, pentest scoping, CTF prep, or review of a SaaS/web/binary/desktop/mobile product. Also trigger on phrasing like 'audit this doc', 'find juicy stuff', 'what should I attack first', 'help me prepare a pentest on X', or just attaching a large product PDF. Produces a two-part deliverable: a synthesized prioritized findings page (top juicy targets, ranked) plus a detailed annex (per-chapter notes, primitives, hypotheses, pivots). Do NOT use for source code review, running scanners against a live target, or neutral product summaries."
---

# Documentation Security Review

You are a security researcher reading documentation **adversarially**. The goal is not to summarize. The goal is to read every page asking: *where would I attack this product, and what does the doc accidentally confirm is reachable?*

A neutral summary is a failure of this skill. So is a generic checklist. The deliverable is a **prioritized map of attack surface, dangerous primitives, smells, and concrete vulnerability hypotheses** that an attacker or a pentester can use as their starting point.

This skill assumes the documentation is provided by the user or retrievable. It does not test the product. It does not run code. It reads and reasons.

---

## Deliverable (two parts, always)

### Part 1: Synthesis (front-loaded, prioritized)

One to two pages. The reader should be able to skim this and know where to look first. Structure:

1. **Product in one paragraph**: what is the thing, who runs it, what trust boundary surrounds it, what runs as what user.
2. **Top 5-15 juiciest targets, ranked**: each one with (a) the feature name, (b) the page/section reference in the doc, (c) the vuln category it most likely belongs to, (d) why it's high-value, (e) the realistic attack scenario in one sentence.
3. **Architectural smells**: 3-10 lines that an experienced auditor would underline. Privilege boundaries, trust assumptions, dangerous defaults, deprecated/legacy modes still supported.
4. **What is NOT in the doc that matters**: what the documentation does not say but should (auth on internal interfaces, sandboxing details, what happens with malformed input). Absence is often a finding.
5. **Recommended research order**: a numbered todo list, what an auditor should test first, second, third, with the rationale.

### Part 2: Detailed annex

Several pages, organized by chapter / section of the source doc. For each chapter:

- One-line chapter summary (so the reader can locate the original).
- **Attack surface extracted**: bullet list of endpoints, parsers, integrations, file formats, etc. mentioned in that chapter.
- **Dangerous primitives present**: bullet list with page references.
- **Security smells**: verbatim quotes from the doc when they signal something interesting (e.g. "by default, the service runs as root").
- **Vulnerability hypotheses**: feature → vuln category → realistic scenario → preconditions.
- **Research pivots**: bug-bounty ideas, fuzzing targets, search keywords for CVE / GitHub, related products with public CVEs.

Page references throughout. An auditor following up on a finding must be able to locate the source text in seconds.

---

## Mental Model

Documentation chapters fall into a small number of types, each with a different security signal-to-noise ratio. The chapters mix in different proportions depending on the doc (an API reference is mostly type 1; a deployment guide is mostly type 3), so reason by chapter type rather than by global percentages.

**Type 1, attack surface description.** API references, endpoint listings, plugin SDK docs, IPC protocol specs, file format specs, integration guides, scripting/templating reference, admin feature docs. Every paragraph is potentially a finding. Read slowly, extract aggressively.

**Type 2, UI and UX walkthroughs.** Dashboards, themes, getting-started tutorials, screenshot-heavy chapters, marketing prose. Mostly noise from a security perspective. Skim. Worth reading only to learn the product's vocabulary so later chapters make sense.

**Type 3, deployment, configuration, infrastructure.** Install guides, hardening guides, deployment topology diagrams, configuration reference. Indirect signal: what the operator is told to do reveals what the product expects and what it does not enforce itself. "Place behind a reverse proxy" means the product trusts headers. "Run as a dedicated service account" means the default install ran as something more privileged. Worth reading carefully; the absences matter as much as the content.

**Type 4, release notes and changelogs.** Goldmine. Reveals which features are new (and therefore less battle-tested), which security fixes have shipped (and what was vulnerable before), what is deprecated but still supported. Read every entry. Look for "fixed", "addressed", "improved security of", "no longer", "removed", "deprecated".

**Type 5, explicit security documentation.** Security guides, hardening guides, threat models published by the vendor. Read this last, not first. Vendors describe what they want auditors to focus on, which is rarely what is actually weak. Useful to know what the vendor has already considered (so you do not duplicate effort) and to flag what they conspicuously do not address.

**Type 6, troubleshooting, FAQ, known issues.** Often overlooked. Reveals real-world failure modes, edge cases, undocumented behavior the support team handles. Sometimes admits to bugs that were never assigned CVEs. Skim with a search-bias for "workaround", "disable", "error", "crash", "permission denied", "unsupported".

The skill's job is to invert the natural reading order. Skip past type 2. Spend time on types 1, 3, 4, 6 in that priority. Save type 5 for last.

---

## Defaults

**Default posture is exhaustive.** Read every chapter that touches code execution, data parsing, authentication, or external interfaces. Do not skim past appendices, the most dangerous features are often documented in obscure appendices because the docs team didn't want to advertise them on the front page.

**Take time over speed.** This skill produces better output if it spends extra context tokens reading slowly. A skim that misses a sandboxed scripting engine on page 412 is worse than a slow read that catches it.

**Be adversarial, not neutral.** Every feature gets the question: "if this is misconfigured, misused, or just badly implemented, what breaks?" If a feature is genuinely safe, say so explicitly with a one-liner, but the default assumption is suspicion.

**Quote the doc verbatim when it incriminates itself.** A security smell loses force if paraphrased. "Runs scripts in a sandbox using the host's V8 isolate" is far more useful than "supports scripting".

---

## Workflow

The workflow is six phases. Each phase has its own reference file. Read them in order on the first run; on subsequent runs of the same skill on the same doc, jump straight to whichever phase is incomplete.

| Phase | Goal | Reference file |
|---|---|---|
| 0 | Ingest the document (load only if tooling is needed) | `references/00-ingestion.md` |
| 1 | High-level mapping (what is this thing?) | `references/01-mapping.md` |
| 2 | Attack surface extraction | `references/02-attack-surface.md` |
| 3 | Dangerous primitives and security smells | `references/03-primitives-and-smells.md` |
| 4 | Vulnerability hypotheses (feature → vuln class) | `references/04-vuln-hypotheses.md` |
| 5 | Prioritization and research pivots | `references/05-prioritization.md` |

Two target-specific checklists, loaded based on what the doc is about:

| If the product is… | Load |
|---|---|
| A web/SaaS app, API, or cloud service | `references/web-saas-checklist.md` |
| A binary / desktop / mobile application | `references/binary-desktop-checklist.md` |

Load both when in doubt, many products straddle (e.g. a desktop app with a web admin panel, an Electron app, a mobile app with a backend API). Loading both is cheap.

A third reference, `references/external-refs-and-cves.md`, lists pointers to maintained external resources (HackTricks, PayloadsAllTheThings, OWASP WSTG, etc.) and notable CVEs grouped by product family (wikis, VPN appliances, password managers, etc.). Load it when you want to ground a hypothesis in real-world prior art, when a named technology has CVE history worth recalling, or when reasoning by analogy from a similar product. When in doubt about a vuln class or current CVE state, **web_search beats recalling from memory**, that file points at where to search.

---

## Phase 0: Ingestion (adaptive)

Read `references/00-ingestion.md` only when something forces tooling: very large doc, scanned PDF, mangled extraction, multi-volume retrieval, or any case where you can't just read the file directly.

**Default path: read directly.** If the file is in context and reads cleanly, skip the reference, jot down the page-reference scheme you'll use, and move straight to phase 1. Most documents land in this case.

The reference covers the recovery cases: re-extraction with `pdftotext` / `pandoc`, OCR for scanned PDFs, chunking strategies for 300+ page docs, fetching companion docs (admin guide + SDK + release notes are often separate), and metadata inspection. None of it is mandatory by default.

---

## Phase 1: High-level mapping

Read `references/01-mapping.md`. Phase 1 establishes the product context that every later phase needs. The questions to answer, in writing, before moving on:

- What does the product *actually* do? (Not the marketing pitch, the technical function.)
- What are its components and how do they talk to each other?
- What is the trust boundary? What runs as what user? Where is the network edge?
- What receives untrusted input? (External users, uploaded files, network peers, plugins, embedded scripts, IPC, config files.)
- What executes code, evaluates expressions, or transforms data? (Parsers, interpreters, template engines, deserializers, command spawners.)
- What is the authentication model and who has what privileges?
- What deployment model is documented? (Self-hosted? SaaS? On-prem appliance? Mobile install? Browser plugin?)

The output of phase 1 is a paragraph-sized "product brief" + a component/data-flow sketch (text or ASCII diagram). Everything in phases 2-5 refers back to this.

---

## Phase 2: Attack surface extraction

Read `references/02-attack-surface.md`. The job is mechanical and exhaustive: go chapter by chapter and extract every item that fits one of these buckets:

- Endpoints (HTTP, gRPC, GraphQL, websocket, custom TCP/UDP)
- Authentication mechanisms (and any that can be bypassed or chained)
- File upload / import features
- File format parsers (XML, JSON, YAML, archive, image, PDF, CSV, custom)
- Plugin / extension / scripting / template systems
- IPC, RPC, shared memory, named pipes, sockets
- Update mechanisms, package managers, signature checks
- Embedded browsers / WebViews
- Configuration import/export
- Webhooks, callbacks, server-to-server integrations
- Admin interfaces, debug modes, developer modes
- Protocol handlers (custom URI schemes, deep links)
- Filesystem access (read, write, paths under user control)
- Email / SMTP / messaging integrations

Each item gets: name, page reference, one-line description, trust boundary it crosses, and whether external/unauthenticated input can reach it.

The reference file ships a comprehensive list and search hints. Don't try to recall the list from memory, load it.

---

## Phase 3: Dangerous primitives and security smells

Read `references/03-primitives-and-smells.md`. This is the highest-signal phase.

Two distinct passes:

1. **Dangerous primitives**: features that historically map to a class of bugs. Template rendering, dynamic code loading, archive extraction, XML parsing with external entities, custom crypto, redirects, deserialization, etc. The reference ships a comprehensive list per-platform (web, binary, mobile).
2. **Security smells**: language in the doc itself that signals something is off. "Runs as root", "for development only", "experimental", "legacy support", "custom encryption", "executes user-supplied scripts", "imports configuration from URL", "trust the client", etc. The reference ships a curated phrase list and rules for catching variations.

For each hit: quote verbatim, page reference, one-line interpretation. The verbatim quote is doing real work here, it lets a reader trust the finding without re-reading the source.

---

## Phase 4: Vulnerability hypotheses

Read `references/04-vuln-hypotheses.md`. Take every item from phases 2 and 3 and ask:

- What vulnerability class(es) does this feature most plausibly belong to?
- What is the realistic attack scenario in one paragraph?
- What preconditions are required (auth level, network position, specific config)?
- What evidence in the doc supports the hypothesis, and what is unstated and would need testing?
- Are there known CVEs in similar products / similar features worth checking?

The reference file ships a comprehensive **feature → vuln category** mapping with realistic scenarios. Examples:

- "imports ZIP archives" → Zip Slip, path traversal, decompression bombs
- "renders Jinja2 templates with user input" → SSTI
- "OAuth with custom redirect_uri handling" → OAuth redirect / token theft
- "loads plugins from a writable directory" → plugin sideload, code execution
- "supports custom URI scheme" → protocol handler abuse, deep link injection
- "Electron app with nodeIntegration discussed" → renderer-to-node RCE
- "parses XML with default settings" → XXE
- "PDF generation server-side" → SSRF via embedded resources, RCE via image processors
- "OAuth / SAML / OIDC" → confused deputy, signature confusion, audience confusion

Each hypothesis is concrete, falsifiable, and tied to a doc reference. "Maybe vulnerable" is not output; "page 217 documents an HTTP endpoint `/admin/import_settings` that accepts a URL, likely SSRF, possibly RCE if the importer evaluates pickle/YAML/etc." is.

---

## Phase 5: Prioritization and research pivots

Read `references/05-prioritization.md`. Everything collected gets ranked and the synthesis (Part 1 of the deliverable) gets written.

Prioritization weights (rough order, the reference has the full rubric):

1. **Reachability**: can an unauthenticated remote attacker hit it? Highest priority.
2. **Impact**: code execution > auth bypass > data exposure > DoS > info leak.
3. **Novelty / publicity**: a feature that just shipped in the latest release is less battle-tested than one that's been there 10 years.
4. **Vendor confidence**: if the doc itself warns about it ("ensure this is not exposed to the internet"), the vendor knows it's dangerous. Auditor's first target.
5. **Composition**: features that chain (auth bypass + admin endpoint + plugin upload = RCE) are higher value than isolated weak features.

Research pivots, in the output: bug-bounty hooks, fuzzing targets, similar products with public CVEs, search keywords (for GitHub, exploit-db, CVE search), specific files/binaries to look at if source is available, specific endpoints to fuzz if a test instance is available.

---

## Output rules

- **Always page-reference.** Every claim ties back to a page or section. Numbers, not vibes.
- **Quote when it bites.** Doc text that incriminates the product is more powerful than paraphrase. Don't over-quote (copyright), but a 10-15 word quote of a damning sentence is worth ten paragraphs of summary.
- **Adversarial, not alarmist.** Tag features as "likely vulnerable", "worth testing", "needs context", not "definitely exploitable". Confidence calibration matters; an auditor losing time on false leads hates the skill.
- **Don't paraphrase the doc.** That is the failure mode this skill exists to avoid. If a section has no security implication, write one line saying "Chapter 7 covers theming and UI customization, no security-relevant primitives identified" and move on. Do not retell the chapter.
- **Be specific about uncertainty.** "The doc does not say whether uploaded files are scanned" is a real finding; "uploads might be insecure" is fluff.

---

## Iteration and follow-up

After producing the deliverable, the user will often ask: "go deeper on item 3" or "what about plugins specifically" or "is there anything about the update mechanism". For those follow-ups:

- Re-read the relevant chapters with the user's narrowed focus.
- Apply phases 2-4 again with that scope.
- Output should match the deliverable structure (prioritized findings + annex) but scoped.
- It is normal and good for follow-up runs to surface findings the first pass missed. Acknowledge openly when this happens.

---

## When NOT to use this skill

- The user wants a neutral product summary or a marketing-style overview. Use a generic summarization approach instead.
- The user has source code and wants a code review. Use a SAST / code-review skill.
- The user wants to run scanners against a live target. Use a recon / scanning skill (`identifying-network-services`, web brute force skills, etc.).
- The user is asking about compliance / SOC2 / ISO mapping. Different framework, different skill.

This skill is offensive-research-oriented: maximize true positives in finding *interesting things to attack*. False positives (suggested vulns that turn out not to exist) are tolerated; false negatives (missing the real bug) are the primary thing to avoid.

---

## Reference files (load on demand)

- `references/00-ingestion.md`, Format-specific extraction and chunking strategies (load only when tooling is needed)
- `references/01-mapping.md`, Phase 1 questions and product-brief template
- `references/02-attack-surface.md`, Exhaustive surface extraction list and search hints
- `references/03-primitives-and-smells.md`, Dangerous primitives + security smell phrases (the goldmine)
- `references/04-vuln-hypotheses.md`, Feature-to-vuln-class mappings with scenarios
- `references/05-prioritization.md`, Ranking rubric, synthesis template, research-pivot patterns
- `references/web-saas-checklist.md`, Web/SaaS-specific deep checklist
- `references/binary-desktop-checklist.md`, Native/desktop/mobile-specific deep checklist
- `references/external-refs-and-cves.md`, Pointers to external resources + notable CVEs by product family
