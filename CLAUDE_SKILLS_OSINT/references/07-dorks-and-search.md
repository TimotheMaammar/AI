# 07: Dorks and Search

Almost every pivot in this skill starts with a query. A well-built search-operator query (a "dork") routinely replaces an entire tool, and costs nothing. Load this file early in any investigation, and come back to it whenever a branch says "search for X" without specifying how.

---

## Core operators (Google-syntax; most work on Bing/DuckDuckGo/Brave too, see engine notes below)

| Operator | Effect | Example |
|---|---|---|
| `"exact phrase"` | Exact match, no stemming/reordering | `"Jean Dupont" "Société X"` |
| `site:` | Restrict to a domain/subdomain | `site:linkedin.com/in "Jean Dupont"` |
| `-site:` | Exclude a domain | `"Jean Dupont" -site:linkedin.com` |
| `filetype:` | Restrict to a file extension | `site:target.com filetype:pdf` |
| `intitle:` | Term appears in the page title | `intitle:"index of" target.com` |
| `inurl:` | Term appears in the URL | `inurl:admin site:target.com` |
| `intext:` | Term appears in the body (useful combined with others) | `intext:"confidential" filetype:pdf site:target.com` |
| `related:` | Sites the engine considers similar | `related:target.com` |
| `cache:` | Engine's cached copy (mostly dead on Google now; use Bing or archive.today) | `cache:target.com` |
| `OR` / `|` | Either term | `"CEO" OR "fondateur" "Société X"` |
| `-term` | Exclude a term | `"Jean Dupont" -actor -musician` |
| `*` | Wildcard, any word(s) | `"Jean * Dupont"` |
| `AROUND(n)` (Bing) | Terms within n words of each other | `Jean AROUND(3) Dupont` |
| `before:` / `after:` (Google) | Date-bound results | `"Société X" after:2023-01-01` |
| `numrange` / `1234..5678` | Numeric range (good for ID/reference numbers) | `"facture" 1000..2000 site:target.com` |

**Combine operators freely** — the leverage is in the combination, not any single one. `site:target.com filetype:pdf intext:"confidential"` is far more precise than any of the three alone.

---

## Per-target-type dork recipes

### Person
```
"Firstname Lastname"
"Firstname Lastname" "City"
"Firstname Lastname" "Employer"
"Firstname Lastname" filetype:pdf          — CVs, minutes, member lists, academic papers
"Firstname Lastname" filetype:pptx OR filetype:docx
site:linkedin.com/in "Firstname Lastname" "Job Title"
"Firstname Lastname" site:facebook.com OR site:instagram.com
"Firstname Lastname" intitle:"obituary"    — confirm alive/not a namesake collision
"Firstname Lastname" -site:linkedin.com -site:facebook.com   — strip the obvious, surface the rest
```

### Email
```
"target@domain.com"
"target@domain.com" -site:domain.com
site:pastebin.com "target@domain.com"
"target@domain.com" filetype:pdf OR filetype:xlsx
```

### Company / organization
```
"Company Name" site:linkedin.com/company
"Company Name" "SIREN" OR "SIRET"
"Company Name" filetype:pdf intext:"rapport annuel" OR intext:"annual report"
site:target.com filetype:pdf                — leaked/published internal documents
"Company Name" intitle:"index of"
related:target.com
"Company Name" -site:target.com             — third-party mentions, press, reviews
```

### Domain / infrastructure
```
site:target.com filetype:pdf OR filetype:docx OR filetype:xlsx
site:target.com inurl:admin OR inurl:login OR inurl:wp-admin
site:target.com intitle:"index of"
site:pastebin.com "target.com"
"target.com" site:github.com                — code referencing the domain, possible leaked endpoints/keys
intext:"target.com" filetype:env            — rare but devastating when it hits
```

### Image / file provenance
```
"exact-filename.jpg"
intext:"photo credit" "exact description of scene"
site:instagram.com OR site:facebook.com "distinctive caption text"
```

