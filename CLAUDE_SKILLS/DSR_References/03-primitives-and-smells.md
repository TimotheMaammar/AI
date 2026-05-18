# Phase 3: Dangerous primitives and security smells

The highest-signal phase. Two passes, both important.

---

## Part A: Dangerous primitives

A "dangerous primitive" is a feature whose existence historically maps to a class of bugs. When you see it in the doc, the question is not *whether* it's exploitable but *how* the vendor implemented it.

### Code execution surfaces

These features execute or evaluate code. Every one of them deserves a deep look.

- **Template rendering with user input.** Jinja2, Twig, Handlebars, Freemarker, Velocity, ERB, Razor, Pug, Liquid, EJS, Smarty, Mako, Mustache (with helpers), DOM-based templating. If user input reaches the template *as the template itself* (not just as a value), it's SSTI. Even if the doc claims "sandboxing", history shows sandboxes leak.
- **Dynamic code loading.** `eval()`, `exec()`, `Function()`, `setTimeout(string)`, dlopen/LoadLibrary called on user-controlled paths, Java reflection from user input, .NET `Activator.CreateInstance`, Python `__import__`.
- **Deserialization.** Java `ObjectInputStream`, .NET `BinaryFormatter` / `NetDataContractSerializer`, Python `pickle` / `shelve` / `marshal`, Ruby `Marshal`, PHP `unserialize`, Node.js `node-serialize`, YAML with non-safe loaders (PyYAML default `load`), XML with custom resolvers.
- **Command execution.** `system()`, `exec`, `popen`, `subprocess.Popen(shell=True)`, `Runtime.exec`, `ProcessBuilder`, shell-out helpers. Especially: where input flows in and how it's quoted/escaped.
- **Embedded scripting engines.** V8/QuickJS for JS, CPython embedded, LuaJIT, Groovy shell, Nashorn (old Java JS), Rhino, JRuby. Sandbox claims should be verified against known escapes.
- **Database query construction.** Especially if the doc shows raw query construction in examples ("just concatenate the WHERE clause"), even if the product itself uses parameterization elsewhere, the example code reaches users.
- **Compilation features.** JIT compilers, dynamic SQL, on-the-fly LaTeX rendering, on-the-fly markdown-to-PDF, server-side image processing that uses ImageMagick or ffmpeg (vast attack surface).

### Parser and format surfaces

- **XML parsing.** Default settings often enable XXE (External Entity), XInclude, billion-laughs DoS. Look for: doctype handling, entity expansion limits, network access from XML processor.
- **XSLT.** XSLT can execute code via extensions in many implementations.
- **Archive extraction.** ZIP Slip (path traversal via `../` entries), tar/tar.gz symlink overwrites, decompression bombs (small file → massive output).
- **Image processing.** ImageMagick (CVE-rich history), libvips, Pillow, native codecs. SVG → SVG with embedded JS/foreignObject.
- **Document parsing.** Office formats (macros, OLE, embedded objects), PDF (JavaScript in PDFs, embedded files, form actions).
- **YAML.** Tag-based instantiation (`!!python/object`, `!!ruby/object`). Default loaders are often unsafe.
- **JSON.** Mostly safe but watch for: BigDecimal/Integer parsing differences, prototype pollution (JavaScript), `__proto__` keys.
- **CSV.** Formula injection (`=CMD()`, `=HYPERLINK()`) when downloaded and opened in Excel.
- **Email parsing.** MIME, attachments, HTML rendering, calendar attachments (ICS exploits).
- **Custom protocols.** Any binary parser is a fuzzing target.

### Web-specific dangerous primitives

- **SSRF surfaces.** Server fetches a URL the user provided (webhooks, image previews, link unfurling, RSS, PDF generation, screenshot generation, OAuth issuer discovery, proxy features).
- **Open redirects.** `?next=`, `?return_to=`, `?redirect_uri=` accepting arbitrary URLs.
- **CORS.** `Access-Control-Allow-Origin: *` with credentials, reflected origins, subdomain wildcards.
- **JWT.** `alg: none`, weak secrets, key confusion (RS256↔HS256), missing audience/issuer checks, kid header injection.
- **OAuth / OIDC misconfig.** Open redirector in `redirect_uri`, `state` not validated, implicit flow used, PKCE missing for public clients.
- **CSRF.** State-changing GET requests, missing CSRF tokens on POST, SameSite cookie issues.
- **Cross-origin postMessage.** Especially if origin not validated.
- **WebSocket.** Origin checked? Auth on connect or per-message? Subprotocol injection?
- **CORS preflight bypass.** Simple request methods bypass preflight; sometimes overlooked.
- **HTTP smuggling surface.** Multiple proxies, custom HTTP parsers, header normalization differences.
- **Cache poisoning.** Unkeyed input that influences response (headers reflected into body, error pages cached).
- **HTTP request signing flaws.** Custom signature schemes that miss headers / bodies.

