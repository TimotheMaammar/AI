# 01: People

Pivoting on a person. Seed is typically a name, an email, a username, or a phone number. The goal is an identity card plus the surrounding graph (employer, relations, locations, accounts), each fact rated with the NATO Admiralty code (source letter + credibility digit, see SKILL.md).

The pivot tree below is transcribed from a field-tested mind map. Read it as: from the central node PERSON, each branch is a pivot, and each pivot opens onto further pivots. Follow the branches that serve the current target; in exhaustive mode you walk all of them unless a branch is plainly irrelevant.

Most branches below produce facts (an address, a filing, an employer) that are rated and done. A few produce an **identity-binding claim** instead — "this account is this person", "this namesake is the target and not a homonym" — and those are a different kind of claim: a correlation across weak signals, not a direct observation. Treat them with the same discipline `02-companies.md`, `03-infrastructure.md`, `04-socmint.md`, and `06-geolocation.md` apply to their own correlated claims: never state a binding as settled on one signal, state the confidence level explicitly, and keep the alternative (wrong namesake, coincidental photo reuse, shared pseudonym) visible rather than silently discarded. See "Identity-binding discipline" below.

---

## Pivot tree: PERSON

```
PERSON
├── name search
│   ├── files (pdf, doc, ...) ──► companies / meeting minutes (named in them)
│   ├── images ──► reverse image  (see 06-geolocation.md)
│   └── blogs, articles, mentions
│
├── company director / officer, or association officer  (check both actively, by name — don't wait until you already know; see the "dirigeant"/association searches below)
│   ├── website ──► legal/company notice ──► domain name
│   │                                        ├── registrant / contact (whois)
│   │                                        └── other domains by same registrant
│   ├── postal address ──► land registry / property records
│   ├── home address
│   ├── articles of association / bylaws (name the officers)
│   ├── other directorships / shareholdings
│   ├── associates / co-officers ──► pivot each as a new PERSON
│   └── establishment history (where the company has operated)
│
├── civil-status data (vital records)
│   ├── date and place of birth
│   └── domicile  ◄──► land registry / property records
│
├── land registry / property records
│   ├── domicile
│   └── date/place of birth (sometimes recorded)
│
├── pseudonym / username search ──► social-media accounts  (see 04-socmint.md)
│
├── email search
│   ├── data-breach exposure  (see 05-breaches.md)
│   └── social accounts tied to the address  (see 04-socmint.md)
│
├── social-media accounts
│   ├── reverse-image the profile photo ──► candidate link to other accounts / real identity (corroborate, see below)
│   └── profile analysis
│       ├── content + dates (activity pattern, timezone, habits)
│       ├── relations (friends, follows, frequent interactions)
│       ├── geolocation (check-ins, backgrounds, metadata)
│       └── profile photo ──► reverse image
│
└── local press
    ├── photos ──► reverse image
    └── articles (named mentions, life events, affiliations)
```

Two structural points worth internalizing from this tree:
- **The director branch turns a person into a company investigation** (and `02-companies.md` turns a company back into its people). People and companies are one graph; cross between `01` and `02` freely.
- **The profile photo is a hub.** Reverse-imaging it bridges from one account to others and sometimes to the real identity behind a pseudonym. It is one of the strongest single pivots for a person.

---

## Anchoring by seed type

