# SKILLS_CYBER - Bug Bounty Web Vulnerability Playbooks

Dense cheatsheets, one vulnerability class per file. Built for use by Claude while bug bounty hunting with the **Caido MCP**. No fluff: recon signals, trick checklists, payloads, WAF bypass, escalation, references.

Assumes an **already-defined scope** being tested with Caido. Asset/subdomain discovery is handled separately.

## How to use this folder (for Claude)

1. **Start with `00_METHODOLOGY.md`** to frame the target (scope, functional mapping, attack-surface mapping) - it also holds the general Caido module usage and the standard testing loop.
2. **Route to the right file** based on the observed parameter/behavior (see router below).
3. **Cross-reference `00_WAF_ENCODING.md`** whenever a filter/WAF blocks a payload.
4. Each vuln file has its own **Caido** section with the concrete recipe for that class.
5. Keep every payload **in-scope** and **non-destructive** by default (no DROP, no DoS, no mass exfil). Confirm impact with the minimal PoC.

## Testing principle (reminder)
- One signal = one hypothesis = one isolated test. Change **one** parameter at a time.
- Always take a **baseline** (normal response) before fuzzing: status, length, timing, keywords, reflections.
- Look for **oracles**: any response difference (content/length/timing/code/error) is an information channel.
- Escalate from a **harmless PoC** (`alert(document.domain)`, `sleep 0`, unique marker, collaborator ping) to real impact only once confirmed.
- Log every test: request, response, hypothesis, verdict. Reproducibility = paid report.

## Quick router (symptom → file)

| Observed signal | File |
|---|---|
| Numeric ID / UUID / GUID in URL, body, JSON, cookie | `IDOR_BROKEN_ACCESS_CONTROL.md` |
| Role/permission, admin endpoint, `role=`, `/admin` path | `IDOR_BROKEN_ACCESS_CONTROL.md`, `AUTH_SESSION.md`, `JWT.md` |
| SQL error, quote breaks the page, `id=`, sort/filter/`ORDER BY` | `SQL_INJECTION.md` |
| Input reflected in HTML / JS / attribute / DOM sink | `XSS.md` |
| URL/hostname/webhook/`url=`/`img=`/remote import/PDF render | `SSRF.md` |
| `{{7*7}}`, template engine, preview, custom email, display name | `SSTI.md` |
| `ping`, `exec`, file conversion, `cmd=`, ffmpeg/imagemagick | `COMMAND_INJECTION.md` |
| `file=`, `path=`, `download=`, `template=`, `../` | `PATH_TRAVERSAL_LFI.md` |
| Avatar / document / image / import upload | `FILE_UPLOAD.md` |
| Sensitive action with no anti-CSRF token, POST form | `CSRF.md` |
| `redirect=`, `next=`, `returnUrl=`, `?url=`, `dest=` | `OPEN_REDIRECT.md` |
| Password reset, link in email, cache key | `HOST_HEADER_INJECTION.md`, `WEB_CACHE_POISONING.md` |
| XML/SOAP/SVG/DOCX/XLSX/`Content-Type: *xml` | `XXE.md` |
| `Access-Control-Allow-Origin`, authenticated cross-origin request | `CORS.md` |
| Serialized cookie, `rO0`, `__VIEWSTATE`, pickle, `O:8:` | `INSECURE_DESERIALIZATION.md` |
| Coupon/cart/limit/vote/transfer/quota/multi-step workflow | `BUSINESS_LOGIC.md` |
| One-time purchase, promo code, double-spend, invite, balance | `RACE_CONDITIONS.md` |
| `/graphql`, `query {`, introspection, `__schema` | `GRAPHQL.md` |
| OAuth flow, `redirect_uri`, `state`, `code`, SSO | `OAUTH.md` |
| JSON PATCH/PUT, hidden fields (`isAdmin`, `role`, `balance`) | `API_MASS_ASSIGNMENT.md` |
| Front-end/back-end desync, `Content-Length`+`Transfer-Encoding` | `HTTP_REQUEST_SMUGGLING.md` |
| `CNAME` to an unclaimed third-party service, provider 404 | `SUBDOMAIN_TAKEOVER.md` |
| `__proto__`, object merge, query/JSON parsing | `PROTOTYPE_POLLUTION.md` |
| Stacktrace, `.git`, backup, API key, debug, verbose error | `INFO_DISCLOSURE.md` |
| JWT `eyJ...`, `alg`, signed session cookie | `JWT.md`, `AUTH_SESSION.md` |
| SPA / JS bundle / `.js.map` / hidden routes & fields | `00_JS_RECON.md` |
| AI chatbot / assistant / auto-summary / moderation / RAG | `LLM_PROMPT_INJECTION.md` |
| Sensitive 1-click action, page framable (no `X-Frame-Options`/`frame-ancestors`) | `CLICKJACKING.md` |
| User-controlled CSS / `<style>` / theme, JS blocked but CSS passes | `CSS_INJECTION.md` |
| Front-end builds a request path from input (`fetch('/api/'+x)`), `../` in path | `CLIENT_SIDE_PATH_TRAVERSAL.md` |
| HTML injection allowed but JS blocked, code reads `window.x`/config | `DOM_CLOBBERING.md` |
| Param reflected into a header / redirect `Location`, `%0d%0a` | `CRLF_INJECTION.md` |
| Leaked internal package name, private dep not on public registry | `DEPENDENCY_CONFUSION.md` |

