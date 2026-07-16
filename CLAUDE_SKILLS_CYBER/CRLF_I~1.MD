# CRLF Injection / HTTP Response Splitting

**TL;DR**: inject `\r\n` (`%0d%0a`) into something reflected in a response header (redirect `Location`, `Set-Cookie`, custom header) or a log. Lets you add headers, split the response, poison caches, set cookies, or inject a body (reflected XSS). Adjacent to request smuggling and open redirect.

## Where to look
- Params reflected into a header: redirect `Location` (`?url=`, `?next=`, `?redirect=`), `Set-Cookie` values, language/region headers, `X-*` echoed headers.
- Nginx `$uri`/`$document_uri` in `return`/`add_header` (see `INFO_DISCLOSURE.md` Nginx), proxies, log files (log injection).

## Payloads
- Add a header: `%0d%0aSet-Cookie:%20sessionid=attacker` (session fixation), `%0d%0aX-Injected:%201`.
- Response splitting + body (reflected XSS under injected content): `%0d%0a%0d%0a<script>alert(document.domain)</script>`.
- Force a redirect: `%0d%0aLocation:%20https://evil`.
- Cache poisoning: split so the cache stores your injected headers/body (chain `WEB_CACHE_POISONING.md`).
- Encoding variants when `%0d%0a` is filtered: `%0a` alone (some parsers), `%E5%98%8A%E5%98%8D` (unicode CR/LF that some frameworks down-convert), `\r\n`, `%23%0d%0a`, double-encode `%250d%250a`.

## Escalation
- Session fixation via injected `Set-Cookie`.
- Reflected XSS via injected body (bypasses some XSS filters since it rides in headers).
- Open redirect via injected `Location`.
- Web cache poisoning -> served to all users.
- Header smuggling toward the backend.

## Detection
- Inject `%0d%0a<marker>:%20x` into redirect/header params; inspect raw response for the new header line. Confirm the parser honors CR/LF (many normalize/strip = not vulnerable).

## Caido
- Replay: put the CRLF payload in the redirect/header param, read the raw response for injected `Set-Cookie`/`Location`/split body.

## References
- PayloadsAllTheThings - CRLF Injection - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/CRLF%20Injection
- OWASP - CRLF Injection - https://owasp.org/www-community/vulnerabilities/CRLF_Injection
- HackTricks - CRLF (0d0a) - https://book.hacktricks.wiki/en/pentesting-web/crlf-0d-0a.html
