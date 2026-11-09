# 02: Companies

Pivoting on a company, organization, or brand. Seed is typically a company name, a registration number (SIREN/SIRET in France, a Companies House number, an EIN, etc.), a brand, or an address. The goal is an entity card (legal identity, structure, officers, financials, premises) plus the people and other entities around it, each fact rated with the NATO Admiralty code.

The pivot tree below is transcribed from a field-tested mind map. From the central node COMPANY, most branches converge back on either a **person** (officer/director) or **another company** (sibling entity, same address, same group) — a company investigation is a people investigation wearing a legal wrapper, and the two files (`02` and `01`) are meant to be walked together.

Most of what a registry returns is a direct, primary-source fact (an A-rated filing). Two things on this tree are inferences rather than facts, and need the same discipline `01-people.md`, `03-infrastructure.md`, `04-socmint.md`, and `06-geolocation.md` apply to correlated claims: **"same group" from a shared officer or address**, and **beneficial-ownership data**. A shared registered officer or registered address does not by itself mean two companies belong to the same group — company-formation agents, domiciliation services, accountants, and professional nominee directors routinely register dozens of unrelated companies at one address or under one name. Beneficial-ownership filings are self-declared, sometimes stale, and sometimes use a nominee rather than the real controller. Treat both as leads to verify, not facts to assert — see "Confidence discipline for corporate inferences" below.

---

## Pivot tree: COMPANY

```
COMPANY
├── identification
│   ├── SIREN (France: unique entity number)
│   │   ├── structure (legal form, capital, incorporation date)
│   │   ├── status (active / dissolved / in receivership, filings)
│   │   ├── officers / beneficial owners  ──► pivot each as a new PERSON (01-people.md)
│   │   └── establishment history (where/when it has operated)
│   ├── SIRET (France: establishment-level number, one per physical site)
│   └── address
│       ├── land registry / cadastre  ──► property owner
│       └── reverse directory on the address  ──► other companies at the same address
│
├── officers / associates  (from the SIREN record — scan the whole list for the target's own surname, see below)
│   └── other companies they run or sit on  ──► loop back into this tree per company (same officer ≠ same group — verify, see below)
│   └── pivot each officer as a PERSON  ──► 01-people.md
│
├── professional / personal social accounts
│   └── personnel (employees, officers)  ──► 04-socmint.md
│
├── stock market / financial info
│   └── (public companies only) filings, ownership, financial statements
│
├── data breaches
│   └── company domain / employee emails in leak corpora  ──► 05-breaches.md
│
├── website
│   ├── legal notice (mentions légales)
│   ├── contact page
│   ├── personnel (team/about pages)
│   └── domain name
│       └── owner / contact (whois)  ──► 03-infrastructure.md
│
├── intellectual property
│   ├── trademark
│   ├── patent
│   ├── design / model (dessins & modèles)
│   └── geographical indication
│
└── local / trade press
    ├── photos  ──► reverse image (06-geolocation.md)
    └── articles (announcements, hires, disputes, expansions)
```

---

## Anchoring by seed type

### Seed = company name or brand
1. **Find the legal entity first.** A brand/trade name can map to several legal entities (franchise networks, holding structures, rebrands); confirm which one you mean before anything else. Start with a general registry search: OpenCorporates (cross-jurisdiction aggregator, good first stop regardless of country) or the national registry directly (see `references-by-region.md`).
2. **France:** Pappers.fr or Societe.com or Infogreffe.fr or the official annuaire-entreprises.data.gouv.fr — any of these resolves a name to a SIREN and gives structure, officers, financials, filings, and establishment history in one page. BODACC (bodacc.fr) carries official legal announcements (incorporation, changes, insolvency, business sales).
3. **Other jurisdictions:** Companies House (UK, free and complete), SEC EDGAR (US public companies), Handelsregister/Bundesanzeiger (Germany), and the rest of `references-by-region.md`.
4. Once you have the registration number, move to the "Seed = registration number" path below for depth.

