# Phase 4: Vulnerability hypotheses

Take every entry from phases 2 and 3 and convert it into a concrete, falsifiable hypothesis.

A hypothesis has five fields:

1. **Feature**: name and page reference.
2. **Vuln class(es)**: the CWE/OWASP/historical category this most plausibly belongs to.
3. **Scenario**: one paragraph explaining how an attacker exploits this in realistic conditions.
4. **Preconditions**: what the attacker needs (auth level, network position, config, victim interaction).
5. **Evidence vs unknowns**: what the doc confirms, what is unstated and would need testing or source review.

Each hypothesis should be falsifiable: a tester reading it knows what to test, and the test has a clear pass/fail outcome.

---

## Section 1: Feature-to-vuln mapping (reference table)

Use this as a lookup. Most features in phases 2-3 map to one or more rows below. When in doubt, list multiple classes; the priority phase will sort them.

### File upload and import

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| Image upload | ImageMagick / Pillow CVEs, polyglot files, SVG XSS | Upload crafted SVG with embedded JS → stored XSS in viewer; upload polyglot JPEG/PHP → unrestricted upload + filename rewrite for RCE |
| Document upload (PDF, Office) | PDF JS, Office macros, OLE, document parser CVEs | PDF with JS in form action; DOCX with external template URL → SSRF / NTLM hash leak |
| Archive upload (ZIP, TAR) | Zip Slip, decompression bomb, symlink overwrite | ZIP with `../../etc/cron.d/x` entry → arbitrary file write; tar with symlinks; 42.zip → DoS |
| Generic file upload | Unrestricted file upload, content-type bypass | Upload `.php`/`.jsp`/`.aspx`/`.html` with bypass on extension or MIME check → RCE or stored XSS |
| Bulk import (CSV/JSON) | CSV formula injection, JSON parser confusion, deserialization | CSV with `=cmd|'...'` in field, opened in Excel by admin → RCE on admin workstation |
| Config import from URL | SSRF, RCE via deserialization | Point config URL at `169.254.169.254` (cloud metadata) or at attacker server returning crafted YAML |
| Config import from file | Deserialization (YAML/pickle/XML), path traversal in config keys | Upload YAML with `!!python/object/apply:os.system` → RCE if non-safe loader used |

### Parsers

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| XML parsing | XXE, XInclude, billion-laughs DoS, XPath injection | Submit XML with external entity → file read or SSRF; XInclude → file read; recursive entities → DoS |
| XSLT | RCE via extensions, file read | XSLT with `<saxon:script>` or `<msxsl:script>` → code execution |
| Image processing | ImageMagick/Pillow/libvips CVEs, SVG XSS, polyglot files | Submit MVG / SVG / TIFF with known CVE payload (ImageTragick family); SVG with `<script>` rendered in browser |
| Document parsing | PDF JS, Office macros, OLE, embedded objects | Server-side preview generation opens malicious PDF → RCE in PDF renderer; OLE-embedded payload |
| YAML parsing | Deserialization via tags | YAML `!!python/object/new:...` or `!!ruby/object:...` triggers code path on load |
| Markdown rendering | XSS via raw HTML, link injection, JS URI | Markdown allows raw HTML → stored XSS; `[click](javascript:...)` if URL not sanitized |
| Template rendering with user input | SSTI | `{{7*7}}` returning 49 → SSTI; chain to RCE via class introspection (Jinja, Twig, Freemarker, Velocity all have known chains) |
| CSV export | Formula injection in downstream | Field starting with `=` or `+`/`-`/`@` triggers Excel formula on open |
| Email parsing (MIME) | Header injection, attachment parser CVEs, calendar parser issues | Malformed multipart, S/MIME bugs, ICS exploits |