### Seed = full name
1. Disambiguate first (city, employer, age, the reason for the inquiry). A name alone is rarely a target — common names routinely collide with homonyms, and a dossier built on the wrong namesake is worse than no dossier. Carry at least one discriminator through every subsequent step, not just the first query. **When the first survey pass turns up not one plausible target plus noise, but three or more clearly distinct real people (different employers, cities, photos — not just different pages about the same person), stop: do not expand any single one of them.** Observed directly on a bare, no-discriminator seed: one exact-phrase search plus one `site:linkedin.com/in` dork surfaced upward of ten genuinely distinct "Thomas Batisse"s in minutes — a PhD student in Clermont-Ferrand, a notarial formaliste in Annecy, two unrelated géomètres-topographes in different regions, a Lyon recruiter, a Lyon warehouse-worker/student, a multi-brand sales rep, a Netherlands-based gaming-company employee, a rugby player, a motocross rider, and an Instagram account — with no two sharing enough to merge and nothing in the request to prefer one over another. In that situation, do the cheap survey pass only (one line per candidate: name variant, the one or two cheapest-to-get facts — job/employer, city, a source link — no further expansion, no breach/phone/company pivots on any of them), present the roster, and ask which one is the actual target rather than guessing from prominence (most followers, most press, richest profile) or silently picking the first result.
2. Exact-match dorks: `"firstname lastname"` plus a discriminator (`"firstname lastname" "city"`, `"firstname lastname" "employer"`). **Run this through an actual browser on live Google, not only through an abstracted/API-based search tool.** The two can disagree sharply: a bare `"firstname lastname"` query through a summarizing search tool can come back empty while the identical query typed into a real Google search tab surfaces a LinkedIn profile, regional press coverage, and a YouTube channel on the first page. Don't conclude "no footprint" (absence) from one search method alone — before writing that down as a finding, re-run the exact phrase in a real browser tab (Claude in Chrome or the built-in browser). This is the single highest-leverage check in the whole file: it's the difference between a dossier and a false negative.
3. Name in documents: `"firstname lastname" filetype:pdf` (CVs, minutes, member lists, academic papers).
4. Name across social platforms (see socmint) and local press.
5. **Reverse "dirigeant" search (companies) — run this on every name, not only when a directorship already looks plausible.** France's company registries let you search by *person name* and get back every company where they're listed as an officer/director/beneficial owner, which is the only way to discover an affiliation you didn't already know about: **Pappers** (pappers.fr/recherche?q=firstname+lastname, or pappers.fr/dirigeant/ for a direct person lookup), **Societe.com** (societe.com's own "recherche dirigeant" field, separate from its company-name search), **Infogreffe** (infogreffe.fr, dirigeant search), **BODACC** (bodacc.fr — searching a person's name surfaces legal announcements naming them: incorporations, officer changes, insolvency filings). Run at least Pappers' dirigeant search as a default step for any French person seed — a hit here (an auto-entrepreneur registration, a family SCI/GFA holding land, a sibling or relative listed in the same entity) is routinely the richest single finding in the whole file, and it's invisible to every other branch here. **Once you have a hit, scan the entity's full officer/associate list for the target's own surname** — see `02-companies.md`'s "Officers and beneficial owners" step for why this matters and how to rate what it turns up. See `references-by-region.md` for the equivalent registries outside France.
6. **Reverse officer search (associations) — the same move, for the nonprofit world, which the company registries above don't cover at all.** A French *association loi 1901* (the legal form behind essentially every local sports club, cultural group, or hobby association) has to declare its officers (président, trésorier, secrétaire) to the state when created or changed, searchable by person name via the **RNA / Répertoire National des Associations** (data.gouv.fr/associations, or the Journal Officiel's own "Associations" search at journal-officiel.gouv.fr/pages/associations-recherche). This is exactly the branch that surfaces a target's role in a football club, a music/cultural association, a parents' association, or a local charity — the kind of affiliation that never shows up in a company registry and is easy to miss entirely if you only run the dirigeant search above.
7. **Name + city in a white-pages lookup — the classic starting move, worth running even now.** Pages Blanches / PagesJaunes' own "particuliers" tab (pagesjaunes.fr, filtered to individuals rather than businesses) resolves a name + city to a listed landline number and address when the person hasn't opted out — distinct from the *reverse* phone-to-name lookup covered under the phone-seed section below. Listing rates have dropped as mobile replaces landlines, so a miss here isn't informative, but a hit is a fast, free, primary-ish source for an address.
8. **Genealogy sites, with real care.** Geneanet (and similar: Filae, GeneaNet's own indexed trees) hold enormous volumes of publicly-contributed French family trees, useful for confirming a family relationship (surname + approximate dates matching an already-known relative) across generations — but these are user-contributed trees, not an authoritative registry, and a name+surname match can land on a *completely unrelated family* from centuries ago that happens to share both names (observed directly: a "Henri Boucher" and a "Quentin Gobinet" surfaced together in one such tree purely by 17th-18th-century coincidence, with zero connection to either actual target). Treat a Geneanet hit as a lead requiring corroboration against a fact you already hold independently (a shared relative's name and approximate birth year you already confirmed elsewhere) — never cite it as a standalone source for a modern identity claim.
9. **Three more name-searchable public registries, each covering a slice the ones above miss entirely** (steps 5, 6, and this one are all France-specific by example — for a non-French target, don't assume these exact tools apply: see `references-by-region.md`'s "what to do when a country isn't listed" for the discovery method and the few genuinely cross-country options, e.g. Wikidata for elected officials):
   - **Elected office.** The **RNE (Répertoire National des Élus)**, published as open data on data.gouv.fr, lists every French mayor, municipal/departmental/regional councillor, MP, and senator. **In practice this isn't a name-search box: data.gouv.fr serves it as twelve separate CSV downloads (one per mandate type, the largest tens of MB), with no web search UI of its own.** For a one-off lookup, a front-end built on top of it (e.g. **Civiqo**, civiqo.fr) gets you to the right row in seconds and is worth using as the first move — but it's then a B-rated aggregator repackaging an A-rated source, not the source itself; climb back to the raw RNE CSV (filter it locally — grep, a spreadsheet, a CSV-aware tool) to confirm before resting an important claim on it. A hit confirms local political involvement that nothing else in this file surfaces. One more caveat specific to this registry: its **profession field uses INSEE's PCS 2003 classification** — coarse, fixed buckets a candidate picks from at registration, not free text — so a bucket like "professeur des écoles, instituteur et assimilé" can be the closest available category for a job that isn't literally that (a private art-school teacher, say) rather than a literal job title; don't over-read it without corroboration.
   - **Registered tradespeople.** The **Répertoire des Métiers / Chambre de Métiers et de l'Artisanat** registration — Pappers' own "Artisans" tab searches this directly — covers craftspeople (plumbers, electricians, hairdressers, and similar trades) who register differently from a company "dirigeant" even when self-employed.
   - **Public-sector concours and nominations.** The **JORF** (Journal Officiel, via legifrance.gouv.fr's own search) publishes civil-service entrance-exam (concours) admissibility/admission lists by name, plus nomination decrees for civil servants, magistrates, and military officers — a name hit here is a solid confirmation of public-sector employment or a specific qualification, something a LinkedIn profile alone can't verify independently.
10. Reverse-image any photos found to bridge toward accounts — this corroborates identity, it does not confirm it alone; a visual match is a lead until backed by a second independent signal (shared identifier, mutual confirmation, consistent biographical detail).

### Seed = email
1. Decompose the address: domain (employer or provider) and name pattern (`first.last`). Generalize the pattern to colleagues via Hunter.io and `automation.md`.

**The reverse direction works too.** Starting from a bare name/username and a known employer domain (no email in hand yet), construct a candidate address from the common patterns (`first.last@`, `flast@`, `firstl@` — see the pattern list in `08-tools-catalog.md`) and *verify* it (an SMTP `RCPT TO` probe, a verifier API, or a service like holehe that confirms account existence) rather than only search-engine-dorking for it as literal text — a constructed-but-unverified guess is worthless, but a verified one is as good as a found one.
2. Breach exposure: Have I Been Pwned (free) first; then DeHashed / LeakCheck / IntelX for depth (see `05-breaches.md`). h8mail [cli] automates multi-source breach hunting.
3. Registered-account discovery: holehe [cli] (`holehe target@mail.com --only-used`) and EmailRep.io [web] show which platforms have an account on that address. Note: some checks email the owner (see `00-operational-footprint.md`).
4. If Gmail: GHunt [cli] or its online mirror returns name, profile/cover photos, calendar, maps reviews, timezone. Reverse-image the photos. Epieos [web] (epieos.com) is a broader, passive sweep worth running alongside GHunt rather than instead of it: it checks the address against Google services and dozens of consumer apps at once and returns a confidence-scored list, and for Gmail specifically can surface an activity-timeline estimate (account creation / last-activity) GHunt doesn't give directly. Passive — no login attempt, nothing sent to the owner.
5. Gravatar: `gravatar.com/{md5(email)}.json` may return a profile and avatar → reverse-image it.
6. Search the literal address in quotes across Google/Bing/Yandex and paste sites (`site:pastebin.com "address"`).

### Seed = username / pseudo
Primarily a socmint pivot, go to `04-socmint.md`. Tooling: WhatsMyName [web] or Instant Username Search [web] first, then Sherlock / Maigret [cli] for scripted breadth across 400+ sites. Check the handle across platforms, reverse-image the avatars (Yandex), and read cross-platform consistency (same bio, links, writing style). **Also quote-search the bare handle itself** (`"exact-handle"`, real browser — see `07-dorks-and-search.md`'s "re-run on every new identifier" note) — a handle turns up in places a platform-by-platform check misses: a comment left under someone else's content, a forum post, a mention in an unrelated page.

Cross-platform consistency builds a *hypothesis* that several accounts are the same person — it does not bind them on its own. Writing style and bio overlap can coincide by chance, especially with a common handle pattern; a shared avatar can be a stock image or a widely-reused picture rather than a personal one. Treat the hypothesis as confirmed only once at least one hard link corroborates it (a shared real-world identifier such as an email or phone surfaced in a breach record, a domain registration in whois tying the handle to a name, or an explicit same-person statement by the account holder). Until then, state it in the dossier as "candidate match, [confidence level], corroborated by [signal]" — see "Identity-binding discipline" below — and only then bridge to a real name.

### Seed = phone number
1. Format, carrier, region: PhoneInfoga [cli] or a libphonenumber validator [web]. The country/area code already localizes the person.
2. **Search the number in quotes (with spacing and formatting variants) across engines, classifieds, and paste sites — always keep at least one variant with the full country code (`+33673419145` / `+33 6 73 41 91 45`), not just the bare national-format digits (`0673419145`).** A bare national-format number can collide, digit-for-digit, with a syntactically valid number in a completely different country's own numbering plan — observed directly: a French mobile number's digits stripped of formatting (`0673419145`) matched a Japanese reverse-lookup site's listing for an unrelated Osaka landline (Japan also uses a leading `06` area code, for Osaka), complete with its own spam-call comment thread. The listing even looked superficially plausible (a comment describing an unwanted call) until checking the page's own declared type/region (固定電話/大阪 — landline, Osaka) disconfirmed it. Before crediting any phone-number hit from a country-specific site, check that the site's own locale matches the number's actual country, not just that the digits line up.
3. Registered-account discovery: Ignorant [cli] (github.com/megadose/ignorant) is the phone equivalent of holehe — checks the number against each supported platform's signup/recovery endpoint to detect a registered account (confirmed targets include Instagram, Snapchat, Amazon). Each platform's endpoint can change without notice and silently break detection for that platform, so a negative result there is weaker evidence than a positive one. This is an active, attributable check against a real number (see `00-operational-footprint.md`) — flag it before running it rather than firing it automatically as part of an exhaustive pass.
4. Name lookup: Truecaller / Sync.me [web] (account-gated; can expose your account to the target, see `00-operational-footprint.md`).
5. Messaging-app presence: the number may resolve to a profile name/photo on some apps (querying can notify the owner, see `00-operational-footprint.md`).
6. **Breach exposure: HIBP's public website no longer accepts phone-number search — email only, since "HIBP 2.0" (May 2025) explicitly dropped username/phone search from the free site (confirmed live: the search box now rejects a phone number as invalid input).** The breached-account API may still cover phone numbers for subscribers; on the free web UI, DeHashed / LeakCheck / Snusbase (paid, see `05-breaches.md`) are the practical options for a phone-number breach check now.
7. Reverse-directory services (see `references-by-region.md`) — in France, expect PagesJaunes' own lookup pages (both the "particuliers" white-pages tab and the "annuaire inversé" reverse-phone tool) to gate direct/automated-looking access behind a Cloudflare challenge; don't attempt to solve it. A plain search-engine query for the number often has the same page's content already indexed in a snippet, which is the practical workaround.

---

## Profile analysis (depth on the social branch)

Once you have a confirmed account, mine it as the tree's "profile analysis" branch prescribes:
- **Content + dates.** Posting times reveal timezone and routine; topics reveal interests and habits; life events anchor the timeline.
- **Relations.** Frequent interactions map family, colleagues, close friends, each a pivot and a corroboration source. The relationship graph often survives even when a target locks down their own content (their contacts may not have).
- **Geolocation.** Check-ins, recurring backgrounds, event photos, and (rarely, but check) residual metadata place the person. Cross with `06-geolocation.md`. **A fitness-tracking app's personal activity heatmap (Strava and similar) is its own pattern-of-life pivot**: routes that repeatedly start/stop at the same point are a strong home-address lead, distinct from any single geotagged photo — see the "Crowd-sourced activity data" section of `06-geolocation.md`. (Historical illustration of why this category matters at all: a 2018 Bellingcat/De Correspondent investigation deanonymized thousands of Polar Flow users, including military and intelligence personnel, by reading a public profile's other sessions back to a home address; Polar suspended the feature in response, so that exact flow no longer works, but the same home-clustering logic is why a live, still-public activity heatmap is worth checking today.)
- **Profile + banner photos.** Reverse-image both; people reuse images across accounts, which can bridge identities — but check that the image is personally distinctive first. A stock photo, a default avatar, or a widely-shared meme/corporate headshot will return cross-account "matches" that mean nothing; only a visually distinctive, personally-sourced image makes a reverse-image hit a meaningful signal.

---

## Depth control (set this in cadrage, or the investigation never ends)

The associate/relation branches are recursive: every co-officer, family member, and linked entity is itself a new PERSON or COMPANY to investigate. Without a bound, a run sprawls indefinitely. Fix the depth in cadrage:

- **Degree 0**: the target only. Budget: exhaustive — walk every branch of the pivot tree that applies to this seed.
- **Degree 1**: the target plus directly linked entities and people (their companies, immediate relations, co-officers). The usual default. Budget: a bounded pass per linked entity — identity card plus the top one or two pivots for each (don't recurse a degree-1 entity's own associates further without explicitly promoting it to a subject in its own right).
- **Degree 2**: the above plus the entities/people linked to *those*. Only when the wider network matters (e.g. mapping a corporate web or a relationship cluster). Budget: entity-level only — name, core identifier, one-line role; no independent expansion.

Beyond degree 2, expand selectively and only along branches that serve the operative question, not mechanically. State the chosen degree in the dossier so the reader knows the scope of the graph. When a high-value pivot appears beyond the set depth, note it as a follow-up rather than chasing it immediately. The budget per degree exists for the same reason the degree cap does: without it, "degree 1" quietly becomes "degree 1, but exhaustive on every entity," which is how a bounded investigation turns unbounded without anyone deciding that it should.

## Confidence discipline for people

People-search aggregators (Pipl, Spokeo, BeenVerified, Whitepages, and the like) are tempting and rate poorly on source reliability (typically C or D): treat their output as leads, not facts, and climb to a primary source (registry, official filing, the person's own verified publication) before rating a fact A or B. A wrong address or a conflated namesake asserted as A1 is the classic OSINT failure on people, and it can burn the whole effort downstream.

## Identity-binding discipline

An identity-binding claim ("account X is person Y", "this namesake is the target") is a correlation across signals, not a single observation — rate it differently from an ordinary fact.

**Use the same confidence grid as `02-companies.md`, `03-infrastructure.md`, `04-socmint.md`, and `06-geolocation.md`** (an internal working grid, not a universal scale, kept consistent across the skill so a reader sees the same four levels everywhere a correlation is being judged rather than a direct source):

| Confidence | Criteria |
|---|---|
| **Low** | One weak signal only (style/bio similarity, a reused common avatar, a name match with no discriminator). |
| **Moderate** | Two or more independent signals point the same way, none individually decisive. |
| **High** | A hard link corroborates the binding (shared email/phone from a breach record, matching whois registrant, mutual explicit confirmation, a distinctive personal image matched across accounts). |
| **Inconclusive** | Signals conflict, or there isn't enough to distinguish the target from a plausible alternative (homonym, shared handle, coincidental reuse). |

Never silently round a Low or Moderate binding up to a confirmed fact in the dossier. Corroborate with at least two independent signals before crediting an identity-binding claim above Admiralty credibility 3, and state the confidence level explicitly next to the claim: "candidate match, Moderate, corroborated by [signal]" rather than a bare assertion.

**Record the binding, don't just assert it.** For any identity-binding claim that matters to the dossier, note in the findings section:
- **Claim**: e.g. "linkedin.com/in/x and github.com/y are the same person."
- **Signals used**: each one, individually rated (Admiralty) — e.g. shared distinctive avatar [B2], matching bio text [C3], breach record linking the same email to both [A1].
- **Alternative considered**: the homonym/coincidence explanation, and why it was or wasn't ruled out.
- **Disconfirming evidence sought**: what you specifically checked for that would have undermined the claim (a namesake search, a check for a second person with the same bio template) — not just naming the alternative, actually looking for it — and what you found.
- **Confidence level**: Low / Moderate / High / Inconclusive.
- **Conclusion**: the wording actually used in the dossier for this binding.

---

## Common pivots out of this file
- Person → company: `02-companies.md`
- Username/account depth: `04-socmint.md`
- Email/phone in breaches: `05-breaches.md`
- Photos / location: `06-geolocation.md`
- Country-specific civil, land, and directory registries: `references-by-region.md`
- Harvesting colleague emails from a discovered pattern: `automation.md`
