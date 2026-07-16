# Web Cache Poisoning & Deception

**TL;DR**: two distinct flaws. **Poisoning**: inject a malicious response into a shared cache served to other users (via a reflected non-keyed input). **Deception**: trick the cache into storing a private page the attacker then reads.

## Key concepts
- **Cache key** = what identifies an entry (often host+path+query). Inputs **not in the key** (headers, some params) but that **influence the response** = poisoning surface.
- Spot the cache: `X-Cache: hit/miss`, `Age`, `CF-Cache-Status`, `X-Served-By`, `Cache-Control`, CDN behavior (Cloudflare, Akamai, Fastly, Varnish).

## Cache Poisoning - method
1. Identify a reflected **non-keyed input**: headers (`X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Host`, `X-Forwarded-For`, `User-Agent`, `X-Original-URL`), or params excluded from the key.
2. Verify it **influences the response** (reflected in a `<script src>`, link, redirect, content).
3. Verify the response is **cached** (`X-Cache: hit` on 2nd call, growing `Age`).
4. Inject a payload (XSS via `X-Forwarded-Host` reflected in a script src → loads attacker JS), confirm others get the poisoned version.
- Tools: Param Miner (detects non-keyed "cache buster" headers), Caido Automate.

## Frequent vectors
- `X-Forwarded-Host` reflected in an absolute URL → redirect/script to attacker domain (chain with `HOST_HEADER_INJECTION.md`).
- Unescaped reflection → **hidden XSS** served to all.
- Params excluded from the key that change content (`?utm=`, `?callback=`).
- **Cache key normalization**: encoding/case differences that collapse to the same key but different responses.
- **Fat GET**, param cloaking, exotic delimiters (`;`, `#`) that diverge between cache and origin → "cache key injection".
- **Cache DoS** (CPDoS): poison with an error response (oversize header → cached 400).

## Cache Deception - method
- Request a private page with an extension/segment that makes the cache think it is static: `/account/profile.css`, `/account/profile/nonexistent.js`, `/api/me;foo.css`.
- If the origin still serves the private content AND the CDN caches by extension → the attacker retrieves `/victim/profile.css` from the cache.
- Test: path confusion (`.css`, `.js`, `/foo.png`, `%2e`, `;`, `//`), see whether the private response is cached.

## Impact
- Poisoning: XSS/redirect/defacement served en masse = High. Deception: theft of other users' private data = High.

## Caido
- Automate/Param-Miner-like for non-keyed headers; Replay to confirm hit/miss; Match & Replace to inject the header across traffic.

## References
- PortSwigger - Web cache poisoning - https://portswigger.net/web-security/web-cache-poisoning
- PortSwigger - Web cache deception - https://portswigger.net/web-security/web-cache-deception
- James Kettle - Practical Web Cache Poisoning - https://portswigger.net/research/practical-web-cache-poisoning
- PayloadsAllTheThings - Web Cache Deception - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Web%20Cache%20Deception
- OWASP WSTG - Web Security Testing Guide - https://owasp.org/www-project-web-security-testing-guide/
- YesWeHack guide - SSTI / cache poisoning / logic - https://www.yeswehack.com/learn-bug-bounty/ssti-cache-poisoning-logic-vulnerabilities
