# External references and notable CVEs by product family

Load this when you hit a primitive, feature, or product family you want to ground in real-world cases. The point is not to teach vuln classes (covered in `04-vuln-hypotheses.md`) but to:

1. Point at maintained external resources for the deep stuff.
2. Provide notable real-world CVEs per product family to reason by analogy.

When unsure about a class of vuln in a specific product, two reflexes work better than recalling from memory:

- **web_search** the exact feature + "CVE" / "exploit" / "writeup". Real-world prior art is more reliable than my generic priors.
- **Reason by analogy** from a similar product (see the CVE table below).

---

## A. External resources (pointers, not content)

### Web / general

- **HackTricks**: encyclopedic, well-organized per-protocol and per-attack-class. `https://book.hacktricks.wiki/`
- **PayloadsAllTheThings**: payloads + methodology per bug class. `https://github.com/swisskyrepo/PayloadsAllTheThings`
- **OWASP Web Security Testing Guide (WSTG)**: methodology, the most rigorous web checklist. `https://owasp.org/www-project-web-security-testing-guide/`
- **OWASP Cheat Sheet Series**: defense-side, but useful inversely to know what's commonly *not* done. `https://cheatsheetseries.owasp.org/`
- **Portswigger Web Security Academy**: free labs + writeups per vuln class. `https://portswigger.net/web-security`
- **MITRE CWE**: taxonomy of weakness classes. `https://cwe.mitre.org/`

### Bug bounty prior art

- **HackerOne Hacktivity**: public disclosed reports, searchable by product. `https://hackerone.com/hacktivity`
- **Bugcrowd disclosure**: `https://www.bugcrowd.com/crowdstream/`
- **Pentester Land bug bounty writeups**: curated index. `https://pentester.land/list-of-bug-bounty-writeups.html`
- **GitHub Advisory Database**: supply chain CVEs with package details. `https://github.com/advisories`
- **CVE search / NVD**: `https://nvd.nist.gov/`
- **Exploit-DB**: `https://www.exploit-db.com/`

### Specialized

