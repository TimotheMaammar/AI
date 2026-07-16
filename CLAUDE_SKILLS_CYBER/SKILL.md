---
name: bug-bounty-web
description: Web application bug bounty and pentest playbooks for use with the Caido MCP. Use when testing or hunting a web app or API for vulnerabilities, analyzing a request, parameter, response, header, cookie or JS bundle for a bug class, choosing payloads, bypassing a WAF or filter, or planning a Caido workflow. Covers access control and IDOR, SQLi, NoSQLi, XSS, SSRF, SSTI, command injection, path traversal and LFI, file upload, CSRF, auth and session, business logic, XXE, open redirect, host header, CORS, deserialization, race conditions, JWT, OAuth, GraphQL, mass assignment, web cache poisoning, request smuggling, subdomain takeover, prototype pollution, info disclosure, clickjacking, CSS injection, client-side path traversal, DOM clobbering, CRLF injection, dependency confusion, and LLM prompt injection. Triggers on bug bounty, pentest an endpoint, is this param injectable, how to exploit this, or bypass this filter.
---

# Bug Bounty Web Playbooks (Caido)

Dense per-class cheatsheets: recon signals, trick checklists, payloads, WAF bypass, escalation, references. One file per vulnerability class. Read the specific fiche when a symptom matches.

## How to use
1. Start from `00_METHODOLOGY.md` to frame the target (scope assumed already defined) and for general Caido module usage and the standard testing loop.
2. Route by observed symptom to the matching fiche below and read that file for the full playbook.
3. Cross-reference `00_WAF_ENCODING.md` whenever a payload is blocked or normalized, and `00_JS_RECON.md` for SPA and bundle recon.
4. Keep every payload in-scope and non-destructive by default (no DROP, DoS, or mass exfil). Confirm impact with the minimal PoC, then escalate.

## Router (symptom then file to read)
- ID or UUID in URL/body/JSON/cookie, role or permission, admin endpoint: `IDOR_BROKEN_ACCESS_CONTROL.md` (plus `AUTH_SESSION.md`, `JWT.md`)
- SQL error, quote breaks page, sort or filter: `SQL_INJECTION.md`
- Input reflected in HTML/JS/attribute/DOM sink: `XSS.md`
- URL or hostname or webhook, `url=`, remote import, PDF render: `SSRF.md`
- `{{7*7}}`, template engine, custom email, display name: `SSTI.md`
- ping/exec/file conversion, `cmd=`: `COMMAND_INJECTION.md`
- `file=`, `path=`, `download=`, `../`: `PATH_TRAVERSAL_LFI.md`
- avatar/document/image/import upload: `FILE_UPLOAD.md`
- sensitive action, no anti-CSRF token: `CSRF.md`
- `redirect=`, `next=`, `returnUrl=`, `url=`: `OPEN_REDIRECT.md`
- password reset, email link, cache key: `HOST_HEADER_INJECTION.md`, `WEB_CACHE_POISONING.md`
- XML/SOAP/SVG/DOCX, xml content-type: `XXE.md`
- `Access-Control-Allow-Origin`, authenticated cross-origin: `CORS.md`
- serialized cookie, `rO0`, `__VIEWSTATE`, pickle: `INSECURE_DESERIALIZATION.md`
- coupon/cart/limit/quota/multi-step workflow: `BUSINESS_LOGIC.md`
- one-time purchase, promo, double-spend, balance: `RACE_CONDITIONS.md`
- `/graphql`, introspection: `GRAPHQL.md`
- OAuth flow, `redirect_uri`, `state`, SSO: `OAUTH.md`
- JSON PATCH/PUT, hidden fields (`isAdmin`, `role`): `API_MASS_ASSIGNMENT.md`
- front/back desync, Content-Length plus Transfer-Encoding: `HTTP_REQUEST_SMUGGLING.md`
- CNAME to unclaimed third-party: `SUBDOMAIN_TAKEOVER.md`
- `__proto__`, object merge: `PROTOTYPE_POLLUTION.md`
- stacktrace, `.git`, backup, API key, debug: `INFO_DISCLOSURE.md`
- JWT `eyJ...`, `alg`, signed session cookie: `JWT.md`, `AUTH_SESSION.md`
- SPA, JS bundle, `.js.map`, hidden routes: `00_JS_RECON.md`
- AI chatbot, assistant, auto-summary, RAG: `LLM_PROMPT_INJECTION.md`
- one-click sensitive action, page framable: `CLICKJACKING.md`
- user-controlled CSS, style attribute, theme: `CSS_INJECTION.md`
- front-end builds a request path from input: `CLIENT_SIDE_PATH_TRAVERSAL.md`
- HTML injection allowed but JS blocked, reads window globals: `DOM_CLOBBERING.md`
- param reflected into a header or redirect Location, `%0d%0a`: `CRLF_INJECTION.md`
- leaked internal package name, private dep: `DEPENDENCY_CONFUSION.md`

See `README.md` for the full index and master references.
