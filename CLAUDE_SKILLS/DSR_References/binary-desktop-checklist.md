# Binary / desktop / mobile deep checklist

Load when the documented product is a native binary, desktop application (Win/macOS/Linux), mobile app (Android/iOS), CLI tool, daemon, system service, firmware image, embedded device, or any non-web target. Also load alongside `web-saas-checklist.md` when a desktop product has a web admin or a mobile app has a backend.

This checklist complements (does not replace) phases 2-4. Use it to make sure no native-specific category was missed.

---

## A. Process model and privileges

- [ ] **What user does each process run as?** Daemons / services / helpers, document the privilege of each.
- [ ] **Setuid / setgid binaries.** Anywhere in the install? Even one is a major PE target.
- [ ] **Privileged helpers.** GUI runs as user, helper runs as root/admin via IPC, classic PE surface.
- [ ] **Auto-start / persistence.** systemd unit, launchd plist, Windows service, scheduled task, login item, registry Run keys. Each is a persistence + PE vector.
- [ ] **Capabilities (Linux).** `setcap` documented? `CAP_NET_ADMIN`, `CAP_SYS_ADMIN`, `CAP_DAC_READ_SEARCH`?
- [ ] **macOS entitlements.** Hardened runtime? `com.apple.security.cs.disable-library-validation`? `com.apple.security.get-task-allow`? Sandbox entitlement?
- [ ] **Android permissions.** Documented? Any of: Accessibility, Device Admin, MDM, SYSTEM_ALERT_WINDOW, BIND_NOTIFICATION_LISTENER, BIND_DEVICE_ADMIN?
- [ ] **iOS entitlements.** Network extension, VPN, system extension, kext (legacy)?

## B. IPC surfaces

- [ ] **Unix sockets / Windows named pipes**: listing, who can connect, authentication on connect.
- [ ] **D-Bus services** (Linux desktop), bus names, methods exposed, polkit policy.
- [ ] **XPC services** (macOS), service registration, code-signing requirement on caller (often `SecCodeCheckValidity`).
- [ ] **Mach ports** (macOS).
- [ ] **COM / DCOM** (Windows), registered CLSIDs / AppIDs, authentication level, launch permissions.
- [ ] **Binder** (Android), exported services, interface auth (`checkCallingPermission`, `checkCallingUid`).
- [ ] **Shared memory** segments, POSIX shm, SysV shm, Windows mailslots.
- [ ] **Local HTTP listeners** (`127.0.0.1:NNNN`), surprisingly common; often unauthenticated.
- [ ] **WebSocket on localhost**: same.
- [ ] **Custom local sockets** with custom protocol.

For each: who can connect (any local user? specific UID? code-signing-verified caller?), what auth happens (token? UID check? code signature check?), what operations are exposed.

## C. Update mechanisms

- [ ] **Self-update.** Update URL: configurable, HTTPS, certificate-pinned?
- [ ] **Signature verification.** Public key embedded? Algorithm (RSA / Ed25519 / weaker)?
- [ ] **Channel selection** (stable / beta / nightly), can be downgraded to a vulnerable old version?
- [ ] **Rollback prevention.** Version monotonicity enforced?
- [ ] **What user runs the update.** Often elevated (writes to Program Files / /Applications), update path is a major target.
- [ ] **Differential updates.** Patch application logic, historically buggy.
- [ ] **Update for plugins / extensions**: same questions, often weaker than self-update.
- [ ] **Definition / rule updates** (AV-style products), signed?

## D. Plugin / extension systems

- [ ] **Plugin file format and load mechanism.** Native (DLL/.so/.dylib)? Managed (.jar/.NET)? Script (Python/Lua)?
- [ ] **Plugin signature verification.**
- [ ] **Plugin install dir permissions.** User-writable plugin dir + service runs as root = plugin sideload PE.
- [ ] **Plugin discovery.** From config? From dir scan? Order of dirs (env vars influence)?
- [ ] **Plugin API exposed.** What host capabilities can a plugin call?
- [ ] **Plugin sandbox.** Existence, design, known escapes.
- [ ] **Plugin marketplace**: supply chain, search-result confusion, typosquatting.

## E. File handling

- [ ] **File associations.** What extensions does the app register? Opening one launches the app with the file path as argv.
- [ ] **Drag-and-drop.** Accepts what?
- [ ] **Recent files / autoload on startup.** If poisoned, RCE on next launch.
- [ ] **Temp file usage.** Where (`/tmp`, `%TEMP%`)? Predictable names? Race-prone creation?
- [ ] **Cache / config / data dir permissions.** Mode 600 / 700 / 666 / 644?
- [ ] **Symlink handling.** Followed when reading config / data?
- [ ] **Log file paths.** Predictable? In user-writable dirs? Followed symlinks (log-to-arbitrary-write)?
- [ ] **Crash dump locations.** PII / token leakage?

