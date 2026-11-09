# References by Region

Country-specific corporate, land/property, civil-status, and reverse-directory registries. Consult this file whenever a target-type reference says "see region-specific registries" — this is the list of what's actually queryable, by jurisdiction.

Registries are the top of the reliability scale (Admiralty A/B) precisely because they're primary/official; always prefer the registry itself over an aggregator that merely indexes it, and use this file to find which registry applies.

---

## France

| Need | Source |
|---|---|
| Company identity (SIREN/SIRET), officers, filings, financials | Pappers.fr, Societe.com, Infogreffe.fr — any one resolves a name to a SIREN with structure/officers/financials in one page |
| **Reverse: find every company a given person directs** (run by default on any French person seed, not only when a directorship already looks plausible) | Pappers.fr/Societe.com/Infogreffe.fr's own "dirigeant" person-search (separate from their company-name box); BODACC name search for the same from the legal-announcements side |
| Official company register (authoritative, free) | annuaire-entreprises.data.gouv.fr |
| Official legal announcements (incorporation, insolvency, business sales) | BODACC (bodacc.fr) |
| Beneficial ownership (bénéficiaires effectifs) | Infogreffe, Pappers (both surface the mandatory filing — self-declared, rate independently of the surrounding registry data, see `02-companies.md`) |
| **Association officers** (président/trésorier/secrétaire of any *association loi 1901* — sports clubs, cultural/hobby associations, parents' associations, local charities; not covered by the company registries above at all) | RNA / Répertoire National des Associations (data.gouv.fr/associations), Journal Officiel "Associations" search (journal-officiel.gouv.fr/pages/associations-recherche) |
| Trademarks, patents, designs & models | INPI (inpi.fr) |
| Domain whois (.fr) | AFNIC whois |
| Cadastre / land parcels | cadastre.gouv.fr |
| Property transaction values (DVF — Demandes de Valeurs Foncières) | app.dvf.etalab.gouv.fr or demandesvaleursfoncieres.cerema.fr |
| Civil status: death records (open data) | deces.matchid.io / data.gouv.fr "Fichier des personnes décédées" |
| Civil status: birth/marriage records | held by the local mairie; not centrally open, request via the relevant commune. Regional press "carnet"/"naissances-mariages" announcement sections (site-scoped dorks on the local paper, e.g. `site:lunion.fr "naissance"`) sometimes cover what the mairie won't hand out directly. |
| White-pages lookup (name + city → listed phone/address) | PagesJaunes.fr "particuliers" tab |
| Reverse phone directory (phone → name) | Pages Blanches / annuaire inversé services (118712, PagesJaunes "annuaire inversé") |
| Family-tree / genealogy (lead only, see the hedge in `01-people.md`) | Geneanet, Filae |
| Registered tradespeople (artisans — plumbers, electricians, hairdressers, etc., a separate register from the dirigeant search) | Répertoire des Métiers / Chambre de Métiers et de l'Artisanat, via Pappers' own "Artisans" tab |
| Elected office (every mayor, municipal/departmental/regional councillor, MP, senator) | RNE — Répertoire National des Élus (data.gouv.fr), open data as raw per-mandate CSVs (no name-search UI of its own — use a front-end like Civiqo for a quick lookup, then verify against the raw CSV, see `01-people.md`) |
| Civil-service concours (entrance exams) and nominations (civil servants, magistrates, military officers) | JORF via legifrance.gouv.fr's own search, by name |
| Stock market / regulatory filings (listed companies) | AMF (BDIF database), Boursorama |

## European Union / wider Europe

| Need | Source |
|---|---|
| EU trademarks, registered designs | EUIPO (euipo.europa.eu) |
| Cross-EU company lookup (links to national registries) | European e-Justice Business Registers portal |
| UK: officers, filings, charges | Companies House (free, complete) |
| UK: charity trustees/officers (the association-registry equivalent — not in Companies House) | Charity Commission for England and Wales register, OSCR (Scotland), Charity Commission for Northern Ireland |
| UK: land registry | HM Land Registry |
| Germany: company register, filings | Handelsregister, Bundesanzeiger |
| Belgium: company register | BCE/KBO (Banque-Carrefour des Entreprises) |
| Switzerland: company register | Zefix |
| Netherlands: company register | KVK (Kamer van Koophandel) |
| Spain: company register | Registro Mercantil Central |
| Italy: company register | Registro Imprese |
| Ireland: company register | CRO (Companies Registration Office) |
| Luxembourg: company register (common for holding structures) | RCS Luxembourg (Registre de Commerce et des Sociétés) |

## United States

| Need | Source |
|---|---|
| Public-company filings (10-K, 8-K, ownership/insider) | SEC EDGAR |
| State-level company registration | the relevant state's Secretary of State business-search portal (per-state, no federal company register) |
| Property / land records | county assessor or recorder's office (per-county, no national registry — search "[county] assessor property search") |
| Trademarks | USPTO TESS |
| Patents | USPTO Patent Full-Text Search |
| Nonprofit officers/board members (the association-registry equivalent) | IRS Tax Exempt Organization Search (for the Form 990 filing itself, which names officers and compensation) via irs.gov, or an indexed front-end like ProPublica's Nonprofit Explorer / Candid (GuideStar) |
| Political campaign contributions (donor name, address, employer, occupation, above the disclosure threshold) | FEC (fec.gov / OpenFEC API), aggregated at OpenSecrets.org — self-reported by the filer, not FEC-verified; a solid employer/location-binding pivot |

## Cross-jurisdiction / global aggregators

| Need | Source |
|---|---|
| Company lookup across 140+ jurisdictions (first stop for any non-French/non-US company) | OpenCorporates |
| Legal Entity Identifier lookup, official/regulator-backed, cross-jurisdiction — includes filed parent/subsidiary relationships when available | GLEIF LEI Search (strongest for mid-size+ companies and financial entities; thin for small/local businesses — see `08-tools-catalog.md`) |
| Offshore entity structures (leaked registries) | OffshoreLeaks (ICIJ) |
| Cross-border investigative dataset: leaks, registries, sanctions | Aleph (OCCRP) |
| Global trademark search | WIPO Global Brand Database |
| Global patent search | WIPO PatentScope, Espacenet |
| Sanctions / PEP (politically exposed person) screening | OpenSanctions, national sanctions lists (OFAC SDN for the US, EU consolidated list) |
| Elected officials / officeholders, partial cross-country coverage (structured data, not a registry — see caveat below) | Wikidata (a politician's "position held" / P39 statements), query.wikidata.org for a SPARQL search across many officeholders at once; strongest for national-level figures, thins out fast below that |
| Association/nonprofit officers, Germany specifically | Vereinsregister (via the relevant Amtsgericht, or indexed at unternehmensregister.de) — Germany's registered-association (*eingetragener Verein*, e.V.) equivalent of France's RNA |

---

## Using this file, and what to do when a country isn't listed

**No single master index covers every registry category for every country** — be honest about that rather than pretending one exists. What this file actually gives you is two things: (1) the registries already confirmed for a handful of jurisdictions, and (2) a repeatable method for finding the equivalent anywhere else, for *any* of the registry categories used throughout this skill (companies, associations/nonprofits, trades/licensing, elected office, civil service, land/property, civil status) — not just companies.

1. Identify the jurisdiction from whatever anchored the target so far (a SIREN format, a `.fr`/`.de`/`.co.uk` domain, an address, a stated nationality).
2. Check this file for that country first. Go to the official/primary registry listed — it's the highest Admiralty rating available and usually free for a basic lookup.
3. **If the jurisdiction or the category isn't listed here, don't skip the check — go find it, the same way `01-people.md`'s steps do for France:**
   - For **companies**: OpenCorporates first (140+ jurisdictions, genuinely a global aggregator), or `"[country] company register"`.
   - For **elected officials/officeholders**: try Wikidata first (above) for a quick structured check, especially at national level; for anything more local, `"[country] elected officials register"` / `"[country] [office type] directory"`.
   - For **associations/nonprofits**: `"[country] nonprofit register"` / `"[country] charity register"` / `"[country] association register"` — most countries have *some* national or regional equivalent, rarely indexed anywhere central.
   - For **trades/licensing (the "artisan" category)**: this one genuinely doesn't generalize to a single registry type even within one country — it's trade-specific (a gas engineer, an electrician, and a hairdresser are licensed by different bodies in most countries). Search `"[country] [specific trade] license lookup/register"` rather than looking for one unified source.
   - For **civil-service concours/nominations**: France's JORF-published, name-searchable concours results are closer to a French administrative tradition than a universal pattern — most countries don't publish this by name at all. Don't assume an equivalent exists; check and report the absence if a search turns up nothing, rather than silently skipping the branch.
   - In every case: once you've found the real source for a country/category combination that isn't here yet, **add it to this file** so the next investigation doesn't have to re-discover it.
4. Multi-jurisdiction entities (holding structures, EU groups) often have one entity per country — walk each national registry rather than assuming one lookup covers the whole group.
