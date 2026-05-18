# Web / SaaS deep checklist

Load when the documented product is a web application, SaaS platform, REST/GraphQL API, internal web tool, or any browser-accessible service. Many findings below are also relevant to admin web UIs of binary/desktop products, load both checklists when the doc covers a desktop app with a web admin.

This checklist complements (does not replace) phases 2-4. Use it to make sure no web-specific category was missed.

---

## A. Authentication

Read every auth-related section and note:

- [ ] **Auth methods supported.** List all: password, MFA, OAuth/OIDC, SAML, mTLS, API token, magic link, social, anonymous. Each method is a separate surface.
- [ ] **Are there unauthenticated endpoints?** Health, metrics, public APIs, embed widgets, OAuth metadata, OIDC discovery, robots.txt-listed paths.
- [ ] **MFA bypasses.** Does the doc enumerate where MFA *is* required and where it's *not*? Common gaps: API key auth, OAuth login, password reset, "remember device", account recovery.
- [ ] **Password reset flow.** Token in URL? Token length and entropy mentioned? Single-use enforced? Rate-limited? Old session invalidation on reset?
- [ ] **Account enumeration.** Different error for "wrong user" vs "wrong password"? Different timing? Does signup tell you if email is taken?
- [ ] **Account lockout / brute-force protection.** Threshold and reset window. Per-IP vs per-account.
- [ ] **OAuth / OIDC configuration.** Allowed redirect_uri patterns (wildcards, subdomain wildcards, fragments). State parameter required? PKCE enforced for public clients?
- [ ] **SAML configuration.** Signature validation, audience checks, replay protection, IdP-initiated bypass, multiple Assertion handling.
- [ ] **JWT details.** Algorithm enforced? Public/private key separation? Key rotation? `kid` header handling? Audience and issuer validation?
- [ ] **Session management.** Cookie attributes (`HttpOnly`, `Secure`, `SameSite`). Token rotation on auth events. Logout server-side. Session fixation prevention.
- [ ] **"Remember me" / persistent sessions.** Revocable? Rotated on password change? Bound to device fingerprint?
- [ ] **Service-to-service auth.** mTLS? Shared secrets in headers? IP allowlist? Time-limited tokens?
- [ ] **Impersonation / "login as".** Auditing? Restricted to support role? Bypass MFA? Re-auth required?

## B. Authorization

- [ ] **Roles documented.** Are roles enumerated? Are permissions per-role listed? Look for "admin" / "owner" / "member" / "guest" tiers.
- [ ] **Multi-tenant model.** Is data isolation enforced server-side or only UI-side? Cross-tenant IDOR is one of the most common SaaS findings.
- [ ] **Object IDs.** Sequential? UUIDs? Predictable from username/email? IDOR risk inversely correlates with ID entropy.
- [ ] **API granularity vs UI granularity.** Is the API more permissive than the UI? (Frequent finding: UI hides options the API still accepts.)
- [ ] **"Forgotten" endpoints.** Legacy v1 API still running alongside v2 with different auth?
- [ ] **Webhook receivers.** What auth on inbound webhooks? Often weaker than user endpoints.
- [ ] **Sharing model.** Public links / "share with anyone with the link", token in URL → search engines, referrer leaks?
- [ ] **Permission inheritance.** Child objects inherit parent permissions? What happens when parent is reshared?

## C. Input handling and parsers

- [ ] **What body content-types accepted?** JSON only, or also XML, multipart, urlencoded, custom? More types = more parser surface.
- [ ] **XML accepted anywhere?** XXE / billion laughs surface. Even one endpoint is enough.
- [ ] **GraphQL?** Introspection enabled? Query depth/complexity limits? Aliasing / batching abuse? Field-level auth or only top-level?
- [ ] **File upload.** Types accepted, validation (extension, content-type, magic bytes), storage location, served from same origin?
- [ ] **Archive upload.** Zip Slip / decompression bomb surface.
- [ ] **Image upload.** SVG handling (XSS), polyglot files, ImageMagick/Pillow CVE surface.
- [ ] **Document upload.** PDF JS / DOCX template injection / Office macros.
- [ ] **CSV import/export.** Formula injection risk on Excel-open.
- [ ] **Markdown rendering.** Raw HTML allowed? `javascript:` URIs in links? Sanitizer used? Markdown engines have a long XSS history.
- [ ] **HTML rendering of user content.** Sanitizer used? Library and version?
- [ ] **Template engines anywhere.** Jinja, Twig, Handlebars, Freemarker, Velocity. User input ever flows into template *source* (not just template values)?
- [ ] **Email rendering.** HTML emails composed server-side from templates? User input in subject / body?

## D. SSRF surfaces

- [ ] **Webhooks** (outbound, user-configurable URL).
- [ ] **Link unfurling / URL preview.**
- [ ] **OAuth issuer / OIDC discovery** (issuer URL configurable).
- [ ] **SAML metadata import from URL.**
- [ ] **Avatar / profile picture fetched from URL.**
- [ ] **RSS / Atom / Feed integration.**
- [ ] **PDF generation from URL.**
- [ ] **Screenshot / preview generation.**
- [ ] **Import-from-URL** (any "load from URL" feature).
- [ ] **Webhook signature URL** (if the doc has features that fetch from URLs for signature validation).
- [ ] **Proxy / forwarding features.**
- [ ] **API integrations with user-supplied endpoints** (Zapier-style).

For each, check: are there allowlists? DNS resolution restrictions? Cloud-metadata IP blocked (`169.254.169.254`, `fd00:ec2::254`)? Loopback blocked? RFC1918 blocked? `file://` scheme blocked? Redirects followed?