### Web endpoints / auth

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| Outbound webhook (server fetches user URL) | SSRF, blind SSRF, cloud metadata access | Webhook URL = `http://169.254.169.254/latest/meta-data/iam/security-credentials/` → cloud creds; URL = `http://127.0.0.1:6379/` → Redis access |
| Server-side URL preview / unfurl | SSRF, DNS rebinding | Same as above; also DNS rebinding to bypass allowlists |
| Server-side PDF / screenshot generation | SSRF, RCE via headless browser, file:// scheme | URL of `file:///etc/passwd` in rendered PDF if file:// not blocked; chromium RCE via headless |
| OAuth callback / redirect_uri handling | Open redirect, token theft, state misuse | Wildcard or weak redirect_uri match → token interception; missing state → CSRF login |
| SAML AssertionConsumerService | SAML signature wrapping, audience confusion | Crafted SAMLResponse with multiple Assertion elements or comment-in-attribute → authentication bypass |
| JWT-based auth | `alg:none`, key confusion, weak secret | Modify JWT to `alg: none` or `alg: HS256` with public key as HMAC secret; if accepted → auth bypass |
| Password reset | Predictable token, token leakage, missing rate limit, no single-use | Reset token in URL leaked via Referer; brute-forceable short tokens |
| Account recovery flows | MFA bypass, account takeover via lower-priority factor | Recovery via email-only → if attacker controls email forwarding or compromises mailbox, MFA bypass |
| API tokens / personal access tokens | Token in URL / logged, scoped too broadly, no expiration | Token in query string logged in proxies; "read" token has write capability |
| Session cookies | Missing Secure/HttpOnly/SameSite, predictable IDs | Cookie without HttpOnly stolen via XSS; predictable token → session prediction |
| Login with "remember me" | Persistent token without rotation/revocation | Token survives password change; not revoked on logout |
| MFA | Bypass via OAuth / API key / recovery / "trust this device" | Login via OAuth path bypasses MFA enforced on password login |

### Plugins / scripting / templating

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| Plugin system loading native code | Plugin sideload, supply chain, unsafe load path | Plugin dir writeable by lower-priv user → privilege escalation on next service start |
| Plugin marketplace / install from URL | Supply chain, SSRF, unrestricted file write | Marketplace search returns malicious plugin with similar name; install fetches from attacker URL |
| Server-side scripting engine (Groovy, JS, Python) | RCE (if attacker can submit scripts) | Workflow / automation feature lets users write a Groovy snippet → if "sandboxed" Groovy, look for known sandbox escapes (Jenkins-style) |
| Template engine in admin UI | SSTI | Admin email template uses Velocity / Freemarker → if admin compromised or template editable by lower-priv user, RCE |
| Workflow with HTTP step | SSRF | Workflow allows arbitrary HTTP request → covers SSRF angles plus exfil |
| Workflow with code step | RCE | Workflow runs JS / Python; sandbox quality determines exploitability |
| Custom URL scheme handler | Protocol handler abuse, deep link injection | `myapp://load?url=...` → opens content with insufficient validation; on mobile, deep link parameter injection |

### IPC / native (binary / desktop / mobile)

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| Privileged helper service with local socket | Local PE, command injection | Helper accepts JSON commands from any local user; one command spawns a process with user-controlled args |
| Named pipe / D-Bus / XPC service | Local PE, IPC auth bypass | Service trusts any caller; or PID-based auth subject to TOCTOU |
| COM / DCOM | Local PE, remote PE if exposed | Marshalling bugs, type confusion |
| Mach ports / launchd services | Local PE, privilege boundary | Service exposes port; clients can send messages without restriction |
| Auto-update | Unsigned update, downgrade, update URL hijack | Update URL configurable / MITM-able; signature missing or weak |
| Plugin / DLL load from user-writable dir | DLL hijack, plugin sideload | App searches `%PATH%`/working dir before system → user drops `version.dll` → next launch, code runs as app user |
| Insecure file permissions in install | LPE | Config with secrets is world-readable; binaries are user-writable (signed updater overwrites trusted binary) |
| Custom URL scheme | Protocol handler injection, deep link RCE | Browser/email lets attacker invoke `myapp://...` → param triggers file open, page navigation in embedded webview, etc. |
| WebView with JS bridge | Renderer-to-native RCE | Bridge exposes `bridge.fs.write(path, contents)` to any page loaded; attacker iframes or redirects page to attacker origin |
| Electron app | nodeIntegration, contextIsolation off, preload script issues | If renderer can be made to load attacker URL and nodeIntegration is true → full RCE in renderer process |

### Cryptographic

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| Custom encryption scheme | Bespoke crypto flaws, every flavour of broken | Cryptanalyze; usually weak (predictable IVs, ECB mode, no integrity, key derivation issues) |
| ECB mode | Information leak, block-shuffling | Identical plaintext blocks → identical ciphertext blocks; shuffle ciphertext to alter plaintext if no integrity |
| CBC without HMAC | Padding oracle | If oracle exists, decrypt arbitrary ciphertext; classic POODLE-family |
| MD5 / SHA-1 in security contexts | Collision attack | Especially for signatures, version control, software identity |
| Hardcoded keys in doc examples | Key reuse, default-cred attacks | Keys in docs end up in production builds; check vendor binaries for the docs example key |
| `Math.random` / weak PRNG for security tokens | Token prediction | Sequence prediction once a few sample tokens captured |
| Password hashing with fast hash | Offline brute force | MD5/SHA without salt+iterations → cracking with off-the-shelf tools |
| HMAC compare with `==` | Timing leak | Network or local timing oracle to recover HMAC |
| Client-side encryption claims | Often meaningless | "Encrypted client-side" before sending typically means the server gets the plaintext anyway, or the key is on the client |

