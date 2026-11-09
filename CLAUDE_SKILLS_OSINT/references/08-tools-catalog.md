# 08: Tools Catalog

Concrete tools and queryable sources by function. Two tags throughout:

- **[web]**: queryable from a browser or a single HTTP request, no install. Prefer these. They are the dorks-and-sources-first backbone.
- **[cli]**: needs install (`pip`, `git clone`, build). Use only when a [web] option cannot do the job or when scale demands it.

Tools rot. If a named one is dead, the category and the description still tell you what to search for as a replacement. Anchor findings on the underlying source, never on the tool.

---

## Email

| Tool | Tag | Use |
|---|---|---|
| Hunter.io | [web] | Company email format + known addresses for a domain. The fastest first move on corporate email. |
| Phonebook.cz | [web] | Free bulk email/subdomain/domain enumeration for a domain. |
| Snov.io, RocketReach, VoilaNorbert, Clearbit | [web] | Email finder/enrichment (freemium). Cross-check Hunter. |
| Have I Been Pwned | [web] | Which breaches an address appeared in. Free by email. First breach move. |
| DeHashed, LeakCheck, Snusbase | [web] | Paid breach search with plaintext-adjacent fields. See `05-breaches.md`. |
| IntelX (intelx.io) | [web] | Freemium index of leaks, pastes, darkweb, historical data, searchable by email/domain/selector. |
| EmailRep.io | [web] | Reputation/profile of an address (seen on which services, risk). |
| holehe | [cli] | Checks which sites have an account registered to an email, via password-reset/signup flows. `holehe target@mail.com --only-used`. Note: some providers email the owner about reset/signup attempts. |
| h8mail | [cli] | Breach hunting for an email across multiple sources. `h8mail -t target@mail.com`. |
| theHarvester | [cli] | Emails + subdomains + hosts for a domain from many search backends. `theHarvester -d target.com -b all`. |
| GHunt | [cli] | Deep profile of a Google account from an email (name, photos, calendar, maps reviews, timezone). Online mirror exists [web]. |
| Epieos | [web] | Broader passive sweep from a bare email: checks Google services + dozens of consumer apps at once, confidence-scored; for Gmail can estimate an activity timeline (creation/last-active). Run alongside GHunt, not instead of it. |

Email format inference: find two or three real addresses, deduce the pattern (`first.last@`, `flast@`, `firstl@`, `first_last@`, `first@`), then generalize to the whole org chart. The headless engine in `automation.md` harvests; the permutator below generates candidates to verify (MX/SMTP check, or against `holehe`/Hunter verifier).

```
patterns for {first}.{last}@{domain}:
  {first}.{last}  {f}{last}  {first}{l}  {first}_{last}  {first}  {last}.{first}  {f}.{last}
```

Verification without sending mail: `dig mx target.com` for the mail server, then an SMTP `RCPT TO` probe (250 = exists, 550 = not), or a verifier API. SMTP probing is noisy and sometimes logged by the mail server.

---

## Username / pseudonym

| Tool | Tag | Use |
|---|---|---|
| WhatsMyName (web app) | [web] | Checks a username across hundreds of sites. The go-to first move. |
| Instant Username Search | [web] | Fast live availability check across many platforms. |
| Sherlock | [cli] | Same idea, scriptable across 400+ sites. `sherlock username`. |
| Maigret | [cli] | Sherlock successor, richer per-site data extraction. |
| Gravatar | [web] | `gravatar.com/{md5(email)}.json` returns profile + avatar for an address. Reverse-image the avatar. |
| Namechk, KnowEm | [web] | Username + brand availability across platforms. |

Method: confirm the handle across platforms, reverse-image avatars, read cross-platform consistency (same bio, links, writing style). Treat this as a hypothesis, not a bind — corroborate with a hard link before crediting it and bridging to a real name. See the confidence grid and impersonation caution in `04-socmint.md`.

---

## Domain / IP / infrastructure