## E. Open redirects and URL handling

- [ ] **Login redirect parameter** (`?next=`, `?return_to=`, `?continue=`).
- [ ] **OAuth `redirect_uri` validation.**
- [ ] **SSO redirect after auth.**
- [ ] **Post-action redirects** (after form submit, etc.).
- [ ] **Email link tracking redirects.**

Open redirects chain with OAuth/SAML to become full token theft.

## F. CORS and cross-origin

- [ ] **`Access-Control-Allow-Origin` policy.** Static? Reflected? Wildcard?
- [ ] **`Allow-Credentials: true` combined with reflected Origin.**
- [ ] **Subdomain wildcard** (`*.example.com`) combined with subdomain takeover.
- [ ] **postMessage handlers** in any embedded frames or widgets.
- [ ] **JSONP** still supported anywhere.
- [ ] **Embeddable iframes.** Clickjacking protection (`X-Frame-Options`, `Content-Security-Policy: frame-ancestors`).

## G. CSP and other security headers

- [ ] **CSP policy stated in doc** (vendor often documents it; check for `unsafe-inline`, `unsafe-eval`, wildcard sources).
- [ ] **HSTS** mentioned.
- [ ] **`X-Content-Type-Options: nosniff`** for upload-served paths.
- [ ] **Referrer-Policy.**

## H. Rate limiting and DoS

- [ ] **Rate limits mentioned per endpoint.** Per-user, per-IP, per-token?
- [ ] **Expensive operations** (PDF generation, image processing, large file parsing): rate-limited?
- [ ] **Bulk endpoints / GraphQL aliasing**: multipliers on a single request.

## I. Logging and audit

- [ ] **What is logged?** User actions, admin actions, auth events?
- [ ] **PII / secrets in logs.** Tokens, passwords, API keys reflected in logs?
- [ ] **Log access.** Who can read logs? Admin UI displaying logs is a stored-XSS vector for log-injecting attackers.

## J. Admin and debug surfaces

- [ ] **Admin web UI**: separate auth? Separate port? Separate domain?
- [ ] **Debug/dev/diagnostic endpoints**: listed in the doc, sometimes hidden in appendices.
- [ ] **Internal-only endpoints**: `/internal/`, `/_/`, `/.well-known/`.
- [ ] **Health/metrics** with sensitive info (env vars, build info, git SHA, dep versions).
- [ ] **Profiler / debugger / REPL** endpoints (`/debug/pprof`, `/_debug`, `/console`).

## K. Infrastructure / deployment

- [ ] **Reverse proxy assumed?** Trust headers (`X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-User`)?
- [ ] **Trust of `X-Forwarded-*` headers without auth** → IP bypass / user impersonation.
- [ ] **Default ports.** Often left exposed accidentally.
- [ ] **Default credentials** mentioned in deployment guide.
- [ ] **TLS configuration.** Min version, cipher suites, cert validation toggleable?
- [ ] **Database connection.** SSL required? Credentials passed where?
- [ ] **Container image base.** Old base image = old CVE base.
- [ ] **Kubernetes service account / pod permissions.**

## L. Integrations

- [ ] **OAuth provider integrations** (Google, Microsoft, etc.).
- [ ] **LDAP / AD**: bind credential storage, search filter injection, group mapping logic.
- [ ] **Storage backends** (S3, Azure Blob, GCS), credential handling, bucket name configurable.
- [ ] **Database connectors with user-supplied connection strings**: JDBC injection, connection string manipulation.
- [ ] **Email** (SMTP outbound credentials, inbound parsing).
- [ ] **Messaging** (Slack, Teams, Discord webhooks, webhook URL leakage).

## M. Specific high-risk patterns to grep for

Run these searches across the extracted text:

```
# SSRF
rg -i "fetch.*url|http.get|callout|webhook|preview|unfurl|proxy|outbound"

# Templating
rg -i "jinja|twig|handlebars|freemarker|velocity|erb|liquid|template engine|render template"

# Deserialization
rg -i "pickle|unserialize|deserialize|BinaryFormatter|ObjectInputStream|YAML.load(?!_safe)"

# Crypto smells
rg -i "ECB|MD5|SHA1|RC4|DES|custom encryption|our own"

# Trust headers
rg -i "X-Forwarded|X-Real-IP|X-Original|trust.*header|proxy.*header"

# SQL
rg -i "raw query|concatenat.*query|string.format.*select|where.*\\+"

# Open URLs
rg -i "redirect_uri|return_to|next_url|continue_url|callback_url"

# Sandboxes (always interesting)
rg -i "sandbox|isolat|restrict.*runtime|secure mode"

# Admin
rg -i "admin|superuser|root user|owner role|impersonat"

# Debug
rg -i "debug|diagnostic|profiler|dev mode|developer mode"
```

## N. Per-chapter additions

When reading any chapter:

- Note every endpoint mentioned with its method, path, auth requirement.
- Note every file format accepted with parser library if specified.
- Quote any sentence that includes a passive admission ("requires", "must", "needs", "should", these often reveal preconditions or unenforced expectations).
- Quote any sentence about defaults (`by default, X is...`).
- Quote any sentence about exceptions (`unless...`, `except when...`, `if X is enabled, then...`), these are conditional paths through the security model.

---

## Output addition

Append to phase 2's attack-surface list any items the checklist surfaced that the chapter-by-chapter reading missed. The checklist's job is to catch what was skipped, not to replace the linear reading.
