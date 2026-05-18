# Phase 5: Prioritization and research pivots

Everything collected in phases 2-4 gets ranked, and the synthesis (Part 1 of the deliverable) gets written.

---

## 5.1 Ranking rubric

Each hypothesis gets a score on five dimensions. Score them quickly; this is for ordering, not certification.

| Dimension | Weight | Scoring guidance |
|---|---|---|
| **Reachability** | Highest | Unauthenticated remote = 5; authenticated remote = 4; admin remote = 3; authenticated local = 2; physical access = 1 |
| **Impact** | High | RCE = 5; auth bypass / privilege escalation = 4; sensitive data exposure = 3; DoS / partial info leak = 2; nuisance = 1 |
| **Confidence** | Medium | Doc explicitly confirms it = 5; doc strongly implies = 4; doc consistent with pattern = 3; speculative = 2; long shot = 1 |
| **Novelty / publicity** | Medium | Feature shipped in the latest release = +1; feature has known CVEs in similar products = +1; feature is universally hardened by now (mature OAuth, mature CSRF) = -1 |
| **Composition** | Medium | Hypothesis chains with others = +1 per useful chain; hypothesis is standalone and orthogonal = 0 |

**Simple formula** (a starting point, override with judgment):

```
priority = (reachability * 3) + (impact * 3) + (confidence * 2) + novelty_adj + composition_adj
```

The top 5-15 entries by priority go into the synthesis "top juiciest targets" list.

### Don't over-rank common cases

A 600-page doc surfaces dozens of "missing CSRF token" or "session cookie without `SameSite`" findings. These are real but rarely the most interesting. Rank them medium and group them in the annex; don't let them drown out a single SSTI or auth-bypass finding in the synthesis.

### Tiebreakers

When two hypotheses score equal, prefer in this order:

1. Hypothesis with a clearer test plan (faster to validate).
2. Hypothesis that opens up other findings if true (a privilege escalation that exposes admin endpoints multiplies value).
3. Hypothesis where the vendor's own doc admits the risk ("for development only").

---

## 5.2 Synthesis template (Part 1 of the deliverable)

```
# Security review of <Product Name>

**Source:** <doc title, version, page count or URL>
**Reviewer:** <if relevant>
**Date:** <date>
**Page reference scheme:** <as established in phase 0>

## Product in brief

<One paragraph from phase 1.>

## Top juiciest targets

(Ranked by priority. Each entry is short: feature, doc ref, vuln class, why high-value, one-sentence scenario.)

1. **<Feature name>**: <doc ref>, <vuln class>
   <One sentence: why high-value, one-line scenario.>

2. **<Feature name>**: <doc ref>, <vuln class>
   ...

(5 to 15 entries.)

## Architectural smells

<3 to 10 lines. Verbatim quotes from the doc with brief interpretation. The "auditor's eyebrow" findings.>

- "<verbatim>" (<doc ref>), <interpretation>
- "<verbatim>" (<doc ref>), <interpretation>

## What is NOT in the doc that matters

<Bullet list of unstated facts that would change the picture. Absence findings.>

- Doc does not say <X>. Worth testing because <Y>.
- Doc does not state <X>. Likely <Y>.

## Recommended research order

1. **<Action>**: <one-line rationale>. Map to hypothesis #N, #M.
2. **<Action>**: <one-line rationale>. Map to hypothesis #N.
3. ...

## Cross-feature chains worth pursuing

<Short list of multi-step exploit chains the synthesis identified.>

- <Chain> → maps to hypotheses #A + #B
- <Chain> → maps to hypotheses #C + #D + #E

---

(Detailed annex follows in Part 2.)
```

---

## 5.3 Research pivots

Beyond the synthesis, the report should equip the researcher with leads to keep investigating outside the doc. Include these at the end of the synthesis or as a separate section.

### Bug-bounty / scope check

- **Is this product in any bug bounty program?** Search hackerone, bugcrowd, intigriti, yeswehack, the vendor's own page. Reading the program scope and the published-disclosed reports for the same product is the single highest-ROI external check. Public reports tell you what's already been found and what classes of bugs the vendor pays for.
- **Vendor security page** (`/security`, `/security.txt`, `/responsible-disclosure`): publication policies, known limitations, contact.
- **GitHub Security Advisories** for the product or its OSS components.

### CVE lookups

For each major dependency or feature category, search:

- NVD / MITRE: `<product name>`, `<component name>`, `<file format>` parser.
- exploit-db: same.
- GitHub advisories (`github.com/advisories`): same.
- VulnDB / Tenable / Vulners aggregators.

