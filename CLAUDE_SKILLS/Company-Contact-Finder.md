---
name: company-contact-finder
description: >
  Find published contact email addresses for one or more companies by combining a web search with a crawl of each company's official website, plus optional security.txt, document dorks, 
  certificate transparency, RDAP/WHOIS and official business registers. Given a list of company names (or a single name), it returns the contact emails it can find, grouped per company. 
  Use this whenever the task involves collecting, looking up, or compiling contact emails / points of contact for companies, whether the request arrives from a user, another skill, 
  or a calling script, and whether the companies are Polish or anywhere else. 
  Intended for legitimate use (sales, recruiting, authorized security recon, journalism); respects robots.txt and rate-limits requests. 
---


# Company Contact Finder

This skill is a method for finding the contact emails a company publishes, plus a
reference implementation of that method as a Node.js script. Read the method first.
You can follow it by hand, with another tool, or via a browser; the script is just one
way to execute it. The script is documented in the second half.

The data targeted is what companies publish on purpose (role mailboxes like
`contact@`, `kontakt@`, `careers@`, `security@`, imprint and team pages, addresses in
public documents). This is standard OSINT / prospecting work. Keep it to legitimate
purposes, respect robots.txt, and don't use the output for spam or harassment.

One boundary worth stating plainly: this collects addresses. Generating or mass-validating employees' unpublished addresses (email permutation, SMTP probing) is a
different activity that mainly serves bulk cold-mail and spear-phishing, and it is out
of scope here. For security contact, a published `security@` or a `security.txt` entry
is both more correct and more effective than guessing a person's address.

---

# Part 1: The method

## Step order

1. **Web search.** Query the company name with a contact keyword and pull emails out of
   result snippets and `mailto:` links. Cheap, and it also surfaces candidate URLs for
   the next step.
2. **Detect the official site.** Score the result domains: the name appearing in the
   domain is a strong signal, aggregators and socials are disqualified. Pick the best.
3. **Crawl the official site.** Visit contact / about / team / imprint pages first, then
   follow internal links to a shallow depth. This is the cleanest source because every
   hit sits on the company's own domain.
4. **Harvest emails from every page**, decoding common obfuscations (`name [at] domain
   [dot] com`, HTML entities) so lightly-disguised addresses are still caught.
5. **Widen with the deeper modules** below to double-check and enlarge the results, not only when the easy sources come up short.
6. **Merge and tag by source.** Keep addresses found on the official domain separate
   from search-only hits, so the high-trust set is obvious.

## Judging reliability

- Addresses **on the official domain** (from the crawl, security.txt, or a domain-scoped
  dork) are high trust.
- Addresses seen **only in search results** are leads: verify before use, since snippets
  pull in neighbouring and unrelated addresses.
- **Role mailboxes** (`contact@`, `security@`, `press@`) are safer to use and to keep
  than **named individuals'** addresses, which are real but more sensitive. Flag the
  latter and don't bulk-compile them without a legitimate basis.

## Pacing and rate-limits

Be a good citizen with the search engines, both because it is the right thing to do and
because hammering them gets the scraper IP-banned (which makes results worse, not
better). The method paces itself: a base pause with random jitter between every search
request, and an exponential backoff (30s, 60s, 120s, capped at 3 min, then give up the
phase) whenever an engine returns a 429/503 or an anti-bot page. The base pause is
tunable via `--delay`. If a whole run comes back empty with rate-limit messages in the
logs, wait and rerun later, or pass `--site` to skip the search phase entirely once the
domain is known.

## The deeper modules and their fallbacks

Each external source can be slow or down (crt.sh notably so). For each one there is a
primary and at least one no-key fallback, so the method degrades gracefully.

### a) security.txt

The single highest-value source for a security or bug-bounty contact: the address the
company *wants* researchers to use, published under RFC 9116.

- Primary: `https://<domain>/.well-known/security.txt`
- Fallback: `https://<domain>/security.txt` (older location)

### b) Document dorks

Search-engine queries scoped to the domain that surface addresses published in files
(annual reports, press kits, decks) and on third-party pages, not just on the site.

- Query forms: `site:<domain> "@<domain>"`, and an `intext:"@<domain>"` query across
  `filetype:pdf OR docx OR xlsx OR pptx OR txt OR csv OR odt`
- Note: snippet text alone only catches addresses visible in the preview. To get
  addresses inside the files, the files must be fetched and their text extracted (the
  docx / pdf / xlsx skills in this environment handle that). Treat full extraction as an
  opt-in heavier pass.

### c) Certificate transparency (subdomain discovery)

CT logs list every TLS certificate issued for a domain, revealing subdomains
(`careers.`, `press.`, `investors.`, `security.`) that often have their own contact
pages worth crawling.

