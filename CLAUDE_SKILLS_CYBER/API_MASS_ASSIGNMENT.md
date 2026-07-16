# API Security & Mass Assignment

**TL;DR**: REST/JSON APIs concentrate BOLA, BFLA, mass assignment, excessive data exposure. Mass assignment = inject fields the back-end blindly binds to the object (`isAdmin`, `role`, `balance`).

## API recon
- Find specs: `/swagger.json`, `/openapi.json`, `/api-docs`, `/v2/api-docs`, `/graphql`, `.well-known/`, public Postman collections, front-end JS.
- Multiple versions: `/v1` vs `/v2` (the old one less protected). Mobile endpoints.
- Methods: test `OPTIONS`, `PUT`, `PATCH`, `DELETE` on resources.

## Mass assignment / autobinding
- Add unexpected fields to the body:
  - `{"isAdmin":true}`, `{"role":"admin"}`, `{"verified":true}`, `{"balance":99999}`, `{"user_id":<victim>}`, `{"account_type":"premium"}`, `{"emailVerified":true}`, `{"is_staff":true}`, `{"permissions":[...]}`, `{"price":0}`, `{"status":"approved"}`.
- Discover the fields: read the object's GET response (returned fields are often settable), GraphQL introspection, the spec, the JS.
- Nesting: `{"user":{"role":"admin"}}`, arrays, dot-notation (`"user.role":"admin"`), per framework (Rails/Laravel/Spring/Django autobinding).
- **Update vs create**: test on PATCH/PUT of an existing object AND at signup.

## Other API classes (OWASP API Top 10 2023)
- **API1 BOLA** → `IDOR_BROKEN_ACCESS_CONTROL.md`.
- **API2 Broken Auth** → `AUTH_SESSION.md`, `JWT.md`.
- **API3 Broken Object Property Level Auth**: mass assignment (write) + excessive data exposure (read: the response returns more fields than the UI shows → read the raw JSON for PII/secrets).
- **API4 Resource consumption**: no rate-limit/pagination → DoS/cost, brute-force.
- **API5 BFLA**: admin functions callable by a normal user (change method/route).
- **API6 Unrestricted access to business flows** → `BUSINESS_LOGIC.md`.
- **API7 SSRF** → `SSRF.md`.
- **API8 Security misconfiguration**: CORS, verbs, headers, debug.
- **API9 Improper inventory**: versions/old endpoints/staging (`api-dev`, `staging-api`).
- **API10 Unsafe consumption of 3rd-party APIs**.

## Quick checklist
- [ ] Read the raw JSON (excessive data exposure: hidden token/PII in the response).
- [ ] Inject privileged fields (mass assignment) at signup + update.
- [ ] Test BOLA/BFLA (other ID, other role, unauthenticated).
- [ ] Change method/version/content-type.
- [ ] Rate-limit on sensitive endpoints.

## Caido
- Replay to add fields to the JSON; compare the GET response (fields) → candidates to inject in PUT/PATCH. Automate to enumerate endpoints/versions.

## References
- OWASP API Security Top 10 (2023) - https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- PortSwigger - API testing - https://portswigger.net/web-security/api-testing
- PayloadsAllTheThings - Mass Assignment - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Mass%20Assignment
- OWASP - Mass Assignment Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html
- OWASP - REST Security Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
