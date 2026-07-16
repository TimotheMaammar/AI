# Subdomain Takeover

**TL;DR**: a DNS record (often CNAME) points to an **unclaimed** third-party service → you claim the resource and serve content on the target's subdomain. Impact: credible phishing, cookie theft (if the parent-domain cookie scope applies), allowlist bypass, same-site XSS.

## Detection
1. Enumerate subdomains (crt.sh, Subfinder, Amass, gau/Wayback).
2. Resolve + get the CNAME (`dig CNAME sub.target.com`, dnsx `-cname`).
3. Spot CNAMEs to a SaaS provider + a **"not found / no such bucket / no app"** error response.
4. Tools: `subjack`, `subzy`, `nuclei -t takeovers`, `dnsReaper`, can-i-take-over-xyz (fingerprints).

## Fingerprint signals (common examples)
- **GitHub Pages**: "There isn't a GitHub Pages site here".
- **AWS S3**: "NoSuchBucket".
- **Heroku**: "No such app" / "herokucdn".
- **Azure** (`*.azurewebsites.net`, `trafficmanager.net`, `cloudapp.net`): specific 404.
- **Fastly**: "Fastly error: unknown domain".
- **Shopify, Zendesk, Surge, Netlify, Readme, Unbounce, Cargo, Tumblr, WordPress, Ghost, Bitbucket, Desk, Statuspage, Tilda, Webflow, Pantheon**: each has its own message/condition. See can-i-take-over-xyz.
- **Dangling NS / MX**: delegation to a provider where you can create the zone → full DNS takeover.

## Verification & claim (responsible)
- Confirm the resource is **actually claimable** (create the same-named app/bucket/repo at the provider).
- Minimal PoC: serve a neutral page (`PoC by <handle>, no malicious content`) or a unique file. Do **not** host real phishing.

## Escalation / impact
- **Cookie theft**: if the parent domain sets `Domain=.target.com` cookies, the takeover subdomain receives them → session theft.
- **CORS/allowlist bypass** whitelisted on `*.target.com`.
- **OAuth `redirect_uri`** whitelisted by subdomain → ATO (`OAUTH.md`).
- **Phishing** with high credibility.
- Second-order: subdomain pointing to a CDN/JS you control → XSS/supply-chain.

## Variant: assorted dangling records
- CNAME to an old bucket, dangling NS, dangling A to a recycled cloud IP (claim an ephemeral IP), dangling MX (email interception).

## Impact
- Often Medium/High; High/Critical with parent cookie or OAuth allowlist.

## Caido
- Little Caido here (mostly DNS/HTTP recon). Use Caido to check the provider's HTTP response and confirm the fingerprint.

## References
- can-i-take-over-xyz (fingerprints) - https://github.com/EdOverflow/can-i-take-over-xyz
- Patrik Hudak - Subdomain takeover basics - https://0xpatrik.com/subdomain-takeover-basics/
- HackTricks - Domain/Subdomain takeover - https://book.hacktricks.wiki/en/pentesting-web/domain-subdomain-takeover.html
- Nuclei takeover templates - https://github.com/projectdiscovery/nuclei-templates/tree/main/http/takeovers
- subzy / subjack / dnsReaper - https://github.com/LukaSikic/subzy
