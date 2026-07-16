# Host Header Injection

**TL;DR**: the app trusts the `Host` header (or `X-Forwarded-Host`) to build URLs, route, or cache → password reset poisoning, cache poisoning, SSRF, routing-based attacks.

## Where to look
- Absolute URL generation (email links: password reset, confirmation, invitations).
- Host reflected in the response (page, header, script src).
- Upstream cache (CDN) → `WEB_CACHE_POISONING.md`.
- Virtual hosting / Host-based routing.

## Headers to test
- `Host: evil.com`
- `X-Forwarded-Host: evil.com`
- `X-Host`, `X-Forwarded-Server`, `X-HTTP-Host-Override`, `Forwarded: host=evil.com`.
- Duplicate Host (two `Host:`), Host with port `target.com:evil.com`, absolute-URI in the request line (`GET https://evil.com/ HTTP/1.1`).
- `Host: target.com` + `X-Forwarded-Host: evil.com` (many apps prefer the second).

## Attacks
**Password reset poisoning (the classic ATO)**
- Request a reset for the **victim** with `Host`/`X-Forwarded-Host: attacker.com`.
- If the email link is built with that host → the victim clicks → token sent to `attacker.com` → ATO.
- Variant: the token leaks in the `Referer` when the victim loads an attacker resource on the reset page.

**Web cache poisoning** → `WEB_CACHE_POISONING.md` (poison via reflected non-keyed header).

**SSRF / routing**: Host used to route to an internal backend, or for a server-side fetch.

**Business/validation**: bypass Host-based controls, connect to another internal vhost (admin panel via `Host: internal-admin`).

## CRLF / header injection (related)
- If a param is reflected into a response header, a redirect `Location`, or an Nginx `$uri`, inject `%0d%0a` to add headers or split the response: `/path%0d%0aSet-Cookie:%20x=1`, `/redirect?url=%0d%0aX-Injected:%201`.
- Impact: header injection, response splitting, reflected XSS via injected body, cache poisoning. Backends that normalize/strip CR/LF are safe.

## Detection
- Reflection: inject a marker in `Host`/`X-Forwarded-Host`, look in the response (especially links, `<link>`, `<script src>`, `Location`, canonical).
- Reset: read the received email (your own account) and see if the link domain follows the header.

## Impact
- Reset poisoning → ATO = High/Critical. Cache poisoning → broad. SSRF per pivot.

## Caido
- Match & Replace to inject `X-Forwarded-Host` across all traffic; Replay on the reset endpoint; observe the email/reflection.

## References
- PortSwigger - Host header attacks - https://portswigger.net/web-security/host-header
- PortSwigger - Password reset poisoning - https://portswigger.net/web-security/host-header/exploiting#password-reset-poisoning
- PortSwigger - Host header: exploiting classic vulnerabilities - https://portswigger.net/web-security/host-header/exploiting
- OWASP WSTG - Testing for Host Header Injection - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/17-Testing_for_Host_Header_Injection
- HackTricks - Abusing hop-by-hop / Host - https://book.hacktricks.wiki/en/pentesting-web/abusing-hop-by-hop-headers.html
