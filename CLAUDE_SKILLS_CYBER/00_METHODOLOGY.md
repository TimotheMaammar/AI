# 00 - Methodology & Caido Working Loop

Assumes an **already-defined, already-discovered scope**: we are pentesting a known target with Caido. Asset/subdomain discovery is handled separately and is out of scope for this file. Goal here: go from "a known app in front of me" to "a list of testable vulnerability hypotheses", and run each test efficiently in Caido.

## 0. Scope & rules (non-negotiable)
- Read the program scope: in-scope hosts/paths, out-of-scope, forbidden tests (DoS, heavy brute-force, social engineering, email spam).
- Respect the required rate-limit. Add an identifying header if the program asks (`X-Bug-Bounty: <handle>`).
- Payloads **non-destructive** by default. Never `DROP`, `shutdown`, mass-delete, or exfiltrate other users' real data beyond the minimal PoC (2 IDs are enough to prove an IDOR).

## 1. Map the target (within a known scope)
- **Browse the whole app as a normal user first.** Proxy everything through Caido; the HTTP History becomes your map.
- **Passive URL/param sources** already tied to this target: Caido HTTP History/Sitemap, in-app links, and the JS bundle (see `00_JS_RECON.md` - read the bundle early, it lists every API route/field the front can call, even unclicked ones).
- **Hidden parameters**: param-mining on interesting endpoints (`debug=`, `admin=`, `test=`).
- **Content within the app**: authenticated areas, admin panels, API versions (`/v1` vs `/v2`), mobile API, exports/imports.

## 2. Functional map (where bugs live)
Walk the app and note:
- **Auth surface**: login, signup, reset, MFA, SSO/OAuth, email/password change.
- **Multi-tenant / user objects**: every object ID is an IDOR candidate. Create **2 accounts (A and B)** early.
- **Uploads / imports / exports**: files, avatars, CSV, PDF, images.
- **Outbound integrations**: webhooks, "fetch URL", remote import, SSO, link previews.
- **Multi-step workflows**: payment, cart, KYC, invite, quota → `BUSINESS_LOGIC.md` / `RACE_CONDITIONS.md`.
- **Search / filters / sort**: SQLi/NoSQLi candidates.
- **Content rendering**: markdown, email templates, display names → XSS/SSTI.

## 3. Prioritization (where to hit first)
Typical BB web payoff order:
1. **Broken Access Control / IDOR** - most frequent, often High/Critical, low noise.
2. **Auth / session / OAuth / JWT** - account takeover.
3. **Injection** (SQLi, SSTI, cmd) - high impact when present.
4. **SSRF** - especially in cloud (metadata) → creds/RCE.
5. **Business logic / race** - poorly covered by scanners = fewer duplicates.
6. **XSS / CSRF / CORS / open redirect** - volume, often chainable.

## 4. Chaining (think composed impact)
- Open redirect + OAuth `redirect_uri` → token theft.
- SSRF + cloud metadata → creds → escalation.
- XSS + weak CSRF → ATO. Self-XSS + login CSRF → exploitable.
- IDOR on an export endpoint → mass leak.
- Host header injection → password reset poisoning → ATO.
- Prototype pollution + gadget → XSS/RCE.

## 5. Baseline & oracles (set before fuzzing)
For every endpoint tested, memorize the normal response: **status code**, **length**, **time**, **error keywords**, **input reflections**. Any deviation is a signal. In Caido Automate, add grep-match/grep-extract columns on these oracles and sort by them.

## 6. Quick checklist per new feature
- [ ] Which parameters? (URL, body, headers, cookies, JSON, path)
- [ ] Where does the input come back out? (HTML, JS, SQL, command, template, outbound request, file)
- [ ] Is there an access control? (test as B, then unauthenticated)
- [ ] Is there an anti-CSRF token, OAuth state, rate-limit?
- [ ] Can the workflow be played out of order / in parallel / repeated?

---

## Caido - modules & usage
- **Intercept**: live capture, pause/forward/edit. Catches hidden requests (XHR, webhooks).
- **HTTP History / Sitemap**: everything seen. Filter by host, status, method, mime, extension. Starting point to spot parameters (IDs, `url=`, `file=`, `redirect=`).
- **Replay**: replay/edit a single request. The main manual-testing module. Duplicate tabs (one hypothesis per session). Status/length/time at a glance = oracle.
- **Automate**: Intruder-style fuzzer. Place `{PLACEHOLDER}`s, load a wordlist, sniper/battering-ram/pitchfork. Add grep-match / grep-extract columns and sort by length/status/time to surface anomalies.
- **Match & Replace**: global rewrite rules on requests/responses. E.g. inject a header, swap a session cookie, downgrade `Sec-*`, force `X-Forwarded-For`. Ideal to test access control across the whole session.
- **Convert**: encode/decode (URL, base64, hex, HTML, JWT, hash) before injecting into a filtered context (see `00_WAF_ENCODING.md`).
- **Findings**: mark/annotate hits; keep a reproducible log for the report.
- **Workflows / Plugins**: automate transforms (encode chains, JWT signing, collaborator payloads). Check the plugin store for community active-scan/notify tooling.
- **Projects**: one project per target.
- **AuthMatrix plugin** (Autorize equivalent): replay a request across roles/sessions in a matrix to catch access-control/IDOR gaps fast (see `IDOR_BROKEN_ACCESS_CONTROL.md`).
- **QuickSSRF plugin**: OOB/interaction listener, collaborator-style, for SSRF/blind OOB (see `SSRF.md`).
- **EvenBetter plugin**: UI quality-of-life additions. **PwnFox** for Firefox container-per-scope.
- **HTTPQL**: query language to filter history precisely (https://docs.caido.io/reference/httpql.html). `Ctrl+K` = command palette.
- **Caido CLI** runs headless on a VPS (overnight scans; reach it with `ssh -L 9999:127.0.0.1:8080 user@vps`).

## Standard loop (repeat)
1. Spot an interesting request in HTTP History.
2. Send to Replay. Establish baseline (status/length/time/reflections).
3. One hypothesis → one payload → observe the oracle (status/len/time/reflection/error/collaborator).
4. If filtered → `00_WAF_ENCODING.md`, re-encode via Convert.
5. Confirmed → Findings + minimal reproducible PoC.

Per-vulnerability Caido recipes live in each vuln file's **Caido** section.

## References
- OWASP WSTG (full methodology) - https://owasp.org/www-project-web-security-testing-guide/stable/
- The Bug Hunter's Methodology (Jason Haddix / TBHM) - https://github.com/jhaddix/tbhm
- PortSwigger - all labs by topic - https://portswigger.net/web-security/all-labs
- HackTricks - Pentesting Web - https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/
- Caido docs - https://docs.caido.io/
- Caido - Replay / Automate / Match & Replace - https://docs.caido.io/reference/features/