### Auth-specific dangerous primitives

- **Account enumeration.** Different error messages for "user not found" vs "wrong password".
- **Password reset.** Token strength, leakage in URL/referer, single-use enforcement, no auth on reset endpoint.
- **MFA bypass surfaces.** Recovery codes flow, "remember device" cookies, OAuth login bypassing MFA, API key auth bypassing MFA.
- **SSO confused deputy.** SAML signature wrapping, audience confusion, IdP-initiated bypass, OIDC issuer confusion.
- **Session management.** Tokens in URL, predictable IDs, missing rotation on privilege change, infinite-lifetime tokens.
- **Logout that doesn't invalidate server-side.**
- **"Remember me" features.** Persistent cookies, especially if signed-only (no server-side revocation).

### Binary / desktop / mobile dangerous primitives

- **Plugin systems that load native code.** Trust model, signature checking, load path.
- **Setuid / setgid binaries.** Documented in the install procedure? What helpers run as root?
- **IPC without auth.** Local services that trust any local connection.
- **Custom URL schemes / file associations.** Open `myapp://malicious-payload` triggers what?
- **WebView with JS-to-native bridge.** What is exposed via `window.bridge.X`? Origin validated?
- **Electron with nodeIntegration enabled in renderer.** Game over.
- **Auto-update without signature.** Or with weak signature (MD5, downgrade-attackable channels).
- **Insecure default file permissions.** World-writable plugin dir, world-readable config with secrets.
- **TOCTOU patterns.** "Check file then use file" with attacker-writeable paths.
- **Insecure use of temp files.** Predictable names, race-prone creation.
- **DLL search order hijacking.** Vendor docs say "install to C:\Program Files\X" but installer doesn't lock down the path.
- **Permissions on Android/iOS.** Accessibility service, Device Admin, MDM, Content Provider exports.

### Cryptographic dangerous primitives

- **Custom crypto.** "We use AES with our own scheme" is virtually always a finding.
- **ECB mode.** Mentioned by name in any doc.
- **CBC without HMAC.** Padding oracle territory.
- **MD5 / SHA-1.** For anything security-relevant.
- **Hard-coded keys.** Even "example" keys in docs that may end up in production.
- **Predictable randomness.** `Math.random`, `rand()`, current-time-as-seed.
- **Key derivation.** No KDF, single-iteration hash, fast hash for passwords.
- **HMAC verification with `==`.** Timing leak.
- **Crypto in JavaScript on the client side.** "Encrypted client-side before sending" is almost always meaningless.

---

## Part B: Security smells (the goldmine)

These are phrases or admissions in the doc itself that signal trouble. Quote them verbatim with page reference.

### Privilege / context smells

- "runs as root" / "runs as Administrator" / "requires elevated privileges"
- "needs full disk access" / "needs accessibility permissions"
- "the service account must have write access to..."
- "for simplicity, the daemon runs in the same security context as the user"
- "automatically registers as a system service"

### "For development only" / "internal" smells

- "this feature is intended for development environments only"
- "debug mode" / "developer mode" / "diagnostic mode"
- "do not enable in production"
- "internal use only" / "for internal tooling"
- "experimental feature" / "preview feature"
- "use at your own risk"
- "not recommended for public-facing deployments"

These are admissions that the vendor knows the feature is weakly secured. They are the auditor's first target.

### "Legacy / compatibility" smells

- "legacy support" / "backwards compatibility with v1"
- "supported for migration from..."
- "deprecated but retained for compatibility"
- "older clients can still use..."

Old features carry old security assumptions and rarely get rewritten with modern hardening.

### Crypto / auth smells

- "custom encryption" / "proprietary encryption" / "our own protocol"
- "homegrown" anything
- "obfuscated" (not encrypted, just hidden)
- "encrypts client-side"
- "the password is hashed using..." (then look, is it bcrypt/Argon2, or MD5/SHA-1?)
- "transmits a fingerprint of..."
- "supports anonymous access" / "anonymous read"
- "authentication is optional" / "auth can be disabled"
- "default password is..." / "default credentials are..."
- "self-signed certificate" recommended
- "disable TLS verification for..."

