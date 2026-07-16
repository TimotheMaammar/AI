# Information Disclosure & Misconfiguration

**TL;DR**: exposed secrets, source, endpoints, stacktraces and files. Often the key that unlocks the rest (creds → access, source → other vulns). Weak alone, huge in a chain.

## Leak sources to check
- **Exposed sensitive files**: `.git/` (dump via git-dumper → source + secrets from history), `.env`, `.svn/`, `.hg/`, `.DS_Store` (file listing), `backup.zip/.tar.gz/.sql/.bak/.old/~`, `config.php.bak`, `wp-config.php.swp`, `docker-compose.yml`, `Dockerfile`.
- **API docs/specs**: `/swagger.json`, `/openapi.json`, `/api-docs`, `/graphql` introspection, `/actuator` (Spring: `/env`, `/heapdump`, `/mappings`, `/configprops`), `/metrics`, `/debug`, `/_profiler`.
- **Panels/consoles**: `/admin`, `/phpinfo.php`, `/server-status`, `/server-info`, `/.well-known/`, exposed Jenkins/Grafana/Kibana/phpMyAdmin, `/console` (Werkzeug debugger → RCE if weak PIN).
- **Cloud storage**: open S3/GCS/Azure buckets (list/read/write), leaked pre-signed URLs.
- **Front-end JS**: API keys, endpoints, secrets, comments, source maps (`.map` → reconstruct the code) → skill `js-analysis` / `00_JS_RECON.md`.
- **Verbose errors**: stacktraces (versions, paths, SQL queries), debug=true (Django/Flask/Rails/Symfony error pages), `X-Debug`.
- **Headers**: `Server`, `X-Powered-By`, `X-AspNet-Version`, versions → known CVEs (outdated components).
- **History**: Wayback/gau for old endpoints/params/secrets, GitHub dorks (repos, commits, gists), Google dorks (`site:target ext:sql|log|bak`), public Postman/SwaggerHub.
- **Secrets in responses**: tokens/PII in JSON (excessive data exposure → `API_MASS_ASSIGNMENT.md`), readable CORS.

## Useful dorks
- Google: `site:target.com ext:log | ext:sql | ext:env | ext:bak`, `intitle:"index of"`, `inurl:admin`.
- GitHub: `"target.com" password`, `org:target api_key`, secrets in commits (trufflehog, gitleaks).
- crt.sh, Shodan (`http.favicon.hash`, `ssl:target`), FOFA/Censys for forgotten assets.

## Rate-limit / logging / exceptional conditions
- Missing logging/alerting (hard to prove in BB, but missing rate-limit/anti-automation = testable).
- **Mishandling of exceptional conditions**: send malformed/boundary inputs (unexpected types, very large numbers, null, arrays, unicode) → fail-open, leak, state inconsistency, bypass. Test behavior under error.

## Nginx misconfigurations
- **Missing root location**: a server-level `root` with only specific `location` blocks lets you fetch config directly, e.g. `GET /nginx.conf`.
- **Alias LFI**: `location /imgs { alias /path/images/ }` (trailing slash) is traversable via `/imgs../secret`. See `PATH_TRAVERSAL_LFI.md`.
- **`merge_slashes off`**: re-opens `//..%2f` traversal (normalization disabled) -> LFI.
- **Unsafe `$uri` in redirect** (`return 302 https://x$uri`): CRLF injection via `/%0d%0aHeader:%20value` because `$uri` is decoded; only `$request_uri` is safe.
- **`SCRIPT_NAME` / fastcgi misconfig**: reflected path -> possible XSS. **Raw backend response reading** via `proxy_pass` leaks backend errors/headers.

## Method
1. Aggressive content discovery (SecLists, tech-specific) + passive recon.
2. Triage 200/403/500; 403 = try bypass (`00_WAF_ENCODING.md`).
3. Extract secrets → validate (creds, tokens) → escalate in the right file.
4. Exposed `.git/`: `git-dumper <url> ./dump`, then `cat .git/logs/HEAD` and `git show <commit>` to recover secrets removed from later commits.

## Impact
- Depends on what leaks: creds/cloud key = Critical; source/spec = enabler; version only = Low. Always chain.

## Caido
- HTTP history to spot leaks (secrets in responses); Automate to brute-force backup/config files + grep-match on `BEGIN PRIVATE`, `apikey`, `password`, `AWS`.

## References
- OWASP WSTG - Information Gathering & Config Testing - https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- PayloadsAllTheThings - https://github.com/swisskyrepo/PayloadsAllTheThings
- git-dumper - https://github.com/arthaud/git-dumper · trufflehog - https://github.com/trufflesecurity/trufflehog
- SecLists (Discovery) - https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content
- HackTricks - Web recon / .git - https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/