| Tool | Tag | Use |
|---|---|---|
| crt.sh | [web] | Certificate transparency logs: subdomains and internal hostnames from issued TLS certs. Top passive subdomain move. |
| DNSDumpster | [web] | DNS recon + subdomain map + host relationships, no install. |
| SecurityTrails | [web] | Passive DNS, historical DNS/whois, subdomains (freemium). |
| ViewDNS.info | [web] | Reverse IP, reverse whois, DNS history, all from one page. |
| Shodan | [web] | Internet-exposed hosts/services/banners/certs. Query a domain, IP, or ASN; you read scan data without touching the target. |
| Censys | [web] | Like Shodan; strong on certs and host inventory. |
| FOFA, ZoomEye | [web] | Alternative exposure search engines, different coverage. |
| GreyNoise | [web] | Tells whether an IP is mass-scanner noise or targeted. |
| BGP.he.net (Hurricane Electric) | [web] | ASN/prefix ownership, peering, IP ranges for an org. |
| whois / RDAP | [web]/[cli] | Registrar, dates, sometimes registrant. AFNIC for `.fr`, RDAP for structured output. |
| WhoisXMLAPI, whoxy | [web] | Whois history + reverse whois (other domains by same registrant/email). |
| Wappalyzer, BuiltWith | [web] | Tech stack of a site (CMS, frameworks, analytics IDs that pivot to sibling sites). |
| favup | [cli] | Hashes a site's favicon and queries Shodan's `http.favicon.hash:` facet for every other IP serving the identical icon — useful for finding an origin IP hidden behind a CDN/WAF, or a "same owner" lead. Default/framework favicons produce false matches; corroborate. |
| JARM (`jarm.py`) | [cli]/[web] | Fingerprints a server's TLS stack; Shodan indexes it as `ssl.jarm:`. Matching JARM across hosts suggests the same hosting setup — not proof of common ownership, shared hosting/CDN produces the same fingerprint for unrelated sites. |
| GrayhatWarfare (buckets.grayhatwarfare.com) | [web] | Search engine over publicly-readable cloud storage buckets (S3/Azure/GCS) by keyword/extension/path. A company-name search routinely surfaces an open bucket needing no credentials. See `03-infrastructure.md`. |
| Wayback Machine, archive.today | [web] | Historical snapshots, deleted pages, old robots.txt and staff pages. CDX API (`web.archive.org/cdx/search/cdx`) for scripted, date-bounded pulls — see `03-infrastructure.md`. |
| Waymore | [cli] | Bulk-crawls Wayback's CDX API (plus a few other archive sources) for a domain to recover old pages/posts a live search won't surface. |
| amass | [cli] | Heavy subdomain enumeration (passive + active). Passive mode stays OSINT-clean. |
| subfinder | [cli] | Fast passive subdomain enumeration from many sources. |

Passive DNS + cert transparency + reverse-whois usually map an org's external footprint without a single packet to the target. See `03-infrastructure.md`.

---

## Image / face / geolocation

| Tool | Tag | Use |
|---|---|---|
| Google Lens / Images | [web] | General reverse image; strong on objects, landmarks, products. |
| Yandex Images | [web] | Strong reverse-image option for faces and non-Western/Cyrillic content; not a universal default — see the engine-selection table in `06-geolocation.md` for which engine fits which image type. |
| Bing Visual Search, TinEye | [web] | Additional reverse-image coverage; TinEye is best for finding exact-copy provenance and oldest occurrence. |
| PimEyes | [web] | Face search across the web (paid). |
| FotoForensics, Forensically | [web] | ELA and manipulation analysis. |
| Jeffrey's EXIF Viewer, exiftool | [web]/[cli] | Read EXIF: camera, software, timestamps, GPS. `exiftool image.jpg`. Strip-aware: many platforms remove EXIF on upload. |
| SunCalc, Suncalc.org | [web] | Shadow/sun-position geolocation and time-of-day estimation. |
| Overpass Turbo | [web] | Query OpenStreetMap for features seen in an image (a church 80m from a roundabout). |
| Bellingcat OSM Search | [web] | Describe objects + distances, get matching places. |
| Mapillary, KartaView, Google Street View | [web] | Ground-level imagery to confirm a location. |
| Sentinel Hub, Google Earth, USGS EarthExplorer | [web] | Satellite/aerial imagery, including historical. Google Earth **Pro** (desktop app) has a historical-imagery time slider the Maps web view doesn't expose. |
| Bellingcat Shadow Finder | [web] | Automates shadow-based sun-position chronolocation across candidate locations instead of manual SunCalc slider-matching. See `06-geolocation.md`. |

See `06-geolocation.md` for the full image pivot tree.

---

## Transport and wireless tracking (chronolocation / scene confirmation)

| Tool | Tag | Use |
|---|---|---|
| WiGLE.net | [web] | Crowdsourced WiFi-AP database, searchable by SSID or BSSID — places a photo/screenshot showing a visible network name at a specific building. SSIDs aren't unique; cross-check the BSSID. |
| FlightRadar24, ADS-B Exchange | [web] | Historical flight tracks, for matching a visible/audible aircraft to a time window. Match on the ICAO24 hex code (persists across repaints/registration changes), not the tail number. |
| OpenSky Network | [web] | Research-oriented flight-tracking history (30-day window, open API). Many military/corporate aircraft are deliberately excluded — absence isn't proof nothing was there. |
| MarineTraffic, VesselFinder | [web] | Historical AIS vessel tracks. AIS is self-reported and spoofable — corroborating evidence, not standalone proof. |

See the "Chronolocation" section of `06-geolocation.md` for the method.

---

