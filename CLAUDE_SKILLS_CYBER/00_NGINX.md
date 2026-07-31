# Nginx

**TL;DR**: almost never RCE by itself, it's a config-misuse and access-control-bypass surface. Highest-value bug is `alias` off-by-slash (missing trailing slash on a `location` block escapes the intended directory). Second highest: anything routed through `proxy_pass` where a URI normalization mismatch between Nginx and the backend creates a smuggling or ACL-bypass gap. If the target is Kubernetes, check Ingress-NGINX separately (IngressNightmare), it's a different codebase and CVE surface from vanilla Nginx.

## 1. Fingerprinting / recon

* `Server:` header (often shows exact version unless `server_tokens off;` is set).
* Default error pages (404/50x) can leak the version if `server_tokens` isn't disabled.
* Behavior fingerprinting: how Nginx handles trailing slashes, double slashes, and case sensitivity differs from Apache/IIS/backend app servers, useful to confirm what's actually terminating the connection vs what's behind it.

## 2. Alias misconfiguration (off-by-slash / off-by-one-slash)

The single most common and most exploitable Nginx misconfiguration. When a `location` block without a trailing slash is combined with an `alias` directive, path traversal becomes possible.

```nginx
location /static {
    alias /var/www/static/;
}
```

```
GET /static../settings/config.php
```

Nginx concatenates the location match with the rest of the path literally, so this resolves to `/var/www/static/../settings/config.php` → `/var/www/settings/config.php`, outside the intended directory. This also applies to other directives that take a URI, not just `alias` (notably `proxy_pass`).

```
GET /static../                 # → 403 typically, still confirms the pattern
GET /static.../                # → 404 (dir doesn't exist), also confirms
GET /static../../              # → 403
GET /static../../../../../../../../../../../   # → 400 eventually (path too deep)
```

If `autoindex on;` is also set on the aliased/misconfigured location, directory listing amplifies the impact (browse the escaped directory directly instead of guessing filenames).

**Fix reference (for context, not a test step)**: adding the trailing slash to the `location` block (`location /static/`) closes this.

## 3. merge_slashes

`merge_slashes` is `on` by default, which collapses `//`, `///`, etc. into a single `/`. This can mask vulnerabilities in a backend behind Nginx, particularly LFI-prone apps, because Nginx normalizes multi-slash sequences before the backend ever sees them. If a target has `merge_slashes off;` (33 instances found in a public 2020 Detectify scan of exposed configs), multi-slash payloads reach the backend unmodified, worth testing `//../../etc/passwd`-style payloads against any LFI-suspect endpoint proxied through Nginx.

## 4. Unsafe variable use / request splitting

* `$uri` and `$document_uri` contain the **normalized** URI (normalization includes URL-decoding). If a config uses `$uri` (instead of `$request_uri`) inside a `return` or `rewrite` for a redirect, CRLF injection becomes possible: URL-encoded `%0d%0a` gets decoded by the time it reaches `$uri`, letting an attacker inject headers/response splitting.

  ```nginx
  # vulnerable pattern
  location / {
      return 302 https://example.com$uri;
  }
  ```

  ```
  GET /%0d%0aSet-Cookie:%20pwned=1
  ```

* Printing back arbitrary Nginx variables (e.g. `$http_referer`, `$http_user_agent`, custom `$variables` built from headers) directly into responses or logs without escaping can lead to XSS or log injection. Test by setting a distinctive `Referer` or custom header and checking if it's reflected raw.

* `$host` vs `Host` header handling: some configs trust `$http_host` unconditionally for building absolute URLs/redirects, enabling host header injection downstream even when Nginx itself is not vulnerable.

## 5. proxy_pass URI handling

A classic and subtle bug class: whether `proxy_pass` has a URI component after the address changes routing behavior significantly.

```nginx
# location has a URI component (trailing slash) AND proxy_pass has one:
# the location prefix is stripped before forwarding
location /api/ {
    proxy_pass http://backend/v1/;
}
# GET /api/users -> backend receives /v1/users
```