- Primary: crt.sh, `https://crt.sh/?q=%25.<domain>&output=json`
- Fallback 1: Certspotter, `https://api.certspotter.com/v1/issuances?domain=<domain>&include_subdomains=true&expand=dns_names` (free, no key, verified working)
- Fallback 2: HackerTarget, `https://api.hackertarget.com/hostsearch/?q=<domain>` (free, no key; plain-text subdomains, one per line with IP; daily per-IP quota)
- Fallback 3: RapidDNS, `https://rapiddns.io/subdomain/<domain>?full=1` (free, no key; HTML page to scrape, fuller but heavier to parse)

### d) Web search engine

- Primary: Google
- Fallback: DuckDuckGo HTML, `https://html.duckduckgo.com/html/?q=<query>` (no key,
  tolerant of scraping)
- Secondary mention: Marginalia, `https://search.marginalia.nu` (niche, text-first)

### e) Official business registers

For company-level contacts (registered address, sometimes an admin email) when the web
sources are empty. No single API spans all countries, so use a directory that links
through to each national registry, then fetch the right one for the company. This is a
manual step, since registry formats and access rules vary too much to crawl blindly.

- Primary directory: OpenCorporates, `https://opencorporates.com/registers` (170+
  jurisdictions, each linking to the primary registry)
- Fallback directories: Wikipedia "List of official business registers" (by country);
  UK Companies House "overseas registries" list
- Direct national examples (all no-key for basic search): KRS (Poland), Companies House
  `https://find-and-update.company-information.service.gov.uk` (UK), BRIS via
  `https://e-justice.europa.eu` (EU), Handelsregister (Germany), etc.

### f) RDAP / WHOIS

Domain registration data sometimes exposes an abuse or admin contact.

- Primary: `https://rdap.org/domain/<domain>` (redirects to the registry's RDAP)
- Caveat: reliable for gTLDs (.com, .net, .org) but lacking for many European ccTLDs
  (.de returns nothing useful for example), and corporate records are often GDPR-redacted.
  Treat any hit as a bonus, not a dependable module. The no-key alternatives push toward paid accounts, so there is no strong free fallback here.

---

# Part 2: The reference implementation

The method above is implemented in `scripts/contact-finder.js`. If you use the script,
call it rather than reimplementing the steps inline.

## Prerequisites

Node.js (v18+ for the built-in `fetch` used by the CT and RDAP modules) + Puppeteer.

```bash
node --version            # v18 or newer
npm ls puppeteer 2>/dev/null || npm install puppeteer
```

The Chromium that ships with Puppeteer is enough. On Linux, the launch flags
`--no-sandbox --disable-setuid-sandbox` are already set in the script.

## Run it per company

```bash
node scripts/contact-finder.js "Company Name" [flags]
```

Each run prints one machine-readable line to stdout:

```
CONTACT_RESULT:{"company":"...","official_site":"...","emails":[...],"from_site":[...],"from_search":[...],"security_txt":[...],"placeholders":[...]}
```

- `emails`: all addresses kept after noise filtering
- `from_site`: subset on the official domain (highest confidence)
- `from_search`: subset seen only in search results (verify before use)
- `security_txt`: security contacts from RFC 9116, if the module ran
- `placeholders`: likely-template addresses (`john.doe@`, `first.last@`), kept separate
- `official_site`: the detected site, or `null` if none scored high enough

## Flags

| Flag | Default | What it does |
|------|---------|--------------|
| `--google-pages N` | 5 | Search result pages to scrape (DuckDuckGo fallback is automatic) |
| `--delay MS` | 2500 | Base pause between search requests, with random jitter on top |
| `--official-top-n N` | 10 | Look for the official site among the first N result domains |
| `--crawl-depth D` | 2 | Link-following depth on the official site (0 = seed pages only) |
| `--max-pages P` | 25 | Hard cap on pages crawled per company |
| `--subdomains` | off | Also follow subdomains while crawling |
| `--site URL` | | Skip detection and crawl this exact site |
| `--security-txt` | on | Parse security.txt (turn off with `--security-txt false`) |
| `--dorks` | off | Run domain-scoped document dorks after the site is found |
| `--crtsh` | off | Discover subdomains via CT (crt.sh, Certspotter fallback) and crawl the useful ones |
| `--rdap` | off | Look up RDAP/WHOIS registration contact |

Start light (`--google-pages 3 --max-pages 12`) for a quick pass; turn on
`--dorks --crtsh --rdap` for a deep pass on high-priority targets. If a company comes
back with `official_site: null`, rerun with a sharper name or pass `--site` directly.

## Run a batch

```bash
node scripts/run-batch.js companies.txt
# One company name per line

node scripts/run-batch.js "Comarch" "Allegro" "CD Projekt"
# Names inline
```

It writes `contacts.md` and `contacts.json`. The per-company timeout and default flags
are editable at the top of that file.

## Output format

```
Company1 => {address1 ; address2 ; ...}
Company2 => {address1}
CompanyWithNothingFound => {}
```

Placeholders are excluded by default. If they are wanted, note them separately rather
than mixing them in.

## Files

- `scripts/contact-finder.js`: the pipeline (search + detect + crawl + security.txt +
  optional dorks / CT / RDAP + merge)
- `scripts/run-batch.js`: loops over a list and writes `contacts.md` / `contacts.json`
