# OAuth 2.0 / SSO Attacks

**TL;DR**: OAuth/OIDC flows are full of config bugs → ATO. Key targets: `redirect_uri`, `state`, `code` reuse, implicit flow leaks, account linking.

## Recognize the flow
- Params: `client_id`, `redirect_uri`, `response_type` (`code`=auth code, `token`=implicit), `scope`, `state`, `nonce`, `code_challenge` (PKCE).
- "Login with Google/GitHub/Facebook/SSO", endpoints `/authorize`, `/callback`, `/oauth`.

## Main attacks
- [ ] **Lax redirect_uri**: the auth server accepts a non-strictly-matched `redirect_uri` → redirect the `code`/`token` to the attacker → **ATO**.
  - Bypass: subdirectory (`/callback/../evil`), path traversal (`../`), subdomain, path append, `@`, `#`, query append, open redirect on the legit domain (chain: `OPEN_REDIRECT.md`), weak regex, and **IDN homograph / unicode look-alike domains** to pass a loose validator (H1 #861940).
- [ ] **Missing/unverified state** → **CSRF on the flow** (login CSRF, forced account linking: link the attacker's social account to the victim, or vice versa).
- [ ] **`state` misused as a redirect target** (H1 #206591): if `state` carries a return URL instead of an opaque CSRF token, it becomes an open redirect that leaks the code/token.
- [ ] **Account linking**: link a social identity to an existing account without verifying email ownership → ATO.
- [ ] **Pre-account-takeover**: create an account with the victim's email before they sign up via SSO; on their SSO, the accounts merge.
- [ ] **Code reuse / no expiry**: replay a `code` (must be single-use, short).
- [ ] **Code substitution / injection**: inject a `code` obtained for another client.
- [ ] **Implicit flow token leak**: `token` in the `#` fragment → leak via Referer/open redirect/XSS.
- [ ] **Scope upgrade**: request more scope, or reuse a token for an unconsented scope.
- [ ] **PKCE absent/downgrade** (mobile/public clients) → code interception.
- [ ] **client_secret leak** in front-end/mobile JS.
- [ ] **ID token (OIDC)**: `alg:none`, unverified signature, unverified `aud`/`iss` → `JWT.md`.
- [ ] **SSRF via OIDC**: `request_uri`, JWKS `jku` fetch.
- [ ] **Unverified provider email** treated as verified → impersonation.

## Method
1. Map the full flow (Caido HTTP history), spot `redirect_uri`/`state`/`code`.
2. Test every `redirect_uri` relaxation.
3. Remove `state` → CSRF.
4. Check single-use/expiry of the `code`.
5. Test linking from 2 accounts.

## Impact
- Full ATO via SSO = High/Critical.

## Caido
- Follow the flow in HTTP history; Replay to alter `redirect_uri`/`state`; generate the linking/CSRF PoCs.

## References
- PortSwigger - OAuth 2.0 authentication vulnerabilities - https://portswigger.net/web-security/oauth
- PayloadsAllTheThings - OAuth Misconfiguration - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/OAuth%20Misconfiguration
- OAuth 2.0 Security Best Current Practice (RFC 9700) - https://datatracker.ietf.org/doc/html/rfc9700
- OWASP - OAuth2 Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html
- HackTricks - OAuth to Account Takeover - https://book.hacktricks.wiki/en/pentesting-web/oauth-to-account-takeover.html