```nginx
# proxy_pass has NO URI component (no trailing path):
# the full original URI is forwarded as-is, location prefix included
location /api/ {
    proxy_pass http://backend;
}
# GET /api/../admin -> depending on merge_slashes/normalization, can smuggle
# a path past the location matching logic straight to backend routing
```

Mismatches here are a frequent source of access-control bypass when `/api/` is meant to be the only exposed surface but path traversal in the request line reaches endpoints the location block never intended to expose.

## 6. Raw backend response reading (error interception bypass)

Nginx's `proxy_pass` normally intercepts backend errors and headers to hide internal details (via `proxy_intercept_errors`, custom error pages). However, if Nginx receives an **invalid** HTTP response from the backend, it forwards that raw, unprocessed response directly to the client, bypassing all of Nginx's own header/error handling. This can leak backend internals, stack traces, or headers Nginx was specifically configured to strip.

## 7. Default value in map directive

The `map` directive's default value (when no match occurs) is easy to misconfigure into an unsafe fallback, e.g. defaulting authentication/authorization decisions to "allow" when a header doesn't match any pattern, rather than "deny". Worth reviewing any `map $http_x_custom_header $allowed { ... }`-style ACL logic for a permissive default.

## 8. proxy_set_header Upgrade & Connection (WebSocket smuggling)

Misconfigured WebSocket proxying is a known source of request smuggling / auth bypass:

```nginx
location /ws/ {
    proxy_pass http://backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";   # hardcoded, not conditional
}
```

Hardcoding `Connection: upgrade` even for non-upgrade requests, or failing to clear it when `$http_upgrade` is empty, can let a normal HTTP request be treated as a protocol upgrade downstream, or facilitate request smuggling between Nginx and the backend when both sides disagree on where one request ends and the next begins.

## 9. DNS rebinding / resolver abuse

If Nginx resolves upstream hostnames dynamically (`resolver` directive + variables in `proxy_pass`), and the upstream hostname is attacker-influenced or externally resolvable, DNS rebinding can redirect proxied traffic to attacker infrastructure after the initial validation. Relevant in SSRF-adjacent scenarios where Nginx is acting as a forwarding proxy based on a variable target.

## 10. internal directive / X-Accel-Redirect

`internal;` marks a location as unreachable directly by clients, only reachable via internal redirect (`X-Accel-Redirect` header from a backend, or `error_page`, or `try_files`). Misconfigurations to check:

* A location meant to be internal-only but missing the `internal;` directive, making it directly reachable.
* An application that reflects user input into the `X-Accel-Redirect` response header without validation, letting an attacker request arbitrary internal-only files (SSRF-like internal file read) via the backend app rather than Nginx directly.

## 11. Client-body / request smuggling considerations

Nginx used to have a historically more permissive stance on Content-Length/Transfer-Encoding combinations in some configurations. When Nginx sits in front of another server (another Nginx, a Java/Python backend, a legacy proxy), always test CL.TE / TE.CL desync patterns; the discrepancy in header parsing between the two hops is what actually causes smuggling, so Nginx itself being spec-compliant doesn't guarantee the whole chain is.

**h2c smuggling**: if Nginx forwards the `Upgrade` and `Connection` headers to an h2c-compatible backend (a common misconfiguration in `proxy_pass` setups, particularly with WebSocket-style configs like section 8), an attacker can establish a cleartext HTTP/2 tunnel through Nginx straight to the backend, bypassing whatever path-based routing, auth checks, or WAF rules Nginx enforces per-request. Tool: `h2csmuggler`.

## 12. TLS / SNI and virtual host confusion

* Default server block confusion: sending an unexpected/absent `Host:` header, or connecting without SNI, can fall back to the `default_server` vhost, potentially bypassing per-vhost access controls or reaching an unintended backend.
* Host header vs SNI mismatch: some configs route based on SNI for TLS termination but then trust the HTTP `Host:` header for backend routing, allowing a mismatch to reach a different vhost's backend than the certificate suggests (domain fronting-style behavior).
* **CVE-2025-23419**: insufficient checking in virtual server handling with TLSv1.3 session resumption allowed an SSL session negotiated on one virtual server to be reused on a different one, bypassing client certificate verification on the second server. Directly relevant if the target uses per-vhost client-cert auth with TLS session resumption enabled.