Always check:

- Versions mentioned in the doc against current CVEs for those versions. The doc telling you "we use Jackson 2.9.x" is half a finding by itself (Jackson 2.9.x has many deserialization CVEs).
- The product's own changelog/release notes for security fixes, a fixed CVE in v3.4 is a known-vulnerable surface in v3.3 deployments.

### Fuzzing targets

If a test instance or binary is available, fuzzing candidates include:

- Custom file format parsers (binary or text).
- Custom protocol implementations (network-listening).
- Any feature that parses user input into structured form (XML, JSON, custom).
- IPC endpoints that accept structured messages.
- Web endpoints that accept complex JSON / multipart / XML.

Useful tools to mention by category (without running them in this skill):

- AFL++, libFuzzer, honggfuzz for native binaries
- boofuzz, mutiny for network protocol fuzzing
- ffuf, wfuzz for web parameter fuzzing
- radamsa for input mutation
- jazzer (Java), atheris (Python) for managed-runtime fuzzing

### Search keywords (for GitHub / web / vendor forums)

For each major component the doc names, generate search keywords:

- `<product> RCE` / `<product> SSTI` / `<product> SSRF`
- `<dependency name> CVE`
- `<feature name> bypass`
- Vendor forum / issue tracker for `auth`, `bypass`, `disable`, `exploit`, `RCE`, `XSS`, `crash`.

GitHub code search for the product (if OSS) or for related plugins / examples:

- `<product> + dangerous-keyword` (e.g. `Velocity.evaluate user-controlled`)
- Past issues mentioning "security", "auth", "bypass", even closed and dismissed ones.

### Similar products with public CVEs

If the product has obvious peers (same niche, same architecture), pull their CVE histories. Patterns repeat across products of the same kind:

- Wiki/collab products: SSTI in template macros (Confluence, MediaWiki).
- File-sync products: path traversal on sync (Dropbox, ownCloud).
- DevOps tooling: Groovy/JS sandbox escapes (Jenkins).
- PDF processors: ghostscript / imagemagick CVEs (DocuSign, Adobe).
- Electron desktop apps: nodeIntegration, custom URL scheme, IPC (Discord, Slack, etc.).
- Mobile apps: deep link injection, exported components, WebView bridge (countless).
- Mail products: MIME / S/MIME / parser CVEs.

The pattern: a product in category X usually has bugs in the category-X-typical places. Use peer history as a guide for where to look.

### Related source

If the product is OSS, the source repo is the single most valuable next step. Mention this prominently. The doc establishes hypotheses; the source confirms or refutes them in minutes.

If the product is closed-source, look for:

- Vendor binaries available for download (free trial, evaluation version), apply the `analyzing-binaries` skill.
- Mobile app on Play Store / App Store, extract APK / IPA and apply binary / JS analysis.
- Browser-served bundles for web apps, apply the `js-analysis` skill.
- Decompiled .NET / Java if applicable.

---

## 5.4 Cross-reference table (link annex to synthesis)

In the annex, every per-chapter section ends with a small table mapping the chapter's findings to the synthesis priorities:

```
| Finding (annex section) | Synthesis priority | Hypothesis # |
|---|---|---|
| Webhook URL configurable | Top 5 | #3 |
| ZIP plugin upload | Top 10 | #7 |
| CEF preload bridge | Top 5 | #2 |
| Workshop Groovy DSL | Top 15 | #11 |
```

This makes the deliverable navigable in both directions: a reader who starts from the synthesis can jump to the annex for detail; a reader who reads the annex linearly can see which findings made the top.

---

## 5.5 Final review pass

Before handing off, re-read the synthesis with these checks:

- **Front-loaded?** A reader reading only the top of the synthesis should already know the top 3 findings.
- **Specific?** No vague language ("multiple issues with authentication"). Each finding has a feature, a class, a scenario, a page reference.
- **Calibrated?** Confidence levels match what the doc actually supports. "Likely vulnerable" / "worth testing" / "possible". Avoid "definitely vulnerable" without source / runtime confirmation.
- **Adversarial?** Re-read the chapter summaries in the annex. Any that read like neutral product description should be rewritten with an attacker's lens or marked NONE/LOW.
- **Page-referenced?** Every claim has a citation.
- **No dead ends?** Every hypothesis has a test plan (or an explicit "needs source review" note).
- **Pivots provided?** External research leads (peer CVEs, fuzzing targets, search keywords) are present.

A good deliverable is one a pentester or bug-bounty hunter could open and start working from in five minutes, with a clear sense of "what to try first" and "where the cited material is in the source doc".