### Documents and metadata at scale
```
site:target.com filetype:pdf
site:target.com filetype:doc OR filetype:docx
site:target.com filetype:xls OR filetype:xlsx
site:target.com filetype:ppt OR filetype:pptx
```
Every hit is a candidate for a metadata pull (author, software, sometimes a username/internal path in `Author`/`Company`/`LastSavedBy` fields) — `exiftool` reads Office/PDF metadata the same way it reads image EXIF.

---

## GitHub code search (beyond `site:github.com`)

GitHub's own code search supports a `language:` qualifier and genuine regex search (wrap the pattern in slashes), on top of the generic dork above — worth knowing the actual syntax rather than only dorking it from an external engine:

```
"api_key" language:Python                    — scope by language
org:target-org "password"                    — scope to an org's repos
/AKIA[0-9A-Z]{16}/                            — regex search for an AWS access-key-ID shape
repo:owner/name /secret[_-]?key/i             — regex scoped to one repo
```
A bare unqualified term matches file content or the file path, so a filename guess works too. This is the concrete follow-through on `05-breaches.md`'s observation that GitHub is a frequent accidental-leak source — that file names the risk, this is the query syntax to act on it.

---

## Shodan / Censys query syntax (beyond the IP/domain lookup)

The infrastructure files point to Shodan/Censys as tools; these are concrete query patterns worth having on hand rather than only using the plain search box:

