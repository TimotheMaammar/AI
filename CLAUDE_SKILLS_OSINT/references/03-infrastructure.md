# 03: Infrastructure (Website / Domain / IP)

Pivoting on a website, domain, or IP. Seed is typically a URL, a bare domain, or an IP/ASN. The goal is to map who runs it (person or company), what else they run, and what the site itself exposes about them — without touching the live infrastructure beyond normal passive browsing (see `00-operational-footprint.md`; active scanning is out of scope for this skill, hand that to `identifying-network-services`).

The pivot tree below is transcribed from a field-tested mind map. From the central node WEBSITE, each branch is a pivot; whois and footprinting both key off the domain name, so they are grouped together below even though the mind map draws them as separate branches.

---

## Pivot tree: WEBSITE

```
WEBSITE
├── whois lookup
│   ├── domain owner / registrant contact
│   └── historical whois  ──► past registrants, changes over time
│
├── footprinting
│   ├── subdomain enumeration
│   ├── bulk email harvesting
│   └── bulk document / metadata collection
│
├── social media accounts (linked from the site, or by brand/company name)
│   └── personal / company accounts  ──► 04-socmint.md
│
├── cached data
│   └── search-engine cache
│
├── archive sites
│   ├── Wayback Machine
│   └── archive.today
│
├── site data (read what the site itself publishes)
│   ├── legal notice / mentions légales  ──► registrant company/person
│   ├── contact page
│   ├── people (team/about pages, staff bios)
│   ├── robots.txt  ──► disallowed paths hint at admin/staging/sensitive areas
│   └── sitemap.xml  ──► full page inventory, including unlinked pages
│
├── general search
│   ├── site: operator  ──► scope a search to the domain
│   ├── filetype: operator  ──► documents hosted on the domain
│   └── related: operator  ──► sites Google/Bing consider similar
│
└── company search (from the domain name or the mentions légales)
    └── people / companies  ──► 02-companies.md
```

Two structural points worth internalizing:
- **Whois and the site's own `mentions légales`/legal-notice page are two independent paths to the same answer** (who owns this): whois can be privacy-shielded (GDPR/ICANN redaction, proxy registrars), but a commercial site is often legally required to publish an operator identity on-page (mandatory in France, for example). When one is blocked, try the other.
- **A website is rarely the endpoint.** It almost always resolves to a company (`02-companies.md`) or a person (`01-people.md`) behind it; infrastructure recon exists to get you there, plus to map what *else* that owner runs (other domains, other IPs, a shared analytics ID across "unrelated" sites).

**"Same owner across sites" is an inference, not a fact — treat it with the same discipline as the group-structure, identity-binding, and account-binding claims in `02-companies.md`, `01-people.md`, and `04-socmint.md`.** Reverse-whois and analytics-ID reuse are the two highest-leverage pivots in this file and also the two most prone to false positives: a privacy proxy, a registrar's own placeholder contact, a web agency's boilerplate template, or a reseller's shared account info will produce the exact same "match" pattern between sites that have no real connection to each other. See "Confidence discipline for 'same owner' inferences" below before stating a cross-site ownership link as fact.

---

## Anchoring by seed type