### Cloud / SaaS specific

| Feature in doc | Vuln class(es) | Typical scenario |
|---|---|---|
| Multi-tenant isolation | Tenant escape, IDOR across tenants | Object ID guessable / sequential → cross-tenant data access; tenant scoping enforced only in UI |
| User-supplied database URL | JDBC URL injection, DB credential exfil | JDBC URL `jdbc:mysql://attacker/x?queryInterceptors=...` → RCE in newer drivers; or point to attacker DB to capture creds |
| Webhook integrations | SSRF, webhook signature bypass | Signature using weak HMAC or `==`; signing only headers not body |
| Stored cloud credentials | Credential exposure via reflection, logging | Creds rendered in admin UI; exposed in audit logs |
| S3 / blob bucket integration | SSRF, bucket takeover, signed URL leakage | Bucket name configurable → request `localhost`-style URLs; signed URL with overly broad permission |

---

## Section 2: Hypothesis writing template

For each feature/smell you decide is worth turning into a hypothesis, write:

```
### Hypothesis #N: <Short title>

**Feature:** <name> (<doc:p.XXX>)

**Vuln class(es):** <CWE-XX / class name>, <secondary class if any>

**Scenario:**
<One paragraph. Concrete. Names the endpoint or feature, names the input, names the effect. Avoid hedging language; if uncertain, write the "Unknowns" section, not weasel words in the scenario.>

**Preconditions:**
- Auth level required: <none / authenticated user / admin>
- Network position: <internet / same network / local user>
- Configuration: <default / non-default, specify>
- Victim interaction: <none / open a link / open a file>

**Evidence in doc:**
- <doc:p.XXX>: <verbatim or paraphrase of what the doc says>
- <doc:p.YYY>: <supporting evidence>

**Unknowns (need source or testing to resolve):**
- <specific unanswered question>
- <specific unanswered question>

**Severity estimate:** <Critical / High / Medium / Low>, <one-line justification>

**Test plan (if a test instance is available):**
1. <concrete step>
2. <concrete step>
3. <expected indicator of vulnerability>

**Related CVEs / prior art:**
- <product X CVE-YYYY-NNNN: similar feature, similar bug class>
```

---

## Section 3: Sanity checks before finalizing

For each hypothesis, ask:

- **Is it falsifiable?** A tester reading it should know what experiment confirms or refutes it. If the answer is "look around the product", rewrite.
- **Is the precondition realistic?** A "RCE via plugin upload" precondition of "compromise the admin account first" is technically true for many features and not very interesting on its own. Useful when chained, less useful as a standalone finding.
- **Is the vuln class specific?** "Some kind of injection" is not a class; "SQL injection in the search endpoint" or "SSTI in the email template renderer" is.
- **Did you over-confidence it?** Calibrate. Use "likely vulnerable" / "worth testing" / "needs context to assess". "Vulnerable" with no test is too strong.
- **Is there a similar CVE you can point at?** If yes, attach it. If no, note the absence, sometimes the feature is genuinely novel and the absence of prior CVEs is itself information (less battle-tested or more carefully built; usually the former for niche products).

---

## Section 4: Cross-feature chains

Most interesting findings come from chaining multiple features. After listing single-feature hypotheses, look for chains:

- **Auth bypass + admin endpoint** → effective unauth RCE on the admin feature.
- **SSRF + cloud metadata** → cloud credentials → full cloud compromise.
- **Stored XSS + admin-only page** → admin session hijack.
- **CSRF + state-changing GET on admin** → admin action from victim's browser.
- **Open redirect + OAuth callback** → token theft.
- **File upload + path traversal** → arbitrary file write → next-stage exec via cron / web shell.
- **Plugin install + writable plugin dir** → LPE via auto-load on service restart.
- **WebView + custom URL scheme** → click on attacker link launches app, loads attacker URL in embedded browser, triggers JS bridge.
- **OAuth subdomain wildcard + subdomain takeover (DNS)** → account takeover.

A chain hypothesis combines two or three individual hypotheses with a "→" and explains the composition. Chains are often higher-priority than any single link.

---

## Output of phase 4

A list of hypotheses, written in the template above. Order doesn't matter yet (phase 5 prioritizes). Aim for the right *granularity*: a 600-page doc with rich attack surface should produce 20-60 hypotheses; a 50-page MD might produce 5-10. Fewer than that means too cautious; more than that means lacking discrimination.

Each hypothesis becomes one entry in the detailed annex (Part 2 of the deliverable) and a candidate for the top-15 in the synthesis (Part 1).