### Code-execution smells

- "executes user-supplied scripts"
- "supports plugins" / "supports extensions"
- "embedded interpreter" / "scripting engine"
- "evaluates expressions"
- "runs system commands"
- "shells out to..." / "wraps the X command-line tool"
- "imports configuration from URL"
- "fetches data from a remote source"
- "renders Markdown / HTML / templates"
- "supports macros" / "supports formulas"
- "compiles to bytecode at runtime"

### Trust-the-client smells

- "the client validates..."
- "client-side check"
- "client must include..."
- "we trust the user-supplied..."
- "no server-side enforcement is needed because..."

### Sandbox smells

- "sandboxed", claims of sandboxing are red flags. Look at how it's implemented.
- "isolated environment"
- "restricted runtime"
- "limited API surface"
- "permissions model", what defines a permission?

### Specific high-risk feature mentions

Any time the doc just *names* one of these things, mark it for follow-up:
- "Electron" / "CEF" / "WebView" / "embedded Chromium"
- "Jinja2" / "Velocity" / "Freemarker" / "Twig" (server-side templates)
- "Groovy" / "Nashorn" / "Rhino"
- "ImageMagick" / "GraphicsMagick" / "ffmpeg" / "ghostscript"
- "ZipFile" / "TarFile" / "archive extraction"
- "pickle" / "marshal" / "BinaryFormatter" / "ObjectInputStream"
- "SAML" / "SAMLResponse"
- "OAuth" / "redirect_uri"
- "iframe" / "postMessage"
- "ActiveX" / "BHO" (very old, very dangerous if present)
- "MSHTML" / "WebBrowser control"
- ".NET Remoting" / "WCF" / "BinaryFormatter"
- "Apache Struts" / "Log4j" / "Spring" (history of RCE families)
- "XML-RPC" / "SOAP"
- "shell_exec" / "passthru" / "system" in any example
- "Reflection.Emit" / "Assembly.Load"

### Absence smells (what is NOT said)

The doc not mentioning something can be a finding:

- Documents an upload feature but does not say what format validation is done.
- Documents a webhook feature but does not mention SSRF protection / allowlist.
- Documents OAuth but does not mention `state` parameter validation.
- Documents an admin endpoint but does not mention authentication required.
- Documents a plugin system but does not mention signature verification.
- Documents an update mechanism but does not mention signature verification.
- Says the feature uses "TLS" but does not say whether certificate validation is enforced.
- Mentions "X is encrypted" but does not say what key, what algorithm, what mode.

For each, note explicitly: "Doc does not state whether [thing]. Worth testing."

---

## Output of phase 3

For each found primitive / smell, an entry:

```
[PRIMITIVE | SMELL | ABSENCE] | Page ref | Verbatim quote (if smell) or feature name (if primitive) | One-line interpretation
```

Examples:

```
[SMELL] | p.412 | "For convenience, the worker service runs as root and listens on the local Unix socket /var/run/teamcollab-worker.sock without authentication."
   → Local privilege escalation: any local user can submit jobs to a root-running service via the socket.

[PRIMITIVE] | p.234 | Plugin upload as ZIP, extracted server-side to /opt/app/plugins/<name>/
   → Zip Slip risk; if name contains "../" entries, write outside extraction dir as root.

[PRIMITIVE] | p.89 | CEF renderer with preload script exposing `window.app.fs.read(path)` to page JS
   → If any page can load attacker-controlled HTML/URL (consider chat embeds, dashboard widgets, OAuth iframes), browser→native RCE.

[ABSENCE] | pp.156-160 | Webhook chapter documents URL configuration; no mention of SSRF protection, allowlist, or blocked CIDRs.
   → Likely SSRF. Test webhook URL = 169.254.169.254/, 127.0.0.1:<various ports>, file:// schemes.

[SMELL] | p.78 | "Tokens are signed using HMAC-SHA256 with a server-side secret. For backwards compatibility, tokens signed with the legacy key (until v3.2) are also accepted."
   → Multiple-key acceptance is a key-confusion candidate. Verify both keys are still considered valid; check whether legacy key is shorter / easier to brute-force.
```

This list feeds directly into phase 4.