## Company / corporate

| Tool | Tag | Use |
|---|---|---|
| OpenCorporates | [web] | Cross-jurisdiction company registry aggregator. First stop for any company. |
| GLEIF LEI Search | [web] | Global Legal Entity Identifier search (ISO 17442). Free, official (GLEIF is the regulator-backed body behind the standard), and cross-jurisdiction like OpenCorporates — but where OpenCorporates aggregates registry scrapes, an LEI record is self-filed by the entity to a GLEIF-accredited registration agent and renewed annually, and (when filed) its "Level 2" relationship data states the entity's direct and ultimate parent explicitly. Mostly populated by entities that need an LEI for a reason (issuing securities, derivatives counterparties, some EU/UK regulatory reporting) — strong hit rate for mid-size-and-up companies and financial entities, thin-to-absent for small/local businesses. A stated parent relationship here is a harder "same group" signal than a shared officer/address — see `02-companies.md`'s confidence grid. |
| Pappers, Societe.com, Infogreffe | [web] | France: officers, filings, beneficial owners, financials, bylaws. All three also support **searching by person name** (a "dirigeant" search, not the default company-name box) to find every company a given individual is an officer of — the reverse direction from the usual company-first lookup, and worth running on every French person seed by default. See `01-people.md`. |
| BODACC | [web] | France: official legal announcements (incorporation, insolvency, sales) — also searchable by person name, surfacing filings that name them. |
| RNA / Journal Officiel Associations | [web] | France: officers (président/trésorier/secrétaire) of any *association loi 1901* — sports clubs, cultural associations, charities. The nonprofit-world equivalent of the dirigeant search above, and not covered by Pappers/Societe.com at all. See `01-people.md`. |
| Pappers' "Artisans" tab | [web] | France: Répertoire des Métiers / Chambre de Métiers et de l'Artisanat registration — registered tradespeople (plumbers, electricians, hairdressers, etc.), a different register from the dirigeant search even for a self-employed craftsperson. |
| INPI | [web] | France: trademarks, patents, designs, plus the national company register. |
| Companies House | [web] | UK: officers, filings, charges, free and complete. |
| Charity Commission (England & Wales), OSCR, CCNI | [web] | UK: charity trustees/officers — the association-registry equivalent, not in Companies House. |
| SEC EDGAR | [web] | US: public-company filings (10-K, 8-K, ownership). |
| ProPublica Nonprofit Explorer, IRS Tax Exempt Org Search | [web] | US: nonprofit officers/board via Form 990 filings — the association-registry equivalent. |
| Bundesanzeiger, Handelsregister | [web] | Germany: filings and company register. |
| EUIPO, WIPO Global Brand DB | [web] | EU/global trademarks and designs. |
| Aleph (OCCRP) | [web] | Cross-border investigative dataset: leaks, registries, sanctions, for following entities and people across borders. |
| OffshoreLeaks (ICIJ) | [web] | Offshore entity database (Panama/Paradise/Pandora papers). |

See `02-companies.md` for the pivot tree and `references-by-region.md` for the per-country registry list.

---

## Elected office / civil service

| Tool | Tag | Use |
|---|---|---|
| RNE (Répertoire National des Élus) | [web] | France: every mayor, municipal/departmental/regional councillor, MP, and senator, as open data (data.gouv.fr) — but served as raw per-mandate-type CSVs, not a name-search box. For a quick lookup use a front-end built on it (e.g. Civiqo, civiqo.fr) and climb back to the raw CSV to confirm before resting a high-stakes claim on the aggregator alone. |
| JORF / Légifrance search | [web] | France: civil-service concours (entrance exam) admissibility/admission lists by name, plus nomination decrees for civil servants, magistrates, military officers. |
| Wikidata | [web] | Cross-country, partial: a politician's "position held" statements, queryable directly or via query.wikidata.org for a SPARQL search. Strongest at national level; thins out below that. For anything else, or a country not listed here, see `references-by-region.md`'s discovery method rather than assuming a French-style registry exists. |

---

## Genealogy

| Tool | Tag | Use |
|---|---|---|
| Geneanet, Filae | [web] | Publicly-contributed family trees, for confirming a relationship across generations (surname + approximate dates matching a relative already confirmed elsewhere). User-contributed, not an authoritative registry — a name+surname match can land on a wholly unrelated family from centuries ago. See the hedge in `01-people.md`'s full-name anchoring steps; never cite a hit standalone. |

## Phone

