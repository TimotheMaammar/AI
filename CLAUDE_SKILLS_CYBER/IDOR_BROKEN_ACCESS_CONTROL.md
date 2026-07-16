# IDOR / Broken Access Control

**TL;DR**: the app lets you access/modify an object or function that is not yours. The #1 bug bounty class: frequent, often High/Critical, invisible to scanners. Always create **2 accounts (A and B)** + test unauthenticated.

## Types
- **Horizontal IDOR**: access another same-level user's data (B's object from A).
- **Vertical IDOR / privilege escalation**: a low-priv user reaches an admin function.
- **Function-level access control (BFLA)**: unprotected endpoint/action (not just the object).
- **Object-level (BOLA)**: object ID not checked against its owner.
- **Unauthenticated**: resource reachable with no session at all.

## Where to look (signals)
- IDs in URL/body/JSON/cookie/header: `?id=`, `/users/123`, `/orders/456`, `account_id`, `uuid`, `file`, `doc`, `invoice`, `msg`, `ticket`.
- **Export / download / print / PDF / report** endpoints (mass leak).
- **API** endpoints (`/api/v1/users/{id}`), GraphQL node/id, mobile API (often less protected).
- **Write** actions: update profile, change email, delete, transfer, invite, role change.
- Hidden params carrying identity: `user_id` in the body when the session alone should suffice.
- Batch/bulk endpoints, filters (`?owner=`, `?tenant=`).

## Trick checklist
- [ ] Replace your ID with B's (sequential numeric = trivial; UUID = guess via another endpoint that lists them).
- [ ] Replay the request **without** cookie/token (unauthenticated).
- [ ] Replay with B's token on A's object (both directions).
- [ ] Role downgrade: low-priv account on admin endpoint.
- [ ] Change the **HTTP method**: if `GET /user/2` is blocked, try `POST/PUT/DELETE`, or `GET` on a `POST`-only endpoint.
- [ ] **Add** the ID when implicit: `/api/me` → `/api/me?id=2`, or add `user_id=2` to the body.
- [ ] **Wrap** the ID: `id[]=2`, `id=2,3`, `{"id":["2"]}`, `id=2&id=3` (HPP), JSON vs form.
- [ ] Change **format**: `/user/2` → `/user/2.json`, `.xml`, `/user/2/`, path vs query.
- [ ] **Encode** the ID: predictable hash? base64(`user@x.com`)? `2` → `Mg==`? increment the cleartext then re-encode.
- [ ] **UUID/GUID**: harvest them via a listing endpoint (search, autocomplete, invitations, comments, `@mentions`), Wayback, or error responses.
- [ ] **Blind / write-only IDOR**: no data returned? Check the side effect (email sent to B, object modified as seen from B's account).
- [ ] **Front-end-only control**: button greyed out but the API responds anyway.
- [ ] **403/401 bypass**: see `00_WAF_ENCODING.md` (headers `X-Original-URL`, path tricks, method).
- [ ] **Multi-tenant**: change `tenant_id`/`org_id`/`workspace` in path/subdomain/header.
- [ ] **GraphQL**: request a node by global ID, aliasing for batch → `GRAPHQL.md`.

## Harvesting others' IDs (to prove impact)
- Listing endpoints: search, autocomplete, "share with", mentions, activity feed, notifications.
- Predictability: sequential, timestamp, snowflake, per-tenant increment.
- Leaks: verbose responses, `Location` header, emails, Wayback.

## Escalation / impact
- Read other users' PII → data breach (showing 2 users is enough).
- Modify another account's email/password → **ATO**.
- Reach admin endpoint → vertical escalation.
- IDOR on an export endpoint → mass leak (show the mechanism, not a full dump).
- Write (delete/transfer/role) → integrity, business impact.

## False positives to rule out
- Object is **public by design** (published post, public profile).
- ID is an **unguessable secret** AND never disclosed elsewhere (capability URL) → lower severity; mention the leak if one exists.

## Caido
- Capture a request from account A (with its cookie/token). In Replay, swap the object ID to B's → 200 + B's data = IDOR.
- Full test: (1) session A on B's object, (2) session B on A's object, (3) unauthenticated, (4) low role on admin action.
- Match & Replace: auto-swap A's session cookie for B's across all traffic to re-browse the app "through B's eyes".
- Automate: iterate a sequential numeric ID + grep-extract on email/name to prove enumeration (keep the volume reasonable).

## References
- PortSwigger - Access control & IDOR - https://portswigger.net/web-security/access-control
- PortSwigger - IDOR - https://portswigger.net/web-security/access-control/idor
- OWASP WSTG - Authorization Testing - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/
- OWASP API Top 10 - BOLA (API1) & BFLA (API5) - https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
- PayloadsAllTheThings - IDOR - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Direct%20Object%20References
- OWASP Cheat Sheet - Authorization - https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