## 13. autoindex / static file exposure

`autoindex on;` on any location, intentional or leftover from debugging, exposes full directory listings. Combine with alias misconfigurations (section 2) to escape into directories never meant to be listed.

## 14. FastCGI / PHP-FPM misconfiguration

```nginx
location ~ \.php$ {
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    fastcgi_pass 127.0.0.1:9000;
}
```

The regex `\.php$` matches any URI ending in `.php` regardless of whether the file exists on disk. Nginx will pass any such request to the PHP interpreter via `SCRIPT_FILENAME` built from `$fastcgi_script_name`, which if not carefully bounded can be manipulated with `PATH_INFO`-style tricks (`/upload/image.jpg/x.php`) to have PHP-FPM execute an uploaded non-PHP file as PHP (classic PHP path-info RCE against uploaded images/avatars).

Related: if the PHP-FPM/FastCGI socket is directly reachable (misrouted `fastcgi_pass`, exposed Unix socket in a container context), the FastCGI protocol itself can be spoken directly, bypassing Nginx entirely. See the FastCGI-specific notes for the protocol-level attack.

## 15. Ingress-NGINX (Kubernetes): a separate attack surface

The Kubernetes Ingress NGINX Controller is a distinct codebase/deployment model from vanilla Nginx and has had its own severe CVE class in 2025 known as **IngressNightmare**:

* **CVE-2025-1974** (critical, CVSS 9.8): unauthenticated RCE in the admission controller component. The admission webhook validates incoming Ingress objects by rendering them into an NGINX config and running `nginx -t` against it; because the webhook is by default network-reachable without auth and the controller pod has broad privileges/secrets access, this alone gives unauthenticated RCE and can lead to full cluster takeover.
* **CVE-2025-1097**: the `auth-tls-match-cn` annotation is insufficiently sanitized, allowing NGINX config injection.
* **CVE-2025-1098**: the `mirror-target` / `mirror-host` annotations allow NGINX config injection.
* **CVE-2025-24514**: the `auth-url` annotation allows NGINX config injection.
* **CVE-2025-24513**: directory traversal inside the controller container, DoS or limited secrets disclosure when chained with the above.
* **CVE-2025-15566** (disclosed Feb 2026, CVSS 8.8): the `auth-proxy-set-headers` annotation allows arbitrary NGINX directive injection, leading to RCE and Kubernetes Secrets disclosure.

Any of the config-injection CVEs (1097, 1098, 24514) can be chained with the admission-controller RCE (1974) to go from "can create/update an Ingress object" to full unauthenticated RCE on the controller pod. Recon: check `kubectl get ingress --all-namespaces -o yaml | grep -A5 annotations` for risky annotations (`configuration-snippet`, `auth-url`, `auth-tls-match-cn`, `mirror-target`), and check whether the admission webhook (typically port 8443 on the controller pod) is reachable from within the pod network without additional auth.

## 16. Misc / less common

* **Range header abuse**: overlapping/duplicated Range requests against large static files can cause resource exhaustion (DoS), similar in spirit to the Apache "Range header" DoS class.
* **Malicious response headers**: if user input reaches a header set via `add_header` or `proxy_set_header` without sanitization, CRLF injection / header injection is possible (related to section 4).
* **gixy**: static analysis tool specifically built to catch these Nginx config classes automatically. Run it against any config you can read (via LFI, git history, backup files, or direct access).

---

## CVEs to check