## Files

**Core reference**
- `00_METHODOLOGY.md` - scope framing, functional mapping, per-feature checklist, Caido modules + standard loop
- `00_WAF_ENCODING.md` - encodings, filter/WAF bypass, cross-cutting cheatsheet
- `00_JS_RECON.md` - JS bundle / source-map recon on SPAs

**Vuln classes**
- `IDOR_BROKEN_ACCESS_CONTROL.md`
- `SQL_INJECTION.md` · `XSS.md` · `SSRF.md`
- `COMMAND_INJECTION.md` · `SSTI.md` · `PATH_TRAVERSAL_LFI.md` · `FILE_UPLOAD.md`
- `CSRF.md` · `AUTH_SESSION.md` · `BUSINESS_LOGIC.md`

**Extended**
- `XXE.md`, `OPEN_REDIRECT.md`, `HOST_HEADER_INJECTION.md`, `CORS.md`,
  `INSECURE_DESERIALIZATION.md`, `RACE_CONDITIONS.md`, `JWT.md`, `OAUTH.md`,
  `GRAPHQL.md`, `API_MASS_ASSIGNMENT.md`, `WEB_CACHE_POISONING.md`,
  `HTTP_REQUEST_SMUGGLING.md`, `SUBDOMAIN_TAKEOVER.md`, `PROTOTYPE_POLLUTION.md`,
  `INFO_DISCLOSURE.md`, `LLM_PROMPT_INJECTION.md`,
  `CLICKJACKING.md`, `CSS_INJECTION.md`, `CLIENT_SIDE_PATH_TRAVERSAL.md`,
  `DOM_CLOBBERING.md`, `CRLF_INJECTION.md`, `DEPENDENCY_CONFUSION.md`

## Master references (valid for the whole folder)
- **PortSwigger Web Security Academy** - https://portswigger.net/web-security
- **PayloadsAllTheThings** - https://github.com/swisskyrepo/PayloadsAllTheThings
- **OWASP Web Security Testing Guide (WSTG)** - https://owasp.org/www-project-web-security-testing-guide/
- **OWASP Cheat Sheet Series** - https://cheatsheetseries.owasp.org/
- **HackTricks** - https://book.hacktricks.wiki/
- **Bugcrowd VRT (severity)** - https://bugcrowd.com/vulnerability-rating-taxonomy
- **SecLists (wordlists)** - https://github.com/danielmiessler/SecLists
- **Caido docs** - https://docs.caido.io/
- **YesWeHack - Learn Bug Bounty (per-vuln guides)** - https://www.yeswehack.com/learn-bug-bounty
- **YesWeHack Dojo (labs)** - https://dojo-yeswehack.com/
- **YesWeHack - Vulnerable Code Snippets** - https://github.com/yeswehack/vulnerable-code-snippets