| Tool | Tag | Use |
|---|---|---|
| PhoneInfoga | [cli] | Footprint a number: carrier, region, type, then dorks for the literal number. |
| Ignorant | [cli] | Phone equivalent of holehe: checks a number against each supported platform's signup/recovery endpoint for a registered account (Instagram, Snapchat, Amazon confirmed — `pip install ignorant`, then `ignorant <country code> <national number>`, e.g. `ignorant +33 612345678`). Endpoints change without notice; a negative hit is weaker evidence than a positive one. Observed live: the Snapchat check came back rate-limited on three separate runs in a row, not just an occasional miss — treat a Snapchat result as unreliable right now rather than a confirmed negative. Confirming existence this way is quiet; going further to identify *which* account by walking the platform's own password-reset UI is a separate, louder step — see `00-operational-footprint.md`. |
| libphonenumber-based validators | [web] | Format/carrier/region from the country and area code. |
| Truecaller, Sync.me | [web] | Name lookup by number (account/app-gated; can expose your account to the target, see `00-operational-footprint.md`). |
| PagesJaunes.fr ("particuliers" tab) | [web] | France: the other direction — name + city → listed landline/address, when the person hasn't opted out. Distinct from the reverse (phone → name) lookup above. Both of PagesJaunes' own lookup pages gate direct/automated-looking access behind a Cloudflare challenge — don't attempt to solve it; a search-engine snippet of the same page is the practical workaround. |
| HIBP (phone) | — | **Dead as a free-web lookup**: HIBP's public site dropped phone/username search entirely as of "HIBP 2.0" (May 2025) — email only now (verified live: the search box rejects a phone number as invalid). Use DeHashed / LeakCheck / Snusbase (paid) for a phone-number breach check instead. |

---

## Breach / leak / paste

| Tool | Tag | Use |
|---|---|---|
| Have I Been Pwned | [web] | Free, authoritative breach index by email/phone. |
| DeHashed, LeakCheck, Snusbase | [web] | Paid, deeper fields. See `05-breaches.md`. |
| IntelX | [web] | Pastes, leaks, darkweb selectors. |
| Dorks on paste sites | [web] | `site:pastebin.com "target.com"`, plus gist, ghostbin, etc. |

These indices answer "was this exposed," which is almost always all you need — see `05-breaches.md`.

---

## Search / dorking / aggregation

| Tool | Tag | Use |
|---|---|---|
| Google, Bing, Yandex, DuckDuckGo, Brave | [web] | Core dorking. Cross-engine always. See `07-dorks-and-search.md`. |
| Intelligence X | [web] | Selector search across leaks/darkweb/historical. |
| Google CSE (custom search engines) | [web] | Pre-scoped searches across curated source sets (e.g. webcam catalogs, mastodon instances). |
| SpiderFoot | [cli] | Automation that orchestrates many of the above modules. Heavyweight; use when a run justifies it. |
| recon-ng | [cli] | Modular recon framework for repeatable, scripted collection. |

---

## Visualization / case management

| Tool | Tag | Use |
|---|---|---|
| Maltego (CE) | [cli] | Link-graph of entities and relationships. Good for presenting a network. |
| Obsidian / plain Markdown | [web] | Lightweight case notes with backlinks; often enough. |
| draw.io, yEd | [web] | Manual relationship diagrams for a dossier. |

---

## Sock puppets / collection identity

Account-gated platforms (LinkedIn, Facebook, Instagram, some forums) reveal little to logged-out viewers and fingerprint logged-in ones, so a research persona is often needed. The discipline matters more than any generator: aged accounts (a fresh one gets flagged and burned), one persona per operation (cross-contamination links your activity together), consistent fingerprint (same device profile, egress region, locale, cadence), and never on a device or IP tied to you. Viewing is quieter than interacting: following, liking, or messaging writes to the target's notifications. This skill does not automate account creation.

---

## Catch-all / discovery (when nothing above fits)

This file names concrete tools deliberately, not every tool that exists — see the "pivots, not lists" philosophy in `SKILL.md`. When a task genuinely needs a tool/source this catalog doesn't name (an unusual data type, a platform not covered, a country-specific niche), reach for a live-maintained index instead of guessing:

| Resource | Use |
|---|---|
| OSINT Framework (osintframework.com) | Interactive tree of tools by data type (email, username, domain, IP, image, person...). Fastest way to see what exists for a data type this skill's own pivot trees don't cover. |
| Awesome OSINT (GitHub) | Large categorized tool list. Good for a specialized/niche category (a specific platform, a specific country) where the mainstream tools above come up empty. |
| Bellingcat Online Investigation Toolkit | Curated, actively maintained, with each tool's limits noted — strongest specifically for geolocation and image/video verification; its dedicated Maps & Geolocation and Image & Video Verification sub-pages are worth checking before extending `06-geolocation.md`'s own tool list. |

Same rule as everywhere else in this skill: whatever one of these helps you find, anchor the finding on the underlying primary source (the registry, the platform, the original image), not on the directory that pointed you there — and if it's a source worth using again, add it to the relevant file here or in `references-by-region.md` rather than re-discovering it next time.