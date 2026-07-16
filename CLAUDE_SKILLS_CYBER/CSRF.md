# Cross-Site Request Forgery (CSRF)

**TL;DR**: force an authenticated victim's browser to perform an unwanted state-changing action. Exploitable only if the action relies on auto-sent credentials (cookies) with no robust anti-CSRF. Check SameSite before claiming victory.

## Exploitability prerequisites
- **State-changing** action (POST/PUT/DELETE, or GET with side effect).
- Auth via **auto-sent cookie** (not via an Authorization/custom header a third-party site cannot add).
- No valid anti-CSRF token required, OR token bypassable.
- Session cookie not blocking via `SameSite=Strict/Lax` (see below).

## Checklist
- [ ] Remove the CSRF token → does the action pass? (often not validated server-side).
- [ ] Another user's/session's token → accepted? (not tied to the session).
- [ ] Empty token / dummy value of correct length?
- [ ] Change method: `POST`→`GET` (sensitive action on GET = trivial CSRF), or method override.
- [ ] Is the token only in a cookie (bad double-submit) → duplicate/predict.
- [ ] Content-Type: switch from `application/json` (preflight-protected) to `text/plain`/`form-urlencoded` → does the API still accept it? (dodges CORS preflight).
- [ ] Token required only on some flows (mobile/unprotected API).
- [ ] Token reuse (not one-time).

## SameSite (the big modern filter)
- `SameSite=Strict`: blocks cross-site → classic CSRF dead (except same-site subdomain XSS/redirect).
- `SameSite=Lax` (Chrome default): allows **top-level GET navigation** → CSRF possible if the action accepts a top-level GET; POST blocked.
- `SameSite=None`: cross-site allowed → CSRF possible.
- Lax bypass: find a GET endpoint that performs the action, or a method override via GET.
- **Fresh cookie** (Chrome "Lax+POST" grace period ~2 min after set): window where cross-site POST passes.

## PoC
- Auto-submit form:
```html
<form action="https://target/account/email" method="POST">
  <input name="email" value="attacker@evil.com">
</form><script>document.forms[0].submit()</script>
```
- GET: `<img src="https://target/action?x=1">`.
- JSON forced as form: `enctype="text/plain"` + key=value trick to approximate the JSON.

## Beating protections
- **Referer-based**: strip the Referer (`<meta name="referrer" content="no-referrer">`) if the server "validates only if present", or partial spoof (`https://target.evil.com`, `https://evil.com/target`).
- **Double-submit cookie**: if the CSRF cookie is settable via another vuln/subdomain → inject the same value.
- **Token in custom header**: impossible cross-site unless CORS is misconfigured → `CORS.md`.

## Chaining
- CSRF to change email → then password reset → **ATO**.
- Login CSRF (force login into the attacker's account) → capture the victim's activity.
- CSRF + self-XSS = exploitable XSS.

## Impact
- ATO (change email/password/2FA), settings change, transfers, depending on the action. Severity = that of the forced action.

## Caido
- Replay: remove/alter the token, change method/content-type, observe if accepted. Generate the HTML PoC once the weakness is confirmed.

## References
- PortSwigger - CSRF - https://portswigger.net/web-security/csrf
- PortSwigger - SameSite cookies - https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions
- OWASP - CSRF Prevention Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- PayloadsAllTheThings - CSRF - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/CSRF%20Injection
- OWASP WSTG - Testing for CSRF - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/05-Testing_for_Cross_Site_Request_Forgery
