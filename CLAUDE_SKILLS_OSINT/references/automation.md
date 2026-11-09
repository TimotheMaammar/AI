# Automation: The Headless Collection Engine

When a dork returns many pages worth harvesting, do not collect by hand. This is a generalized headless-browser collector: **a query drives the search, a regex/rule keeps the matches, a post-processor dedupes and exports.** It is the engine; the dork (`07-dorks-and-search.md`) is the input, and the regex is the filter.

The pattern below generalizes a field-tested email harvester. Three things are interchangeable: the **query** (any dork), the **extractor** (any regex or DOM rule), and the **post-processing** (dedupe, normalize, enrich, export). Everything else is plumbing.

---

## When to use it (and when not)

Use it when:
- A dork yields multiple result pages of the same shape of data (emails, usernames, profile URLs, phone numbers, document links, registration numbers).
- You need a deduplicated, exportable set rather than a handful of hand-copied hits.

Do **not** use it when:
- A single query answers the question (just read the results).
- The source is an authoritative registry with its own export (use the registry; do not scrape what you can download cleanly).

Footprint: route the headless browser through non-attributable egress. Search engines rate-limit and serve CAPTCHAs to datacenter IPs and fast cadences, so respect delays and rotate egress. CAPTCHAs and rate limits are signals you are being noticed; back off rather than hammering.

---

## The pattern (three interchangeable parts)

```
for each result page of [QUERY]:
    load page through headless browser (masked, anonymized egress)
    grab innerText + relevant href attributes
    apply [EXTRACTOR regex/rule]  → candidates
    add candidates to a dedup set
post-process the set: normalize, filter false positives, enrich, export
```

### Reference implementation (generalized from the email harvester)