- **OWASP ASVS**: application security requirements (useful inverse list of what's likely missing). `https://owasp.org/www-project-application-security-verification-standard/`
- **OWASP MASVS / MASTG**: mobile equivalent. `https://mas.owasp.org/`
- **OAuth 2.0 Security BCP (RFC 9700)**: authoritative OAuth attack list. `https://www.rfc-editor.org/rfc/rfc9700.html`
- **JWT.io** + **`jwt-hacker`** writeups for JWT specifics.
- **Cryptopals**: practical crypto attacks. `https://cryptopals.com/`
- **OWASP Top 10 LLM**: when the doc covers AI features.
- **CWE Top 25**: current most-impactful weaknesses, useful for ranking.

### Specific dependency families (CVE-rich histories worth checking against version mentions)

- **ImageMagick**: long history of file-format parsing CVEs. If doc mentions it, check version.
- **ffmpeg / libav**: same.
- **ghostscript**: many CVEs, often reached via PDF processing chains.
- **OpenSSL**: version mentions worth checking.
- **Apache Struts**: major RCE history (Equifax-class).
- **Log4j / Log4shell**: check any Java product.
- **Spring (Framework / Cloud)**: Spring4Shell + many.
- **Jackson**: deserialization gadgets.
- **Fastjson**: same, more historically.
- **Apache Commons Collections / Text**: gadget chains, Text4Shell.
- **PyYAML**: default `load` unsafe (deprecated, but legacy code still uses it).
- **Pillow**: image parser CVEs.
- **node-serialize**: RCE-by-default.
- **lodash**: prototype pollution.

---

## B. Notable CVEs by product family

Reason-by-analogy table. When the doc describes product X and you've identified it's "kind of like product Y", the CVE history of Y is a strong prior on what to look for in X. Specific CVEs are anchors, not an exhaustive list, web_search for current state when it matters.

### Wiki / collaboration / docs

- **Confluence**: CVE-2022-26134 (OGNL injection in Velocity → unauth RCE), CVE-2023-22515 (broken auth → admin), CVE-2023-22518 (unauth admin), CVE-2024-21683 (auth RCE via macro).
- **Pattern**: macros, expression languages (OGNL, Velocity), legacy endpoints, admin without auth re-check.
- **MediaWiki**: template-language XSS, XXE in import flows.
- **Notion / similar SaaS**: IDOR on workspace objects, OAuth misconfigs.

### Issue trackers / dev platforms

- **GitLab**: CVE-2023-7028 (account takeover via password reset to attacker email), CVE-2021-22205 (ExifTool RCE via upload).
- **Jira**: CVE-2019-11581 (SSTI in contact form), CVE-2022-26138 (hardcoded Questions plugin creds).
- **Jenkins**: CVE-2024-23897 (arbitrary file read via CLI arg parser), Groovy sandbox escapes (countless), CVE-2018-1000861 (Stapler routing → RCE).
- **Pattern**: scripting consoles, plugin sandboxes (almost always leak), CLI/arg-parsing surface, OAuth re-binding.

### File sync / collaboration

- **ownCloud / Nextcloud**: CVE-2023-49103 (graphapi env leak unauth), path traversal on shared links, share URL token leakage.
- **Sharepoint**: CVE-2023-29357 (auth bypass), CVE-2019-0604 (deserialization).
- **Pattern**: path traversal in download/preview endpoints, SSRF in link unfurl, sharing-token URL leaks.

### CI/CD

- **TeamCity**: CVE-2023-42793 (auth bypass on REST API → RCE).
- **Bamboo**: auth bypass in legacy endpoints.
- **GitHub Actions**: script injection via PR title/body, self-hosted runner LPE, OIDC misconfig.
- **Pattern**: misissued tokens, runner trust model, agent registration, plugin auth.

### Communication / mail / chat

- **Zimbra**: CVE-2022-27924 (memcached injection → cred theft), CVE-2022-41352 (cpio extraction → RCE), CVE-2023-37580 (XSS).
- **Roundcube**: XSS in mail rendering family.
- **Mattermost / Rocket.Chat**: webhook SSRF, plugin sandbox, OAuth misconfig.
- **Pattern**: mail parsers (MIME, S/MIME, calendar), archive extraction on attachments, HTML rendering, plugin systems.

### Identity / SSO

- **Keycloak**: open redirect via `redirect_uri`, SAML signature wrapping (multiple).
- **Okta**: SCIM endpoint exposure, cross-tenant auth issues.
- **Pattern**: redirect_uri validation, SAML signature handling, session/token confusion across realms.

### VPN / network appliances

- **Pulse Secure**: CVE-2019-11510 (unauth file read → keys), CVE-2021-22893 (RCE chain).
- **Fortinet (FortiOS, FortiGate)**: CVE-2022-42475 (heap overflow unauth RCE), CVE-2018-13379 (path traversal unauth).
- **Citrix (NetScaler / ADC / Gateway)**: CVE-2019-19781 ("Shitrix" path traversal RCE), CVE-2023-3519 (RCE in Gateway).
- **Ivanti**: CVE-2023-46805 + CVE-2024-21887 (auth bypass + command injection).
- **Pattern**: web admin paths reachable without auth, template/command injection in admin features, weak session handling on management plane.

### Antivirus / EDR

- **Sophos**: XG firewall family RCEs.
- **Symantec / Trend**: kernel driver IOCTL vulns, file parser bugs.
- **Pattern**: kernel drivers (IOCTL surface), self-protection bypasses, scanner parser bugs (every file format the AV scans), update-channel hijack, IPC between UI and kernel component.

### Backup / archive

- **Veeam**: CVE-2024-29849 (auth bypass), CVE-2023-27532 (info leak).
- **Acronis**: kernel driver + service surface.
- **Pattern**: archive extraction (Zip Slip in restore), backup repo protocol surface, helper service running as SYSTEM.

### Network monitoring / management

- **Nagios / Zabbix / PRTG**: script execution features, SQLi, command injection in monitoring scripts.
- **SolarWinds**: auth bypass, supply chain.
- **Pattern**: features that run commands "for monitoring", script-template injection, weak service-to-service auth.

### Desktop apps (Electron-heavy)

- **Discord**: protocol handler abuse, custom CSS / webview RCE families.
- **Slack**: XSS leading to RCE via Electron, postMessage handlers.
- **VSCode**: extension permission model, terminal hyperlinks, MarkDown rendering bugs.
- **Signal / Telegram**: IPC bugs, link previews (server-side or client-side).
- **Pattern**: nodeIntegration, custom URL schemes (`slack://`, `discord://`), preload script exposure, link unfurl SSRF, auto-update channel.

### Password managers

- **LastPass / 1Password / Bitwarden**: autofill scope bugs, browser extension origin checks, master password handling in memory, native messaging host.
- **Pattern**: autofill on phishing-mimicking iframes, deep-link / URL scheme to expose vault, clipboard handling.

### Browser extensions

- **uBlock-style adblockers**: declarative net request scope, host permission overreach.
- **Pattern**: content script injection, message passing without origin checks, host permission scope.

### Mobile (commonly-found patterns)

- **Banking apps**: root/jailbreak detection bypass (always), cert pinning bypass, deep-link injection, WebView JS bridge exposing transaction APIs.
- **Messaging apps**: share extension data leakage, MediaStore exfil, exported content provider.
- **IoT companion apps**: hardcoded API endpoints, weak local network protocols (BLE / mDNS).
- **Pattern**: exported components, deep links, WebView bridges, certificate pinning bypass, local storage of secrets.

### Productivity / office

- **MS Office**: macros, OLE, MSDT (Follina CVE-2022-30190).
- **LibreOffice**: macro engine, document parser CVEs.
- **PDF readers (Acrobat, Foxit)**: JS in PDFs, font parsers, form actions.
- **Pattern**: parser surface (file formats), embedded interpreters (VBA, JS), update channels.

### Print / scan / firmware

- **Print servers (CUPS)**: CVE-2024-47076 / 47175 / 47176 / 47177 (cups-browsed + ipp).
- **Printer firmware**: PJL/PCL injection, web admin without auth, default creds.
- **Pattern**: hardcoded creds, web admin unauthenticated, weak firmware update.

### Databases (when exposed via product features)

- **MongoDB**: historically deployed without auth (count it as default).
- **Redis**: historically deployed without auth + arbitrary command exec via config.
- **Elasticsearch**: historically open by default + scripting language RCE families.
- **Pattern**: default no-auth, scripting engines (Painless, Lua), unauthenticated REST APIs.

### Cloud / SaaS infrastructure

- **AWS metadata service**: IMDSv1 SSRF, target `http://169.254.169.254/latest/meta-data/iam/security-credentials/`.
- **Azure metadata**: `http://169.254.169.254/metadata/identity/oauth2/token` (with `Metadata: true` header).
- **GCP metadata**: `http://metadata.google.internal/computeMetadata/v1/` (with `Metadata-Flavor: Google` header).
- **Kubernetes**: exposed kubelet API (10250), exposed dashboard, RBAC misconfig.
- **Pattern**: any SSRF in cloud-hosted product → try metadata endpoints first.

### LLM / AI features (recent, evolving)

- **Prompt injection**: user content reaches system prompt; tool/function calls misdirected.
- **Indirect prompt injection**: content loaded from a URL or file influences instructions.
- **Tool/function call hijack**: model can call privileged tools based on attacker text.
- **Embedding-based RAG poisoning**: adversarial documents in the retrieval corpus.
- **Pattern**: if doc mentions "AI assistant", "agent", "function calling", "RAG", "vector store", apply OWASP Top 10 for LLMs.

---

## C. How to use this file during analysis

When reading a doc and you encounter:

1. **A named technology** (Velocity, Electron, ImageMagick, Jackson, etc.), check section A's dependency list to remember it has CVE history; **web_search** for current state if relevant to the deliverable.
2. **A product type** (wiki, VPN appliance, password manager, etc.), check section B for the family's CVE pattern; reason by analogy.
3. **A vuln class you want to ground in real cases**: point at HackTricks / PayloadsAllTheThings / WSTG for the methodology, then web_search for the specific CVE.
4. **An LLM / AI feature**: apply OWASP Top 10 for LLMs.

This file is not meant to be exhaustive. It is meant to remind you that real prior art exists and to point at where to find it. When in doubt: **web_search beats recalling from memory** for anything time-sensitive (CVE counts, current state, latest writeups).