### Seed = registration number (SIREN / SIRET / company number)
1. Pull the full record: legal form, share capital, incorporation date, registered address, current status (active/dissolved/insolvency proceedings), NAF/APE activity code. **A registry's incorporation date and a founder's own "founded in [year]" aren't necessarily the same fact** — a company's legal entity can be incorporated a year or more after the founder started trading under the same name (freelance activity, an unincorporated partnership). Two different "founding" dates from two sources isn't automatically a contradiction; check which event each date actually marks (legal formation vs. first commercial activity) before treating them as conflicting — see "Handling contradictions" in `09-deliverables.md`.
2. **Officers and beneficial owners.** Pappers and Infogreffe both surface the "bénéficiaires effectifs" (beneficial-ownership filing, mandatory in France) and the list of current/past legal representatives (gérant, président, directeur général). The legal-representative list is a direct registry fact (A-rated). The beneficial-ownership filing is self-declared and can be outdated, incomplete, or name a nominee rather than the real controller — rate it on its own (typically B/C on reliability) rather than inheriting the registry's A rating by association. Pivot every name into `01-people.md` — this is usually the single richest branch. **Scan the whole officer/associate/shareholder list for the target's own surname, every time, not just for the target's name itself.** Family businesses, SCIs, and GFAs routinely list several relatives as co-gérants, associés, or beneficial owners under a shared surname — this is exactly how Max De Quick's brother François surfaced (same GFA, same rare surname, a name on the list that was never going to turn up any other way). A same-surname co-officer is a lead, not a confirmed relative — rate it like any other correlation (same confidence grid, "disconfirming evidence sought" field) rather than assuming family just because the surname matches, especially for a common surname.
3. **Establishment history.** Where the company has had SIRET-registered premises over time; a move, a closure, or a new establishment all date and geographically anchor the company's activity.
4. **Group structure.** Parent/subsidiary links, other companies sharing the same registered officer, same registered address, or (for groups) consolidated-accounts filings naming subsidiaries. A shared officer or address is a *candidate* group link, not a confirmed one — company-formation agents, domiciliation addresses, and professional nominee directors produce the same pattern between entities that have no real connection. Verify with a second, independent signal (consolidated accounts naming the subsidiary, a press release, a shared ownership-stake filing, a shared website/brand) before stating a group relationship as fact; otherwise state it as a candidate link and flag the confidence level (see below). **Check GLEIF's LEI Search too, if the entity is mid-size+ or financial** — when an entity has filed a Legal Entity Identifier, GLEIF's own "Level 2" relationship data states its direct and ultimate parent explicitly; this is a filed, regulator-backed statement rather than an inferred shared-officer pattern, so a hit there is a harder signal (closer to High than Low on the grid below) than the address/officer matches above. See `08-tools-catalog.md` and `references-by-region.md`. Loop each sibling entity back through this same tree — but a large group recurses exactly the way the associate/officer branch does in `01-people.md`, so the same depth budget applies: full pass on the target entity, a bounded pass (identity + top pivots) on each direct sibling, entity-level only beyond that.
5. **Financial filings.** Annual accounts (when filed — many small French companies file abbreviated accounts or claim confidentiality) give revenue/headcount bands; for listed companies see the stock-market branch below.

### Seed = postal address
1. **Reverse directory on the address.** Pappers and Societe.com both offer an "autres sociétés à cette adresse" (other companies at this address) lookup — a single business address (a co-working space, a domiciliation agency, a shell-company mill) can surface dozens of registered entities at once, which is itself informative (a domiciliation agency address is a weaker signal of real operations than a standalone building).
2. **Cadastre / land registry.** Confirms who owns the premises (which may differ from who operates there — a landlord vs. a tenant company). See `references-by-region.md` for the French cadastre and equivalents.
3. From any company found at the address, continue with the "Seed = registration number" path.

### Seed = website / domain (company runs a site)
Jump to `03-infrastructure.md` for the domain-side pivots (whois, mentions légales, tech stack), then bring whatever entity identity it surfaces back into this file.

---

## Depth-specific branches

### Stock market / financial information
Only applies to public (listed) companies, but worth checking even for a subsidiary of a public group (filings for the parent can disclose the subsidiary). Sources: Boursorama, Yahoo Finance, Google Finance for live/historical price and basic filings (France/international); for authoritative regulatory filings, SEC EDGAR (US), the AMF's BDIF (France), or the relevant national regulator. Ownership disclosures (major shareholders crossing a threshold) and executive compensation filings are both good for officer/pivot data beyond what a basic company registry gives.

