# Phase 2: Attack surface extraction

Mechanical, exhaustive. Go through the doc chapter by chapter and extract every item that fits one of the buckets below. Don't filter; that's phase 3's job. Cast a wide net here.

## 2.1 The buckets (extract every item that fits any of these)

### Network endpoints

- HTTP/HTTPS routes (REST, GraphQL, RPC-over-HTTP, WebDAV, SOAP)
- gRPC services
- WebSocket endpoints
- Raw TCP/UDP listeners
- Server-Sent Events
- mDNS / zeroconf service announcements
- Health checks, metrics endpoints, debug endpoints
- Internal-only endpoints (often weaker auth, sometimes accidentally exposed)

For each: path, method (if HTTP), authentication required, expected input format, brief purpose.

### Authentication mechanisms

- Login flows (password, MFA, SSO via SAML/OIDC/OAuth)
- API tokens / API keys / personal access tokens
- mTLS / certificate authentication
- Session management (cookies, JWT, opaque tokens)
- Password reset / account recovery
- Service-to-service auth (machine accounts, signed requests)
- "Login as", impersonation, delegation
- Anonymous/unauthenticated endpoints by design
- "Magic links", QR-code logins, device-pairing flows
- Webhook signature validation

Note any flow that bypasses MFA (recovery flows, OAuth, API key auth are common bypasses).

### File upload / import

- Endpoints accepting file uploads (image, document, archive, anything)
- Bulk import flows (CSV, JSON, XML, custom)
- Configuration import from file or URL
- Backup restore
- Migration / data import from another product
- Drag-and-drop in desktop apps
- Email-to-app ingestion (forward an email, attach to ticket)

For each: what formats accepted, where stored, what processing happens after upload (thumbnail generation, indexing, virus scan, parsing).

### File format parsers

The single highest-value category. Any time the product *reads* a file format, list it:

- Document formats (PDF, DOCX, ODT, RTF, HTML, EPUB)
- Spreadsheet formats (XLSX, ODS, CSV with formulas)
- Image formats (PNG, JPEG, GIF, TIFF, BMP, WebP, SVG, AVIF, HEIC)
- Video / audio (MP4, MKV, AVI, MP3, WAV, often via ffmpeg)
- Archive formats (ZIP, TAR, RAR, 7z, GZIP, BZIP2, Zip Slip risks)
- Markup / data (XML, JSON, YAML, TOML, INI)
- Font files (TTF, OTF, WOFF)
- Code / config (any DSL the product imports)
- Custom binary formats specific to the product
- Email formats (EML, MSG)
- Database dumps (SQL, BSON, CSV)

For each: which library / parser is used (if mentioned), what triggers parsing (upload, link, automatic).

### Plugin / extension / scripting / template systems

- Plugin frameworks (load .so/.dll/.jar/.py at runtime)
- Extension marketplaces (Chrome-style, VSCode-style)
- Embedded scripting engines (JS via V8/QuickJS, Python, Lua, Ruby, Groovy)
- Template engines (Jinja, Twig, Handlebars, Freemarker, Velocity, ERB, Razor, Pug, Liquid, EJS)
- Webhooks with executable payloads (some products allow JS expressions in webhook URLs)
- Workflow / automation systems (Zapier-style, with code steps)
- DSL or "formula" support (Excel-formula-likes, custom expression languages)
- WASM modules
- Macros

For each: who can install/write them, what isolation exists, what host APIs are exposed, whether code is signed.

### IPC, RPC, shared memory, named pipes, sockets

(Mostly for non-web targets.)

- Named pipes (Windows `\\.\pipe\...`, Unix sockets at `/var/run/*.sock`)
- D-Bus services
- COM / DCOM
- Mach ports (macOS)
- Binder (Android)
- XPC services (macOS)
- Shared memory segments
- Message queues (POSIX, SysV)
- Custom local sockets
- Loopback HTTP services
- Helper processes / launchd / systemd services that accept commands

For each: who can connect, authentication required, what operations exposed.

### Update mechanisms

- Auto-update for the app itself
- Plugin updates
- Definition / rule updates (AV, EDR, WAF, etc.)
- Configuration push from a central server
- OTA updates (mobile, IoT)
- Update servers, update URLs, signature schemes

For each: signing, TLS, update URL configurable by user, what runs as what user during update.

### Embedded browsers / WebViews

- Chromium Embedded Framework (CEF)
- Electron
- Tauri (uses native webview)
- WKWebView / WebView / WebView2
- Server-side headless browsers (for PDF gen, screenshot, web scraping features)
- In-app browsers (mobile)

For each: what content is loaded, is content/origin controlled by attacker, what JS context bridges to native (preload scripts, JS-to-native bridges, postMessage handlers).

### Configuration import/export

- Settings file upload
- "Import settings from URL"
- Cloud sync of settings
- Profile / template / preset sharing

If config is YAML, JSON, XML, or pickle, the parser surface applies. If config includes URLs, SSRF risks. If config includes scripts/templates, code-exec risks.

### Webhooks, callbacks, server-to-server integrations

