# GraphQL Vulnerabilities

**TL;DR**: a single endpoint (`/graphql`) that usually exposes too much. Targets: introspection, IDOR/BOLA via node IDs, batching for brute-force/DoS, resolver injections, missing field-level access control.

## Recognize & explore
- Endpoints: `/graphql`, `/graphiql`, `/api/graphql`, `/v1/graphql`, `/query`, `/gql`. Also via GET `?query=`.
- **Introspection**: `{__schema{types{name fields{name}}}}` → dump the whole schema. If disabled: field suggestions (error "Did you mean"), `__type`, clairvoyance (graphql-cop/clairvoyance to reconstruct).
  - If `__schema` is filtered by an exact-term regex, append a special char right after it (non-breaking space `\u00A0`, newline) to dodge the filter; use the full fragment-based introspection query (`FullType`/`TypeRef` fragments) for a complete dump.
- Tools: InQL (Caido/Burp plugin), graphql-voyager, graphw00f (engine fingerprint), graphql-cop, clairvoyance, GraphQLmap.

## Trick checklist
- [ ] **Introspection enabled** in prod → full map (info + prepares other attacks).
- [ ] **IDOR/BOLA**: query `user(id:...)`, `node(id: base64)` of another user; global IDs are often base64(`Type:123`) → decode/increment.
- [ ] **BFLA**: admin mutations/queries callable by a normal user (no resolver-level check).
- [ ] **Missing field-level authorization**: a sensitive field (`email`, `token`, `role`) accessible within an otherwise-allowed type.
- [ ] **Batching**: send an array of queries, or **aliasing** to repeat one operation N times in one request → **bypass rate-limit** (OTP/login/coupon brute-force) and amplification.
  ```graphql
  mutation { a:login(pw:"0000"){token} b:login(pw:"0001"){token} ... }
  ```
- [ ] **DoS**: deeply nested/circular queries (query depth), `first: 999999`, massive aliasing → cost. (Do not run a real DoS; sparingly prove the missing limit.)
- [ ] **Resolver injection**: SQLi/NoSQLi/cmd via arguments (`SQL_INJECTION.md`, etc.) - GraphQL does not immunize.
- [ ] **Hidden mutations**: operations not exposed in the UI but present in the schema (delete, setRole, impersonate).
- [ ] **GraphQL CSRF**: if it accepts `application/x-www-form-urlencoded` or GET → CSRF possible (`CSRF.md`).
- [ ] **Info leak**: verbose error messages, stacktraces, debug.
- [ ] **Auth bypass**: an unauthenticated query returning private data.

## Method
1. Get the schema (introspection or suggestion/clairvoyance).
2. List sensitive queries/mutations (user, admin, payment, token).
3. Test unauthorized access (other user, other role, unauthenticated).
4. Batching/aliasing for rate-limit & amplification.
5. Argument injections.

## Impact
- Broad data exposure, ATO via BOLA/BFLA, rate-limit bypass → brute-force. Per operation.

## Caido
- InQL plugin / schema import; Replay modified queries; Automate for aliasing/batching. Decode node IDs via Convert.

## References
- PortSwigger - GraphQL API vulnerabilities - https://portswigger.net/web-security/graphql
- PayloadsAllTheThings - GraphQL - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/GraphQL%20Injection
- OWASP - GraphQL Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html
- graphw00f / graphql-cop / clairvoyance - https://github.com/dolevf/graphw00f
- HackTricks - GraphQL - https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/graphql.html