* **CVE-2025-23419**: SSL session reuse across virtual servers bypasses client certificate verification when TLSv1.3 session resumption is enabled (see section 12). Fixed in 1.27.4+/1.26.3+.
* **CVE-2021-23017**: 1-byte memory overwrite in the resolver, exploitable if `resolver` is configured with an attacker-influenceable upstream DNS response. Fixed in 1.21.0+/1.20.1+.
* **CVE-2024-7347**: buffer overread in `ngx_http_mp4_module` via a crafted mp4 file, worker crash (DoS). Only relevant if the mp4 module is compiled in and the `mp4` directive is used.
* **CVE-2024-24989**: NULL pointer dereference in HTTP/3, crafted QUIC session crashes the worker process. Requires the experimental HTTP/3 QUIC module enabled. Fixed in 1.25.4+.
* **CVE-2024-24990**: use-after-free in HTTP/3, undisclosed requests can terminate worker processes. Requires the HTTP/3 QUIC module enabled. Fixed in 1.25.4+.
* **CVE-2024-31079**: stack overflow and use-after-free in HTTP/3, triggered by connection-draining timing. Requires the HTTP/3 QUIC module enabled. Fixed in 1.27.0+/1.26.1+.
* **CVE-2024-32760**: buffer overwrite in HTTP/3. Requires the HTTP/3 QUIC module enabled. Fixed in 1.27.0+/1.26.1+.
* **CVE-2024-34161**: memory disclosure in HTTP/3, leaks previously-freed worker memory when the network MTU is 4096+ without fragmentation. Requires the HTTP/3 QUIC module enabled. Fixed in 1.27.0+/1.26.1+.
* **CVE-2024-35200**: NULL pointer dereference in HTTP/3. Requires the HTTP/3 QUIC module enabled. Fixed in 1.27.0+/1.26.1+.
* **CVE-2026-42945**: buffer overflow in `ngx_http_rewrite_module`. Fixed in 1.31.0+/1.30.1+, check this one specifically since it's recent and post-dates most deployed versions.
* **CVE-2019-9511** / **CVE-2019-9513**: excessive CPU usage via HTTP/2 small window updates / priority changes (DoS class, low severity but cheap to test on any HTTP/2-enabled target).

Also check the [official nginx security advisories page](https://nginx.org/en/security_advisories.html) directly, it's the authoritative version-indexed source and gets updated ahead of most third-party CVE trackers.

---

## Caido
- Off-by-slash and merge_slashes probing is pure Replay work: take any static-asset-looking path, append `../` variants with and without an extra trailing segment, diff status/length against the clean request.
- Use Match & Replace to strip/inject double slashes across a whole session when testing whether `merge_slashes` is on or off for a given host, faster than testing endpoint by endpoint.
- For `proxy_pass` URI-handling mismatches, compare the same logical request sent with and without a trailing path segment past the `location` prefix, the divergence in backend routing is the signal.
- CRLF-via-`$uri` and header-reflection checks are single-request Replay tests, put the payload in `Referer`/custom headers and read the raw response headers back.

## References

* [HackTricks - Nginx](https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/nginx): alias misconfig, merge_slashes, unsafe variables, proxy_pass/internal directive abuse, DNS rebinding, map directive defaults.
* [Detectify: Common Nginx misconfigurations](https://blog.detectify.com/industry-insights/common-nginx-misconfigurations-that-leave-your-web-server-ope-to-attack/): origin research on off-by-slash and merge_slashes, includes a Dockerized vulnerable test lab on GitHub.
* [Orange Tsai: "Breaking Parser Logic!" (Black Hat)](https://blog.orange.tw): the talk that made off-by-slash / parser-differential attacks widely known, also covers Apache/IIS parser confusion.
* [gixy](https://github.com/yandex/gixy): static analysis tool for Nginx configuration files.
* [ProjectDiscovery: IngressNightmare writeup + Nuclei templates](https://projectdiscovery.io/blog/ingressnightmare-unauth-rce-in-ingress-nginx): detection templates for CVE-2025-1974 and related.
* [h2csmuggler](https://github.com/BishopFox/h2csmuggler): h2c smuggling tool for bypassing proxy_pass routing/auth rules (section 11).
