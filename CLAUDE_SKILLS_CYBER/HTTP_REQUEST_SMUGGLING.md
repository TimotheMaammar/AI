# HTTP Request Smuggling / Desync

**TL;DR**: disagreement between front-end (proxy/CDN) and back-end on where a request ends → you "smuggle" a partial request that prefixes the victim's. Impacts: front control bypass, cache poisoning, request theft, XSS/creds.

## Basics
- Two ways to delimit the body: `Content-Length` (CL) and `Transfer-Encoding: chunked` (TE). If front and back prioritize different ones → desync.
- Variants: **CL.TE**, **TE.CL**, **TE.TE** (obfuscate TE so one ignores it).
- Modern: **HTTP/2 → HTTP/1 downgrade desync** (H2.CL, H2.TE), **CL.0**, **client-side desync**, **pause-based desync** (H1 #1667974 / CVE-2022-22720).
- Header obfuscation seen in the wild: a **leading space before `Content-Length`** (` Content-Length:`) parsed inconsistently (H1 #2237099); same idea with `Content-Length` casing/duplication.

## Detection (careful - can affect other users)
- **Timing**: a TE.CL/CL.TE payload that makes the back wait (delay) without breaking other requests = safe signal. PortSwigger "timing-based detection".
- Tool: **HTTP Request Smuggler** (Burp ext, Kettle) - automatic CL.TE/TE.CL probe + differential responses. Check for a Caido equivalent plugin.
- Confirm with a smuggled request that affects **your own** next request before involving victims.

## Payloads (scheme)
**CL.TE** (front reads CL, back reads TE):
```
Content-Length: 6
Transfer-Encoding: chunked

0

G
```
**TE.CL** (front reads TE, back reads CL): chunk + short Content-Length.
**TE obfuscation** (TE.TE): `Transfer-Encoding: xchunked`, `Transfer-Encoding:\tchunked`, doubled, spacing/case, `Transfer-Encoding : chunked`.

## Impacts / escalation
- **Bypass front-end controls** (reach `/admin` filtered by the proxy).
- **Cache poisoning / deception** via a smuggled request (`WEB_CACHE_POISONING.md`).
- **Capture other users' requests** (steal cookies/CSRF token) - the smuggled prefix makes their request appear in a response to you.
- **Reflected XSS** amplified / forced on others.
- **Persistent web cache poisoning**.

## BB caution
- Smuggling can **impact real users**. Test with timing first, avoid techniques that poison shared connections in prod uncontrolled. Respect scope. Minimal PoC, no campaign.

## Caido
- Requires sending precise raw requests (CL/TE, no re-normalization). Verify Caido does not alter the headers; otherwise use HTTP Request Smuggler (Burp) for detection, document in Caido.

## References
- PortSwigger - HTTP request smuggling - https://portswigger.net/web-security/request-smuggling
- PortSwigger - Finding/exploiting (Kettle research) - https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- PortSwigger - Browser-powered desync / HTTP/2 - https://portswigger.net/research/browser-powered-desync-attacks
- HTTP Request Smuggler - https://github.com/PortSwigger/http-request-smuggler
- smuggler.py (defparam) - https://github.com/defparam/smuggler
- PayloadsAllTheThings - Request Smuggling - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Request%20Smuggling
- YesWeHack guide - HTTP request smuggling - https://www.yeswehack.com/learn-bug-bounty/http-request-smuggling-guide-vulnerabilities
