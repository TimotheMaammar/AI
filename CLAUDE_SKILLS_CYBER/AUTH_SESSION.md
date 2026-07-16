# Authentication & Session

**TL;DR**: break login, reset, MFA, or session management to take over accounts. ATO = bug bounty gold. Test every stage of the account lifecycle.

## Surface
Login, signup, logout, "remember me", password reset, change email, change password, MFA/2FA, SSO/OAuth (`OAUTH.md`), session tokens/cookies, JWT (`JWT.md`), API keys.

## Login / brute-force / enumeration
- [ ] **User enumeration**: different messages ("user not found" vs "wrong password"), different timing, HTTP codes, signup response ("email already taken"), reset ("if the account exists" vs direct confirmation).
- [ ] **Rate-limit / lockout**: absent? bypassable (X-Forwarded-For rotation, email case, alternate endpoints, counter reset) → `00_WAF_ENCODING.md`.
- [ ] **Credential stuffing** feasibility (no captcha/MFA).
- [ ] **Default/weak creds** on panels (admin/admin, etc.).
- [ ] Weak **password policy**.

## Password reset (often the best ATO vector)
- [ ] **Host header poisoning**: reset link built with attacker `Host`/`X-Forwarded-Host` → token exfiltrated → `HOST_HEADER_INJECTION.md`.
- [ ] **Weak token**: predictable (timestamp, sequential, short), no expiry, reusable, not tied to the user.
- [ ] **Token leak**: in Referer to third-party resources, in logged URL, returned in the JSON response.
- [ ] **IDOR on reset**: `POST /reset {user_id: victim}` with no proof of ownership.
- [ ] **Response leak**: the token/OTP returned in the HTTP response.
- [ ] **Race** on reset/OTP → `RACE_CONDITIONS.md`.
- [ ] **Email change without re-auth** + reset = ATO.
- [ ] **Password change** that does not ask for the old password (+ CSRF → ATO).

## MFA / 2FA bypass
- [ ] Post-login endpoint reachable **without** validating the OTP (direct access to the authenticated resource).
- [ ] **OTP brute-force**: no rate-limit (6 digits = 10^6; often limited but test), no invalidation after N tries, code that does not change.
- [ ] **Reuse / non-invalidation** of the code, weak test/backup code.
- [ ] **Manipulable flag**: `mfa_verified=true`, `2fa=false` in body/JWT/response.
- [ ] **OAuth/SSO flow** that skips 2FA.
- [ ] **"Remember device"** forgeable.
- [ ] Response that **leaks** the code (JSON) or the status ("code correct" leaked before the next step).
- [ ] **Downgrade**: force a flow without MFA (recovery code, old API).

## Session management
- [ ] Session **not invalidated** on logout / password change.
- [ ] **Predictable token** / low entropy.
- [ ] **Session fixation**: session unchanged after login (fix a pre-login session).
- [ ] Cookies without `HttpOnly`/`Secure`/`SameSite`.
- [ ] Token in URL (leak via Referer/logs).
- [ ] Concurrent sessions unmanaged; "sign out all" ineffective.
- [ ] **Long-lived** tokens, trivially forged "remember me".
- [ ] JWT → `JWT.md`.

## Registration
- [ ] Sign up as admin (email domain, `role` field → `API_MASS_ASSIGNMENT.md`).
- [ ] Bypassable email verification; pre-create an account on a future victim's email (pre-account-takeover, then SSO).
- [ ] Unicode/dot/email normalization → account collision.

## Impact
- Full ATO = High/Critical. Enumeration alone = Low/Info (but useful in a chain).

## Caido
- Automate to test OTP/rate-limit (within program limits). Match & Replace to flip session flags. Compare responses (len/timing) for enumeration.

## References
- PortSwigger - Authentication - https://portswigger.net/web-security/authentication
- OWASP - Authentication Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP - Forgot Password / Session Management Cheat Sheets - https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
- OWASP WSTG - Authentication & Session Testing - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/
- PayloadsAllTheThings - Account Takeover / 2FA bypass - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Account%20Takeover