```javascript
const puppeteer = require("puppeteer");
const fs = require("fs");

// ---- CONFIG: the three interchangeable parts -------------------------
const target = process.argv[2];
if (!target) { console.error('Usage: node collect.js "query target"'); process.exit(1); }

const PAGES = 5;
const DELAY_MS = 1500;            // be polite; raise for stealth
const HL = "fr";                  // result language/region

// 1) QUERY: the dork. {t} is the target. Swap freely.
const QUERY = t => `"${t}" adresse mail contact`;

// 2) EXTRACTOR: what to keep. Swap the regex for the data shape you want.
const EXTRACTORS = {
  email:    /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g,
  // see the extractor library below for more
};
const EXTRACTOR = EXTRACTORS.email;

// 3) NORMALIZE: how to clean each hit before dedup.
const normalize = s => s.toLowerCase();
// ---------------------------------------------------------------------

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox",
           "--disable-blink-features=AutomationControlled"],
  });
  const page = await browser.newPage();
  await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36");
  await page.setExtraHTTPHeaders({ "Accept-Language": "fr-FR,fr;q=0.9" });

  const hits = new Set();
  for (let p = 0; p < PAGES; p++) {
    const url = `https://www.google.com/search?q=${encodeURIComponent(QUERY(target))}&start=${p*10}&hl=${HL}`;
    console.log(`page ${p + 1}/${PAGES}`);
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });
    } catch (e) { console.error(`  page ${p+1} failed: ${e.message}`); continue; }

    const text = await page.evaluate(() => {
      const body = document.body.innerText;
      const hrefs = Array.from(document.querySelectorAll("a[href]"))
        .map(a => a.href);
      const mailtos = Array.from(document.querySelectorAll("a[href^='mailto:']"))
        .map(a => a.href.replace("mailto:", ""));
      return [body, hrefs.join(" "), mailtos.join(" ")].join(" ");
    });

    (text.match(EXTRACTOR) || []).forEach(h => hits.add(normalize(h)));
    if (p < PAGES - 1) await new Promise(r => setTimeout(r, DELAY_MS));
  }
  await browser.close();

  const out = [...hits];
  console.log(`\n${out.length} hit(s):\n`);
  out.forEach(h => console.log("  ", h));
  const file = `hits-${target.replace(/\s+/g, "_")}.csv`;
  fs.writeFileSync(file, ["value", ...out].join("\n"));
  console.log(`\nexported -> ${file}`);
})();
```

The structure is deliberately the same as a simple email harvester: masked headless browser, paginated search, `innerText` + `href`/`mailto` extraction, regex match, `Set` dedup, CSV export. The generalization is only that QUERY, EXTRACTOR, and normalize are now first-class knobs.

---

## Extractor library (swap the regex)

| Target data | Regex (starting point) | Notes |
|---|---|---|
| Email | `/[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g` | Filter image/CDN false positives (`@2x.png`). |
| Phone (FR) | `/(?:\+33\s?|0)[1-9](?:[\s.\-]?\d{2}){4}/g` | Normalize to E.164 in post-processing. |
| Phone (intl loose) | `/\+\d{1,3}[\s.\-]?(?:\d[\s.\-]?){6,12}\d/g` | Noisy; corroborate. |
| SIREN (FR) | `/\b\d{3}[\s ]?\d{3}[\s ]?\d{3}\b/g` | Validate with the Luhn check before trusting. |
| SIRET (FR) | `/\b\d{3}[\s ]?\d{3}[\s ]?\d{3}[\s ]?\d{5}\b/g` | Luhn-checkable too. |
| IBAN | `/\b[A-Z]{2}\d{2}(?:[\s ]?[A-Z0-9]{4}){2,8}[\s ]?[A-Z0-9]{1,4}\b/g` | Often a strong identifier; validate the checksum before trusting. |
| Username/handle | `/@[A-Za-z0-9_]{2,30}\b/g` | Platform-dependent; refine per network. |
| Profile URLs | `/https?:\/\/(?:www\.)?(?:linkedin\.com\/in|twitter\.com|x\.com|github\.com|instagram\.com)\/[A-Za-z0-9_\-.\/]+/g` | Pivot list for socmint. |
| Bitcoin address | `/\b(?:bc1[a-z0-9]{20,80}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b/g` | For crypto/threat-intel pivots. |
| Document links | `/https?:\/\/\S+\.(?:pdf|docx?|xlsx?|pptx?|csv)\b/gi` | Feed into a metadata-extraction pass. |

Always add a false-positive filter in post-processing. Regexes over-match; a quick sanity filter (valid TLD, Luhn check, plausible length) raises the signal sharply.

---

## Variations on the engine

- **Different search source.** Swap the Google URL for Bing (`https://www.bing.com/search?q=...&first=N`) or a site's own search. Cross-engine harvesting catches different hits.
- **Archive-driven instead of search-driven: Waymore [cli].** Same dedup/export shape as the pattern above, but the query source is the Wayback Machine's CDX API (plus a few other archive sources) rather than a live search engine — it pulls every historically captured URL for a domain, recovering old pages/posts a live search won't surface (deleted forum posts, old blog entries tied to a leaked email). Pairs with the CDX-API note in `03-infrastructure.md`.
- **Per-platform DOM rule instead of regex.** For a structured page (a directory, a registry listing), replace the regex match with a DOM selector inside `page.evaluate` (e.g. pull every `.result-card .name` + `.result-card .email`). Rule beats regex when the page is structured.
- **Two-stage enrich.** First pass harvests profile URLs; second pass visits each URL and extracts deeper fields. Keep the politeness delay and egress discipline on the second pass too (it hits real sites, not just search).
- **Stealth hardening.** When a target fingerprints aggressively: `puppeteer-extra` + `stealth` plugin, randomized viewport and cadence, rotating residential egress per session, and a longer `DELAY_MS`. Datacenter IPs get flagged fastest; residential/mobile egress lasts longer.

---

## Operational notes

- When a direct fetch hits a target-owned page, your IP and user agent can land in their logs. For target-owned pages prefer search snippets, caches, and archives; reserve direct fetches for neutral third parties.
- Authenticating the collector to a platform makes the activity attributable to that account, and some platforms surface viewers or notify owners (see `00-operational-footprint.md`).
- Prefer an official export or API over scraping whenever the source offers one cleanly: faster, structured, and quieter.
- Keep raw harvested output (CSVs, dumps) separate from the finished report; drop it in `Annexes/` if it is worth keeping.