- Outbound webhooks (you specify URL, product calls it, SSRF risk if not constrained)
- Inbound webhooks (receive payload, parse, act on it)
- OAuth callback URLs
- SAML AssertionConsumerService URLs
- OpenID redirect_uri
- Push notification endpoints

### Admin interfaces, debug modes, developer modes

- Web admin panel (separate or part of main UI?)
- Admin CLI
- Debug toggles (`?debug=1`, env vars, `~/.appname/debug.flag`)
- Developer mode features (often documented in the SDK doc)
- "Maintenance mode" with reduced auth
- Diagnostics dumps, profile reports, stack traces accessible via UI

### Protocol handlers (custom URI schemes, deep links)

- App-registers-URL-scheme features (`myapp://...`)
- Universal Links / App Links (mobile)
- Custom protocol registration on desktop
- File-association handlers (open .myext → triggers app)

### Filesystem access

- Paths the user controls (upload destinations, log file paths, plugin directories)
- Path-traversal-shaped APIs (download files by name, view config by name)
- Symlink-followed APIs
- Temp file usage
- Worldwriteable / group-writeable paths created by installer
- Privilege boundaries that filesystem crosses (root daemon reads from user-writable dir, etc.)

### Email / SMTP / messaging integrations

- Outbound email (SMTP creds, can attacker control content sent to other users / abuse for SSRF via image-loading?)
- Inbound email (parse incoming email, attachments, headers, huge attack surface)
- IRC, XMPP, Matrix, Slack, Teams integrations
- SMS gateways

### Cloud / SaaS integrations

- Integrations with S3, Azure Blob, GCS (credential handling, bucket name configurable)
- LDAP / AD bindings (auth surface)
- Database connectors (JDBC URL configurable → JDBC URL attacks)
- External API integrations with stored credentials

### Telemetry / crash reporting

- What data is collected and where it's sent
- Endpoints contacted, can they be redirected (proxy support, env vars)
- Crash dumps stored where, readable by whom

### Internationalization / localization

(Often dismissed; surprisingly buggy historically.)
- User-selectable language (file path / locale string injection)
- Custom translation upload
- Time zone / locale-based parsing differences

## 2.2 Search hints (how to find these in the doc)

When reading chapter-by-chapter, do a targeted scan using these keyword patterns. They surface items that the chapter title doesn't advertise.

```
# Endpoints
/api/  /v1/  /v2/  /admin  POST /  GET /  endpoint  route  webhook  callback  REST  GraphQL  gRPC  socket  ws://  wss://

# Auth
authenticat  login  logout  session  token  bearer  JWT  OAuth  SAML  OIDC  SSO  LDAP  Kerberos  mTLS  API key  service account  impersonat  delegat

# Upload / import
upload  import  attach  drag-and-drop  multipart  bulk  migration  restore  load  parse  decode

# File formats
PDF  DOCX  XML  YAML  JSON  ZIP  TAR  archive  image  font  CSV  XLSX  base64

# Plugins / scripting
plugin  extension  module  add-on  addon  marketplace  scripting  macro  formula  expression  template  Jinja  Handlebars  Velocity  Freemarker  Lua  Python  JavaScript  Groovy  custom code

# IPC
IPC  socket  pipe  D-Bus  XPC  COM  Mach  shared memory  helper  service  daemon  launchd  systemd

# Update
update  upgrade  signature  verification  patch  OTA  channel  rollout

# WebView
WebView  CEF  Electron  Chromium  embedded browser  in-app browser  preload

# Config
config  configuration  settings  preference  profile  template  preset  YAML  JSON  TOML

# Admin / debug
admin  debug  diagnostic  developer mode  maintenance  internal  staging  experimental

# Protocol handlers
URI scheme  deep link  app link  protocol handler  associat  file type

# Filesystem
path  directory  folder  upload  temporary  symlink  permission

# Integrations
integration  connector  webhook  Slack  Teams  S3  Azure  LDAP  AD  JDBC

# Email
SMTP  IMAP  POP3  email  mailbox  attachment  forward  reply
```

Don't trust your memory, use search across the full extracted text. Many findings are in chapters whose titles do not hint at them.

## 2.3 Output of phase 2

A growing list, organized by category, where each entry is:

```
[Category] Item name | Page reference | Brief description | Trust boundary crossed (Y/N, which) | Attacker-reachable (Y/N, by whom)
```

Example:

```
[Endpoints] POST /admin/api/plugins/install | p.234 | Installs a plugin from a URL or uploaded file | Crosses unauth→admin | CAN BE attacker-reachable if admin creds leak
[File parsers] ZIP archive on plugin upload | p.234 | Plugin distributed as ZIP, extracted to /opt/app/plugins/<name>/ | Crosses upload→filesystem | reachable post-auth
[Webhooks] Outbound webhook URL configurable per workflow | p.412 | User specifies URL, server makes HTTP request | SSRF surface | reachable post-auth
[Embedded browsers] CEF in renderer | p.89 | Renders user-provided HTML in dashboard widgets | Bridges browser→native via preload script | reachable post-auth
```

Keep this list flat and append-only during reading. Phase 3 will mark items dangerous; phase 4 will turn the dangerous ones into hypotheses.