**SEC EDGAR's full-text search is a cross-company person pivot, not just a per-company filing lookup.** Beyond pulling one company's own 10-K/8-K, EDGAR's full-text search (sec.gov/edgar/search, backed by efts.sec.gov) searches the *text* of filings themselves and supports a dedicated reporter's-name field alongside keyword/company/CIK and boolean operators (exact phrase in quotes, OR, exclusions, wildcards). Searching a person's name directly surfaces every filing, across every company, that names them as an officer, director, or beneficial owner — a genuine cross-company pivot a single-company lookup misses. The SEC's current FAQ states coverage back to 2001; spot-check the live tool's date range before relying on an older source for the exact window.

### Data breaches
Take the company's email domain (and any employee emails already collected) into `05-breaches.md`. A company breach history (credential dumps naming `@company.com` addresses, a disclosed incident) is both a direct finding and, operationally, a reason to be careful about how the recon itself is conducted if the engagement has a defensive angle.

### Intellectual property
- **France:** INPI (inpi.fr) — trademarks, patents, designs & models (dessins & modèles), and geographical indications, searchable by owner name or mark. INPI also runs the national company register data.
- **EU:** EUIPO (euipo.europa.eu) for EU trademarks and registered designs.
- **International:** WIPO Global Brand Database (brand/trademark, cross-jurisdiction) and WIPO PatentScope (patents); Espacenet (patents, strong non-US/EU coverage too).
- **US:** USPTO TESS (trademarks) and USPTO Patent Full-Text Search.
A trademark/patent filing names the owner entity and sometimes an individual inventor/applicant — both are pivots. Filing dates and renewal gaps (a lapsed trademark, an abandoned patent application) are also informative about a company's trajectory.

### Local / trade press
General and regional news search (Google News scoped by region/language, plus any local outlet specific to the company's area) for announcements, hires, expansions, disputes, and litigation. Any photo attached to coverage is a reverse-image candidate (`06-geolocation.md`) — company press photos often double as the only public photo of an otherwise low-profile officer.

---

## Confidence discipline for corporate inferences

"Same group" and "real beneficial owner" claims are correlations across signals, not direct registry reads — rate them with the same confidence grid used in `01-people.md`, `03-infrastructure.md`, `04-socmint.md`, and `06-geolocation.md` (an internal working grid, kept consistent across the skill: Low/Moderate/High/Inconclusive), separately from the Admiralty rating of each individual signal feeding into them.

| Confidence | Criteria |
|---|---|
| **Low** | Shared officer or address only, no other link (the single most common false-positive pattern: a domiciliation agency, formation agent, or professional nominee director shared by unrelated companies). |
| **Moderate** | Two or more independent signals point the same way (shared officer **and** shared brand/website, or shared address **and** overlapping activity code), none individually decisive. |
| **High** | A hard link confirms it: consolidated accounts naming the subsidiary, an explicit ownership-stake filing, an official group announcement. |
| **Inconclusive** | Signals conflict, or the shared element (officer, address) is independently known to be a formation-agent/nominee pattern rather than evidence of a real relationship. |

Record it the same way an identity-binding claim is recorded in `01-people.md`: the claim, each signal rated individually, the formation-agent/nominee alternative considered and why it was or wasn't ruled out, disconfirming evidence actively sought (not just the alternative named — what you specifically checked, e.g. whether the shared address is a known domiciliation agency rather than a real operating site), the confidence level, and the conclusion as actually worded in the dossier.

---

## Common pivots out of this file
- Officers / beneficial owners → person: `01-people.md`
- Registered address → cadastre / reverse directory: this file (identification branch) and `references-by-region.md`
- Company website → domain/whois/tech stack: `03-infrastructure.md`
- Employees' social presence: `04-socmint.md`
- Company/employee email exposure: `05-breaches.md`
- Press photos / logos: `06-geolocation.md`
- Country-specific corporate, IP, and land registries: `references-by-region.md`
- Tool shortlist for each step: `references/08-tools-catalog.md`
