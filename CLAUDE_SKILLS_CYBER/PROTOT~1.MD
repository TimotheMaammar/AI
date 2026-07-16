# Prototype Pollution

**TL;DR**: in JavaScript, injecting properties onto `Object.prototype` via `__proto__`/`constructor.prototype` → affects all objects → DoS, logic bypass, XSS (client) or RCE (Node server-side) via a "gadget".

## Two terrains
- **Client-side (CSPP)**: pollute via query string/hash/parsed JSON in the browser → gadget in a front-end lib → XSS/DOM.
- **Server-side (Node.js)**: pollute via JSON body / query parsing → gadget in the back → RCE (child_process spawn options), auth bypass, SSRF, DoS.

## Injection vectors
- JSON: `{"__proto__":{"polluted":"x"}}`, `{"constructor":{"prototype":{"polluted":"x"}}}`.
- Query/params (libs that parse into objects, e.g. `qs`): `?__proto__[polluted]=x`, `?__proto__.polluted=x`, `?constructor[prototype][polluted]=x`, `?a[__proto__][polluted]=x`.
- Vulnerable functions: recursive merge/extend/clone (`lodash.merge`/`mergeWith`/`defaultsDeep`, `lodash.set`/`setWith`, `$.extend(true,...)`, badly-done `Object.assign`, `deepmerge`), path setters (`dot-prop`, `property-expr`, `Hoek`), query/hash parsers (`deparam` over `location.hash`), config loaders.

## Detection
- **Client**: inject `?__proto__[testprop]=polluted` then in console `Object.prototype.testprop` → `"polluted"`. Tools: **DOM Invader** (Burp) has a prototype-pollution mode; ppmap; "PP-finder" extension.
- **Server**: send `{"__proto__":{"json spaces":10}}` (Express) and observe a change in JSON response formatting (indentation) = pollution confirmed. Or `{"__proto__":{"status":510}}` per gadget. Time/behavior oracles.

## Gadgets → impact
- **Client XSS**: pollute a property read by a sink (`srcdoc`, `src`, template option, sanitizer config `ALLOWED_ATTR`, script `src`) in libs (jQuery, Kendo, etc.). DOM Invader lists gadgets.
- **Server RCE (Node)**: pollute options passed to `child_process.spawn`/`fork` (`NODE_OPTIONS`, `shell`, `env`, `argv0`), or templates (EJS/Pug/Handlebars) → RCE. Known gadgets per framework. Real cases: `_.set` in Kibana (H1 #852613, RCE), ORM query options in typeorm (H1 #869574, PP → SQLi).
- **Auth/logic bypass**: pollute `isAdmin`, `role`, default flags read when absent.
- **DoS**: pollute a property that breaks the runtime.

## Sanitization bypass
- If `__proto__` filtered: `constructor.prototype`, `constructor][prototype`, encoding, duplicate keys.
- Nesting per parser (`[__proto__][x]` vs `__proto__.x`).

## Impact
- Client: XSS (often via gadget) = High. Server: RCE = Critical, or auth bypass/DoS.

## Caido
- Replay/Automate to inject the payloads (query & JSON); observe the oracle (Express JSON formatting, behavior). Confirm client XSS via Chrome/DOM Invader.

## References
- PortSwigger - Prototype pollution - https://portswigger.net/web-security/prototype-pollution
- PortSwigger - Server-side prototype pollution - https://portswigger.net/web-security/prototype-pollution/server-side
- PayloadsAllTheThings - Prototype Pollution - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Prototype%20Pollution
- Client-side PP gadgets (BlackFan) - https://github.com/BlackFan/client-side-prototype-pollution
- HackTricks - Prototype Pollution - https://book.hacktricks.wiki/en/pentesting-web/deserialization/nodejs-proto-prototype-pollution/