### Seed = domain name
1. **Whois / RDAP first.** `whois domain.com` [cli] or a web RDAP lookup; for `.fr` use AFNIC's whois. Note registrar, creation/expiry/update dates, name servers, and registrant contact if not redacted. A young domain, privacy-shielded registrant, and a registrar known for anonymous registrations are themselves a signal (worth noting even when they block identification).
2. **Historical whois.** If current whois is redacted, the registrant may not always have been: WhoisXMLAPI, whoxy, or SecurityTrails historical whois can show a pre-GDPR or pre-privacy-service record, or a lapse during a renewal where the real registrant briefly showed.
3. **Reverse whois.** Once you have *any* registrant identifier (an email, an organization name, even a literal name), reverse-whois (whoxy, WhoisXMLAPI, DomainTools) finds every other domain registered with the same identifier — this is one of the highest-leverage pivots in the whole skill: one sloppy registration habit exposes an entire portfolio of "unrelated" sites run by the same person/company. It's only meaningful, though, when the identifier is distinctive. A personal email or an uncommon organization name is a strong match; a privacy-proxy address, a registrar's own placeholder contact, or a domain reseller's shared account info returns a long list of genuinely unrelated domains that merely bought from the same service — check what the identifier actually is before reading anything into the hit list. A real hit list can still run to dozens of domains — same depth budget as `01-people.md`'s associate branch: full pass on the seed domain, a bounded pass per sibling domain, entity-level (just note it exists) beyond that.
4. **Read the site itself.** Legal notice (`mentions légales` in France — legally mandatory for commercial sites, usually linked in the footer; equivalent "imprint"/"impressum" pages exist in Germany, Austria, Switzerland), contact page, team/about page, `/robots.txt` (what the owner doesn't want indexed is often informative — admin paths, staging subdomains, old sections), `/sitemap.xml` (the full page inventory, including pages with no inbound link from the nav).
5. **Subdomain enumeration.** crt.sh (certificate transparency — query `%.domain.com`, every subdomain that's ever had a TLS cert issued shows up, including ones never meant to be public), DNSDumpster [web], subfinder/amass [cli] for more exhaustive passive enumeration. Subdomains routinely reveal staging environments, old marketing microsites, internal tools, and acquisitions. **A sparse crt.sh result isn't proof of a small footprint**: a domain covered by a wildcard cert (`*.domain.com`) can show up as a single wildcard entry with the actual subdomains in active use not separately listed underneath it. When crt.sh looks thin, cross-check with subfinder/amass before concluding the attack surface is small.
6. **Tech stack fingerprint.** Wappalyzer or BuiltWith [web] — CMS, analytics IDs (a Google Analytics/Tag Manager/Facebook Pixel ID reused across sites is a lead toward "same owner", searchable via a dork or a dedicated reverse-analytics-ID tool — but check it's a personal/org-specific ID and not a copy-pasted template default: a web agency that reuses the same boilerplate across unrelated clients' sites, forgetting to swap the placeholder ID, produces the identical pattern without a real ownership link), hosting provider, email provider (MX records hint at Google Workspace vs. Microsoft 365 vs. self-hosted, useful later for email-format guessing in `08-tools-catalog.md`).
7. **Favicon and TLS fingerprint — two more "same owner" leads of the same shape as the analytics ID.** Shodan hashes every favicon it indexes (MurmurHash3); `http.favicon.hash:<value>` in Shodan returns every other IP serving an identical icon — favup [cli] computes the hash for a given site and queries it for you, useful for finding an origin IP hidden behind a CDN/WAF. Separately, JARM fingerprints a server's TLS stack (Shodan indexes it as `ssl.jarm:<value>`; the standalone `jarm.py` [cli] computes it directly) — a matching JARM across hosts suggests the same hosting setup. Both carry the exact same caveat as the analytics-ID signal above: a default/framework favicon or a common hosting provider's TLS config produces the identical fingerprint between sites with no real connection, so treat a hit as a Low-confidence lead (per the grid below) until corroborated by something more distinctive.
8. **Archives.** Wayback Machine and archive.today for historical versions — deleted pages, an old team page naming former staff, a pre-redesign contact page with a personal email instead of a generic one, changed ownership/branding over time. Prefer reading the archive over fetching the live page when the fetch itself would be noisy (see `00-operational-footprint.md`). Beyond the calendar UI, Wayback's **CDX API** (`web.archive.org/cdx/search/cdx?url=domain.com/*&from=YYYYMMDD&to=YYYYMMDD&collapse=timestamp`) can be queried directly for a date-bounded, deduplicated list of every captured URL — useful when scripting a historical pull across many pages instead of clicking through the calendar by hand. Jump straight to one capture with `web.archive.org/web/YYYYMMDDhhmmss/<url>` once you have a timestamp. `automation.md`'s **Waymore** entry wraps this for bulk recovery.
9. **Search-engine cache.** Google's own cache is largely gone, but Bing and some regional engines still cache; archive.today and the Wayback Machine are the reliable substitutes now.
10. **Dorks scoped to the domain.** `site:domain.com filetype:pdf` (leaked documents, internal reports accidentally published), `site:domain.com intitle:"index of"` (open directory listings), `related:domain.com` (Google/Bing's own similarity graph, sometimes surfaces sibling/competitor sites run by the same org). Full operator list in `references/07-dorks-and-search.md`. **Exposed cloud storage** is a distinct, high-value variant: `site:s3.amazonaws.com "company name"` finds indexed-but-public buckets, and GrayhatWarfare (buckets.grayhatwarfare.com) runs a dedicated search engine over publicly-readable S3/Azure/GCS buckets by keyword, extension, or path — a company-name search there routinely surfaces an open bucket with no credentials needed, which is both a direct finding and, operationally, worth a defensive-posture note if the engagement has one.
11. **Company search.** Take whatever registrant/operator identity you found (from whois, the legal notice, or the WHOIS organization field) into `02-companies.md` to pull the full corporate picture.

### Seed = IP address / ASN
1. **Reverse IP / hosting.** ViewDNS.info reverse-IP (other domains hosted on the same IP — meaningful on dedicated/VPS hosting, noisy on shared hosting/CDNs), BGP.he.net for ASN/prefix ownership and the organization that holds the IP block.
2. **Exposure search engines.** Shodan / Censys / FOFA / ZoomEye [web] — query the IP for exposed services, banners, and certificates. This reads existing scan data; it is not you scanning the target (stays OSINT-clean). See `08-tools-catalog.md`.
3. **Certificate data.** Any TLS cert served by that IP (via Censys/Shodan or crt.sh by IP) names every hostname on the cert's SAN list — often reveals the "real" hostname behind an IP presented generically.
4. **GreyNoise.** Tells you whether the IP itself is known mass-scanner/bot noise vs. a targeted, dedicated host — useful context before reading too much into a single IP.
5. From any hostname found this way, fold back into the domain-name path above.

---

## Specific site-data checklist (always run these on a target-owned site)

- `/robots.txt` — disallowed paths are a map of what the owner considers sensitive or doesn't want indexed; visit the disallowed paths yourself (robots.txt is a request to crawlers, not an access control).
- `/sitemap.xml` (and `/sitemap_index.xml` for larger sites) — full page inventory; diff against what's actually linked from navigation to find orphaned/forgotten pages.
- `/.well-known/security.txt` — sometimes names a security contact (a real person/team) and a PGP key.
- `/humans.txt` — occasionally used by agencies/dev shops to credit the people who built the site, by name.
- View-source / page metadata — `<meta name="generator">` (CMS + version), analytics/tag-manager IDs in the `<head>`, comments left in HTML/JS by developers (names, internal tool references, TODOs).
- JS bundles — endpoints, internal hostnames, API keys, and comments are routinely exposed in shipped JavaScript; see the `js-analysis` skill for a deep pass if the site is a SPA with heavy client-side logic.
- Legal notice / mentions légales, Terms of Service, Privacy Policy — these pages are where a company is contractually obligated to name itself, its registered address, and (in the EU) its data controller; read them even when they look boilerplate.

---

## Confidence discipline for "same owner" inferences

Rate a cross-site ownership claim with the same confidence grid used in `01-people.md`, `02-companies.md`, `04-socmint.md`, and `06-geolocation.md` (Low/Moderate/High/Inconclusive, an internal working grid kept consistent across the skill), separately from the Admiralty rating of each signal feeding into it.

| Confidence | Criteria |
|---|---|
| **Low** | One shared element only, and it's of a type known to be reused across unrelated parties (privacy-proxy contact, registrar placeholder, reseller account, agency-template analytics ID, a default/framework favicon hash, a common-hosting-provider JARM fingerprint). |
| **Moderate** | Two or more independent signals point the same way (shared distinctive registrant identifier **and** shared analytics ID, or shared hosting IP **and** matching TLS SAN hostname), none individually decisive. |
| **High** | A hard link confirms it: a distinctive personal/org-specific identifier (not a proxy or template default), a legal-notice page naming the same entity on both sites, or the registrant/analytics match corroborated by a company-registry or social pivot. |
| **Inconclusive** | The shared element is independently known to be a shared-service pattern (proxy, reseller, template), or signals conflict. |

Record it the same way as the other files: the claim, each signal rated individually, the shared-service/template alternative considered and why it was or wasn't ruled out, disconfirming evidence actively sought (e.g. checked whether the shared registrant contact resolves to a known proxy/reseller service rather than a real identity), the confidence level, and the conclusion as worded in the dossier.

---

## Common pivots out of this file
- Registrant / legal-notice identity → company: `02-companies.md`
- Registrant / legal-notice identity → person: `01-people.md`
- Social links found on the site: `04-socmint.md`
- Harvested emails from the domain: `01-people.md` (email anchoring) and `05-breaches.md`
- Building whois/reverse-whois/dork queries: `references/07-dorks-and-search.md`
- Tool shortlist for each step above: `references/08-tools-catalog.md`
- Bulk subdomain/email/document collection at scale: `references/automation.md`