```
ssl.cert.subject.cn:"domain.com"              — subdomains via issued certs, complements crt.sh (03-infrastructure.md)
org:"Company Name"                            — every host Shodan attributes to an org
http.title:"text" port:8080                   — exposed services/dashboards by page title + port
http.favicon.hash:<value>                     — same-icon hosts, see the favicon-pivot note in 03-infrastructure.md
ssl.jarm:<value>                              — same-TLS-fingerprint hosts, see 03-infrastructure.md
```
Only `ssl.cert.subject.cn` (the certificate's common name) is confirmed as a field — don't assume a `.subject.org` equivalent exists without checking Shodan's own syntax reference first.

---

## Engine comparison — always cross-engine

No single engine indexes everything; a target-relevant page can be indexed by one and not another. Run the same dork across at least two engines when a search matters.

| Engine | Strength |
|---|---|
| Google | Largest general index, richest operator support, best `filetype:`/`site:` precision. |
| Bing | Different crawl, sometimes surfaces what Google has deprioritized; supports `AROUND(n)` proximity; still has a usable cache. |
| Yandex | Different index entirely, strong in Russian/CIS-language content. Also a strong reverse-image option for several use cases (faces, non-Western/Cyrillic content) — see the engine-selection table in `06-geolocation.md` rather than defaulting to it for every image. Worth a text-search pass even for non-Russian targets. |
| DuckDuckGo | Bing-backed results with its own ranking; occasionally cleaner for a straightforward query, supports most of the same operators. |
| Brave Search | Independent index, worth a cross-check, especially post-2022 content. |
| Baidu | Essential, not optional, for China-related targets — different web entirely from the above. |

---

## Google Custom Search Engines (CSEs)

Pre-scoped search engines built by third parties to search a curated set of sites — faster and cleaner than hand-building a long `OR` chain of `site:` operators. Search for an existing public CSE before building your own query: common ones cover things like webcam directories, specific document-sharing platforms, Mastodon/fediverse instances, or a curated list of leak-paste sites. If nothing existing fits and the same scoped search will be needed repeatedly, Google's own CSE builder lets you create one from a site list in a few minutes.

---

## Reverse / "find where this came from" search

Not a text dork, but the same first-move instinct applies to non-text seeds:
- **Image** → `06-geolocation.md` (Yandex/Google Lens/TinEye/Bing Visual, by use case).
- **Exact phrase that might be a quote, a leaked line, or copied boilerplate text** → search it in quotes to find every other place it's been published; identical boilerplate across "unrelated" sites is a strong same-owner/same-template signal (useful in `03-infrastructure.md`).
- **A document** → search a distinctive sentence or an unusual header/footer string from it in quotes to find other copies or the original source.

---

## Search hygiene

- **An abstracted search tool is not the same thing as the engine it's wrapping — this is the search-specific case of the skill-wide "don't stay in the sandbox" rule (see `SKILL.md`'s philosophy).** A summarizing/API-based search tool (including Claude's own web-search tool) can return a thin or empty result for a query that the same engine, typed directly into a real browser tab, answers immediately and richly — observed directly: an exact-phrase name query came back with nothing relevant through an abstracted tool, then surfaced a LinkedIn profile and two newspaper articles the moment it was run as a live Google search in an actual browser. Treat an abstracted tool's "nothing found" as provisional, not as the finding — confirm genuine absence (or catch a false negative) by re-running the same exact-phrase query in a real browser before writing "no footprint" into a dossier. This matters most on a bare name/entity seed, where there's no `site:`/`filetype:` scoping to fall back on.
- **Re-run the exact-phrase trick on every new identifier, not just the original seed.** Each pivot (a username/handle surfaced from one platform, a company name, an employer+name combination, a nickname mentioned in a comment) is itself a fresh seed for the same `"exact phrase"` real-browser search — don't treat the technique as a one-time step spent on the starting name. In practice: find a handle on platform A → quote-search the bare handle → it can surface activity on platforms B and C that the handle's own profile page never links to (a one-line comment under someone else's content, a forum post, a leaked mention) that a name-only search would never catch. Budget this the same way as any other recursive branch (see the per-degree search budget in `01-people.md`) rather than running it to exhaustion on every single identifier — but run it at least once on every identifier that matters to the dossier.
- **Vary phrasing and language.** A French target may be indexed under an accented vs. unaccented name variant, or discussed in English-language coverage with a transliterated spelling.
- **Don't stop at page one.** OSINT-relevant hits (an old forum post, a niche directory listing) are routinely buried past the first page, especially for common names.
- **Re-run periodically on a live investigation.** Indexes change; a page not indexed last week can appear this week, and vice versa for deletions (check the archive sites then).
- **A query is quieter than a tool.** Reading search-engine snippets and cached/archived copies of target-owned pages avoids a direct fetch to the target's own server — see `00-operational-footprint.md`.
- **A site's own search-box typeahead/autocomplete can silently corrupt a query, producing a false "0 results."** Observed twice on the same investigation, on two unrelated French database search tools (theses.fr, then journal-officiel.gouv.fr's association search): loading the page with a pre-filled query (via a `?q=` URL parameter) left stale text in the search box, and typing a fresh query into it appended rather than replaced — submitting a mangled double query (`"Thomas BatisseThomas Batisse"`) that matched nothing, which would read as a clean absence finding if the actual field contents weren't checked. Before trusting a "0 results" or "nothing found" on any site with its own search-suggestion/typeahead behavior, read back what's actually in the query field (or clear it explicitly — select-all + delete, not just typing over — before entering the real query) rather than assuming the box contains only what was just typed.
- **Expect occasional Cloudflare-style bot-check gates on direct navigation to a specific page, beyond the PagesJaunes case already noted in `01-people.md`/`08-tools-catalog.md`.** Observed on two more, unrelated French sites: `hal.science` (an official open-archive research-paper host) and `rugbyamateur.fr` (an amateur-sports stats site) both interstitial-paged a direct navigate to a specific document/player URL with a "checking you're not a robot" screen. This isn't one quirky site, it's a general pattern on French small-to-medium sites behind a common CDN/security layer — don't attempt to solve the challenge (see the hard rule against bypassing bot-detection); the search-engine-snippet workaround that already covers PagesJaunes applies the same way here: the content is usually already indexed and readable from the engine's own result snippet even when the live page is gated.

---

## Common pivots out of this file
- Any dork result pointing at a person/company/domain/image folds into the matching target-type reference (`01` through `03`, `06`).
- A dork returning many pages of the same data shape (not just one answer) → stop hand-copying, use `automation.md`'s headless collector instead.
- Tool shortlist if a dork alone doesn't resolve the question: `references/08-tools-catalog.md`