## F. Custom URL schemes and protocol handlers

- [ ] **What schemes does the app register?** `myapp://`, `myapp-debug://`, multiple.
- [ ] **What does each scheme do?** Load URL in embedded browser? Open file path? Execute action with parameters?
- [ ] **Parameter validation.** URL-decoded? Length-limited? Filtered? Scheme + host + path validation?
- [ ] **Reachability.** Triggered by clicking a link in a browser, in an email, in another app. Effectively remote attack surface.
- [ ] **Mobile: Universal Links / App Links.** Domain ownership verified (`apple-app-site-association`, `assetlinks.json`)?

## G. Embedded browsers and WebViews

This is one of the highest-value categories for desktop / mobile apps.

- [ ] **Engine.** CEF? Electron (Chromium + Node)? Tauri (system WebView)? WKWebView / WebView2 / Android WebView?
- [ ] **Content loaded.** Always local files (file://)? HTTPS to vendor server? User-controlled URLs?
- [ ] **CSP applied?** What policy?
- [ ] **JS-to-native bridge.** Exposed via:
  - Electron: preload script, `contextBridge`, IPC
  - macOS WKWebView: `WKScriptMessageHandler`
  - Android WebView: `addJavascriptInterface`
  - iOS UIWebView (deprecated): `JSContext`
- [ ] **Bridge surface enumeration.** What methods? What parameters validated?
- [ ] **Origin check on bridge calls.** Often missing, any iframe can call `bridge.X`.
- [ ] **Electron-specific:**
  - `nodeIntegration` enabled? (Default off in modern versions, but check.)
  - `contextIsolation` enabled? (Default on in modern versions.)
  - `webSecurity` disabled? (Disabling allows file:// XHR to anywhere.)
  - `allowRunningInsecureContent`?
  - `experimentalFeatures`?
  - Open windows: `webPreferences` inheritance, `window.open` carrying over node integration.
- [ ] **Loading remote content with privileges**: major Electron pitfall.

## H. Cryptographic surface

- [ ] **TLS configuration.** Cert pinning? Configurable trust store? `--insecure` style flags?
- [ ] **Crypto for local data at rest.** What's encrypted, what key, where stored.
- [ ] **Key derivation from password.** PBKDF2 / scrypt / Argon2 / single-iteration hash?
- [ ] **Keychain / credential manager integration.** Stored in OS secure storage or in a config file?
- [ ] **Master password feature.** Where does the master password go? Memory? Disk?
- [ ] **Custom crypto.** Always a finding.

## I. Network behavior

- [ ] **Outbound connections.** What endpoints, what for (telemetry, update, license check)?
- [ ] **Endpoints configurable.** Can env var / config / argv redirect them?
- [ ] **DNS over plain vs DoH / DoT.**
- [ ] **Proxy support.** HTTP_PROXY honored? Auth proxy creds stored where?
- [ ] **Listening sockets.** Localhost only or all interfaces? Default bind address.
- [ ] **mDNS / Bonjour broadcasts.** Discoverable on LAN?
- [ ] **Multicast / broadcast usage.**

## J. Mobile-specific

### Android

- [ ] **AndroidManifest review** (if available, often partially documented in vendor docs):
  - Exported components (`activity`, `service`, `provider`, `receiver` with `android:exported="true"`).
  - Permissions declared.
  - Custom permissions defined.
  - `android:debuggable`.
  - `android:allowBackup`.
  - `usesCleartextTraffic` / network security config.
  - Intent filters with `BROWSABLE`.
- [ ] **Content Providers.** What URI authorities? What permissions? `grantUriPermissions`?
- [ ] **WebView usage.** `setJavaScriptEnabled`, `addJavascriptInterface`, `setAllowFileAccess`, `setMixedContentMode`.
- [ ] **Deep links.** Custom scheme + intent filter combos.
- [ ] **Tap-jacking / overlay.** `filterTouchesWhenObscured`.
- [ ] **Backup mechanism.** `allowBackup` true → adb backup extraction.
- [ ] **External storage usage** (`getExternalFilesDir`, `Environment.getExternalStorageDirectory`), historically world-readable.
- [ ] **SQL injection in Content Provider queries**: common in providers built around raw query construction.

### iOS

- [ ] **Info.plist review:**
  - `LSApplicationQueriesSchemes` (which other apps queried).
  - `CFBundleURLTypes` (registered URL schemes).
  - `NSAppTransportSecurity` exceptions (which domains bypass HTTPS).
  - `UIFileSharingEnabled` (iTunes file sharing).
  - `LSSupportsOpeningDocumentsInPlace`.
- [ ] **Keychain access groups.** Shared with which other apps?
- [ ] **App groups.** Shared container with which extensions?
- [ ] **App extensions.** Share, action, custom keyboard, etc., each is a separate process with separate entitlements.
- [ ] **Universal Links.** Domain association via `apple-app-site-association`.
- [ ] **Pasteboard usage.** Reading clipboard, especially `general` pasteboard.
- [ ] **Background modes.** Network, audio, location.

### Cross-mobile

- [ ] **Certificate pinning.** Documented? Bypassable via debugger / Frida?
- [ ] **Jailbreak / root detection.** Mentioned? Often weak.
- [ ] **Local data storage.** SQLite, plist, files, encrypted? Where?
- [ ] **Inter-app communication.** Deep links, custom schemes, share extensions, Bonjour, BLE.

## K. Configuration files

- [ ] **Locations.** Per-user, system-wide, defaults shipped with binary?
- [ ] **Permissions.** What modes? Group/world readable?
- [ ] **Format.** YAML (parser surface), JSON (lighter), TOML, INI, custom.
- [ ] **Schema enforcement.** Validates input or trusts file content?
- [ ] **Reload mechanism.** SIGHUP, file watch, restart-only?
- [ ] **Secrets in config files.** API keys, DB passwords, TLS keys?
- [ ] **Environment variables.** What is read? Path-influencing vars (`LD_PRELOAD`, `LD_LIBRARY_PATH`, `DYLD_*`, `PATH`)?

## L. Persistence / install

- [ ] **Install destination.** Permissions of install dir.
- [ ] **Installer privileges.** Runs as admin? Drops setuid binaries?
- [ ] **Uninstaller behavior.** What's left behind? Privilege when uninstalling?
- [ ] **Service registration.** systemd, launchd, Windows Service, Scheduled Task.
- [ ] **Autostart hooks.** Login items, registry Run keys, /etc/profile.d, ~/.config/autostart/.

## M. Specific high-risk patterns to grep for (extracted text)

```
# Process / privilege
rg -i "root|administrator|admin user|superuser|setuid|setgid|elevation|UAC|sudo"

# IPC
rg -i "named pipe|socket|D-Bus|XPC|Mach port|Binder|RPC|IPC|local listener|loopback"

# Update
rg -i "auto.?update|self.?update|update server|signature|verify.*update"

# Plugin
rg -i "plugin|extension|module|add-?on|sideload|signature"

# WebView / Electron
rg -i "WebView|CEF|Electron|Chromium|nodeIntegration|contextIsolation|preload"

# URL schemes
rg -i "URI scheme|custom URL|protocol handler|deep link|app link|registerProtocol"

# Update / load paths
rg -i "LD_PRELOAD|LD_LIBRARY_PATH|DYLD_|PATH=|search.*path"

# File operations
rg -i "symlink|symbolic link|temp file|tmpfile|world.?writ|chmod 777|0666"

# Crypto smells
rg -i "ECB|MD5|SHA1|RC4|DES|custom encryption|our own crypto|obfuscat"

# Mobile
rg -i "exported|content provider|JavascriptInterface|allowBackup|debuggable|cleartext"

# Default creds
rg -i "default password|default credentials|out of the box|factory default"
```

## N. Specific patterns by app type

- **Antivirus / EDR:** kernel driver attack surface, scanner parser bugs (every file-format parser is in scope), update channel hijack, self-protection (`SetThreadInformation` / hooks) bypasses, IPC between user-mode UI and kernel driver.
- **Backup software:** restoration as root, archive extraction (Zip Slip in restoration), symlink handling, encryption at rest, repository protocol surface.
- **Password managers:** master password handling, autofill scope (which fields, which domains, frame matching), browser integration (native messaging host, URL scheme), local data file encryption.
- **VPN clients:** privileged helper for routing/firewall changes, tun/tap device control, DNS handling, kill switch races, leak on network change.
- **Remote support / TeamViewer-style:** session establishment auth, file transfer, command surface during session, accessibility permissions abuse.
- **DevOps agents** (CI runners, deployment agents): work directory permissions, secret handling, runner-to-server protocol, job script execution context.
- **IoT / embedded firmware:** firmware update protocol, factory reset behavior, hardcoded creds, debug interfaces (UART/JTAG), bootloader, OTA channel.
- **Browsers / browser extensions:** content script / page injection, message passing, host permission scope, declarative net request rules.
- **Email clients:** MIME parser, HTML rendering, calendar parser, S/MIME / PGP integration, attachment handling, link preview / unfurl.
- **PDF readers / office suites:** macro engines, JS engines, plugin systems, font parsing, file format parsers.

---

## Output addition

Append to phase 2's attack-surface list any items the checklist surfaced. Some items here may require the user to share additional materials (the manifest, the install script, a binary for static analysis), flag those as follow-ups in the deliverable. The doc may not give complete answers; recording the unknowns is itself part of the value.
