# JWT Attacks

**TL;DR**: JSON Web Tokens often carry identity/roles. Target signature verification (`alg:none`, RS256→HS256 confusion, weak key), manipulable claims, and key leaks.

## Recognize
- Cookie/header `Authorization: Bearer eyJ...` (3 base64url parts split by `.`).
- Decode header+payload (Caido Convert / jwt.io / jwt_tool). Note `alg`, `kid`, `iss`, role claims (`role`, `admin`, `scope`, `user_id`, `email`).

## Signature attacks
- [ ] **`alg: none`**: set `{"alg":"none"}`, empty signature → accepted if the lib does not forbid it. Case variants: `None`, `nONE`, `NONE`.
- [ ] **RS256 → HS256 confusion**: the server verifies RS256 with the public key; re-sign HS256 using the **public key** (often retrievable: `/jwks.json`, TLS cert, endpoint) as the HMAC secret → valid forgery.
- [ ] **Weak HMAC secret**: offline brute-force (`hashcat -m 16500`, jwt_tool wordlist, `jwt-secrets` list). Common secrets (`secret`, `changeme`, framework key).
- [ ] **`kid` injection**: path traversal (`kid: ../../dev/null` → empty/known key), SQLi in `kid`, point `kid` at a predictable file.
- [ ] **`jku`/`x5u` header**: force the server to fetch YOUR JWKS key (SSRF-like) → forgery. Test the `jku` domain allowlist.
- [ ] **Signature not verified at all**: alter the payload without re-signing → accepted? (frequent bug).
- [ ] **Algorithm swap** to an unsupported/empty alg.

## Claims / logic attacks
- [ ] Modify `role`/`isAdmin`/`user_id`/`sub`/`email` (if the signature is breakable).
- [ ] Expiry: `exp` ignored (replay an old token), very distant `exp` accepted at creation.
- [ ] **No invalidation**: token valid after logout/password change.
- [ ] `aud`/`iss` not verified → token from another service/tenant accepted (cross-service).
- [ ] Claim type confusion (`user_id: "1"` vs `[1]`).

## Key leaks
- Look for the secret/private key in: front-end JS, repos, `.env`, debug endpoints, Flask SECRET_KEY (via SSTI/LFI → forgery).

## Tools
- `jwt_tool` (all-in-one: tamper, crack, RS/HS confusion, jku/kid), `hashcat -m 16500`, jwt.io, Caido/Burp JWT plugins.
  - `jwt_tool <TOKEN> -T` (tamper wizard); `jwt_tool -M at -t <URL> -rh "Authorization: <TOKEN>"` (all attacks vs a live endpoint, add `-cv "<canary>"` to grep a difference); `jwt_tool -C -d rockyou.txt <TOKEN>` (crack HMAC secret).

## Impact
- Identity/role forgery = ATO / privesc = High/Critical.

## Caido
- Convert to decode; JWT plugin (or workflow) to re-sign; Replay to test `alg:none` / a non-re-signed altered token.

## References
- PortSwigger - JWT attacks - https://portswigger.net/web-security/jwt
- PortSwigger - Algorithm confusion - https://portswigger.net/web-security/jwt/algorithm-confusion
- PayloadsAllTheThings - JSON Web Token - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/JSON%20Web%20Token
- OWASP - JWT Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- jwt_tool - https://github.com/ticarpi/jwt_tool
- HackTricks - JWT - https://book.hacktricks.wiki/en/pentesting-web/hacking-jwt-json-web-tokens.html
