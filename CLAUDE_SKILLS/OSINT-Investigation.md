---
name: osint-investigation
description: "Use whenever the user or another skill needs OSINT on a target: researching a person, company, domain, email, username, phone, IP, brand, or image to build a folder, find pivots, identify assets, map relationships, or prepare a pretext. Covers direct requests and recon phases invoked from other skills (e.g. a pentest or doc-review skill needing recon on an organization or individual), in any language. Spans people, companies, and infrastructure, including grey-area techniques (LinkedIn scraping, breach data, sock-puppets, headless collection) for thorough offensive and investigative recon. Dorks-and-sources-first: leans on search operators and directly queryable sources (Pappers, Companies House, SEC EDGAR, crt.sh, DNSDumpster, Have I Been Pwned, Wayback) plus a generalized headless-browser engine rather than install-heavy tooling. Do NOT use for actively scanning live infrastructure (use identifying-network-services), source code review, or neutral background reading that needs no pivoting."
---

# OSINT Investigation

The goal is not to dump every URL a search returns. It is to **build a folder of correlated, source-rated facts about a target by pivoting between sources**, exhaustively.

A list of links is a failure of this skill. So is a generic "here is what the web says about X". The deliverable is a **structured, rated map of the target and its surroundings**, with concrete pivot trails an analyst can audit and extend.

The seed (a name, email, domain, username, phone, IP, brand, or image) comes from the request or from the calling context (another skill's recon phase). This skill does not actively scan or attack live infrastructure: it reads, searches, correlates, rates, and (when configured) collects via a headless browser.

---

## Philosophy

Internalize these before touching the workflow. Every decision in this skill descends from them.

**Dorks and queryable sources first.** The fastest, most reliable OSINT runs on three things: well-built search-operator queries (dorks), light scraping, and sources that answer a direct query without setup. A query gets you most of the way before any tool does. Reach first for things you can hit straight from a browser or a one-line request: search dorks, DNSDumpster and crt.sh for infrastructure, Societe.com and Pappers and Companies House and SEC EDGAR for companies, Have I Been Pwned for breach exposure, the Wayback Machine and archive.today for history. These are stable, fast, and need no install. Anything that requires `git clone`, a build step, an API key dance, or a fragile install is a last resort, not a first move, and usually a heavyweight wrapper around a query you could have written yourself.

**Build on the source, not the wrapper.** Whatever surfaces a finding, anchor the finding to the underlying authoritative source (the registry, the filing, the certificate log, the archived page). Sources are durable and citable; the thing that helped you find them is interchangeable. This keeps the folder defensible and keeps the method working even as individual tools come and go.

**Pivots, not lists.** Every finding has value as data AND as a bridge. A username on one platform is a fact, but it is also the pivot to GitHub, Steam, Disqus, breach corpora, and Gravatar. An address pivots to the land registry, the reverse directory, and every company domiciled there. Always ask: what does this finding let me reach next? The pivot trees in the reference files (transcribed from field-tested mind maps) are the backbone of this method.

**Score every claim.** Findings range from "pulled from an authoritative registry" to "inferred from weak circumstantial signals". The reader must see which is which. Rate every fact with the NATO Admiralty code (source letter + credibility digit, e.g. A1, C3, F4), defined below.

**Exhaustive by default, but mind the footprint.** Pull everything, follow every pivot, leave nothing on the table. The only operational constraint is awareness: a few actions tip off the target (registration probes, logged-in profile views, interactions, direct fetches of target-owned pages). Know which, so you do not announce the collection by accident. See `references/00-operational-footprint.md`.

**Absence is a finding.** No LinkedIn, no breach hits, no domain registration, no press: each absence says something (privacy-conscious target, fresh identity, scrubbed history, or wrong seed). Record what is not there, not only what is.

**The seed must be right before anything else.** A flawless folder on the wrong John Smith is worse than nothing: it is confidently misleading. Disambiguate before expanding.

---

## Deliverable

One format, always: a single Markdown report containing everything found, plus an `Annexes/` folder for anything non-textual (images, screenshots, videos, downloaded documents) when there is any. No variation by use case: collect and report exhaustively.

### The Markdown report

1. **Target in one paragraph.** What the target is and the seed it grew from.
2. **Identity card.** Core facts as a labelled list, each rated with the Admiralty code: names/aliases, DOB and birthplace if relevant, locations, primary identifiers (emails, usernames, phone, registration numbers like SIREN/SIRET/company number), affiliations.
3. **Findings**, grouped by subject (the target, each person around it, each related entity, each infrastructure cluster). For each subject:
   - One-line summary.
   - **Identifiers extracted**: emails, usernames, IDs, IPs, phones, profile URLs, registration numbers.
   - **Notable findings**, each with its source URL, retrieval date, and Admiralty rating.
   - **Pivots available**: what this subject opens onto next.
   - Links to any related files in `Annexes/`.
4. **Pivots followed.** A short audit trail: from seed → finding → source → next pivot, so the chain can be verified and extended.
5. **What is missing.** Coverage gaps and sources that returned nothing (itself a signal).

### The `Annexes/` folder

Created only when there is non-textual material to keep: profile photos, screenshots of pages likely to change or be deleted, downloaded documents, videos, exported CSVs from the headless engine. Reference each annex file from the relevant finding in the report. Snapshot volatile evidence (a tweet, a profile, a listing) before it disappears, and store the capture here alongside its live and archive URLs.

### Source/information rating (NATO Admiralty system)

Rate every fact with the NATO Admiralty code (STANAG 2511): a letter for source reliability and a digit for information credibility, written as a pair such as A1, B2, or F6. The two axes are independent: a reliable source can report something uncorroborated, and an unreliable source can report something that turns out true.

Source reliability:
- **A**: completely reliable (authoritative registry, official filing, primary document).
- **B**: usually reliable (established outlet, the target's own verified channel).
- **C**: fairly reliable.
- **D**: not usually reliable.
- **E**: unreliable.
- **F**: reliability cannot be judged (new or unknown source).

Information credibility:
- **1**: confirmed by independent sources.
- **2**: probably true (consistent with other known facts).
- **3**: possibly true (plausible, not corroborated).
- **4**: doubtful.
- **5**: improbable.
- **6**: credibility cannot be judged.

So an official corporate filing read directly is A1 or A2; a single unsourced forum post is F3 or F4; two independent reputable outlets reporting the same thing is B1. Never silently merge axes or round a guess up to look solid. Presenting an F3 rumor as an A1 fact defeats the purpose of rating. People-search aggregators are typically C or D on reliability: treat their output as a lead, climb to a primary source, then re-rate.

---

## Workflow

Five phases. On a first run, read the phase references in order. On a follow-up ("now pivot on this username", "dig the infrastructure"), jump straight to the relevant reference.

| Phase | Goal | Reference |
|---|---|---|
| 0 | Footprint awareness (what tips off the target) | `references/00-operational-footprint.md` |
| 1 | Cadrage + seed validation | this file (below) |
| 2 | Identification + anchoring | router below → target-type reference |
| 3 | Expansion via pivots | target-type references |
| 4 | Correlation + rating | `references/09-deliverables.md` |
| 5 | Report assembly | `references/09-deliverables.md` |

### Router by target type

Load the reference that matches the seed. Most investigations cross over (a person leads to a company, a company to its infrastructure), so load several as the pivots demand.

| Seed / target type | Primary reference | Frequently also |
|---|---|---|
| Person (name, alias) | `references/01-people.md` | socmint, breaches, geolocation |
| Email address | `references/01-people.md` + `references/05-breaches.md` | socmint |
| Username / pseudo | `references/04-socmint.md` | people, breaches |
| Company / brand | `references/02-companies.md` | infrastructure, people |
| Domain / website / IP | `references/03-infrastructure.md` | companies |
| Image / photo | `references/06-geolocation.md` | people, socmint |
| Phone number | `references/01-people.md` | breaches |

### Cross-cutting references

| When the task involves... | Load |
|---|---|
| Building search queries (always relevant early) | `references/07-dorks-and-search.md` |
| Choosing a tool for a specific job | `references/08-tools-catalog.md` |
| Region-specific registries (corporate, land, civil) | `references/references-by-region.md` |
| Breaches, dumps, exposed credentials | `references/05-breaches.md` |
| Automated / scaled collection | `references/automation.md` (the headless engine) |

Load `references/07-dorks-and-search.md` early. Almost every pivot starts with a query, and the query is where most of the leverage lives.

---

## Phase 1: Cadrage and seed validation

Before any search. Five minutes here saves hours of chasing the wrong target.

**Disambiguate the seed.** "Jean Dupont" is not yet a target. Pin it with distinguishing context: city, employer, age range, a known identifier. If the seed is ambiguous and you cannot disambiguate from what you were given, ask. For a company, confirm which legal entity (a brand can map to several). For a domain, confirm it is the right one (typosquats and look-alikes abound).

**Sanity-check the seed before expanding.**
- Person: real, distinguishable, alive, in the expected region.
- Company: exists in a registry, current status, parent/subsidiary structure.
- Domain: resolves, registrar and creation date plausible, not an obvious look-alike.
- Image: already published widely? A quick reverse search tells you if it is stock, news, or original.

**Set the graph depth.** Decide how far the recursion runs (the target only, the target plus direct relations/entities, or wider). Without this, the run never ends. See the depth-control note in `references/01-people.md`.

Only once the seed is solid do you move to Phase 2 and the target-type reference.

---

## Operating notes

**Cite as you go.** Every fact carries a URL and a retrieval date. OSINT findings decay (profiles deleted, pages edited, companies dissolved); a finding without a timestamped source is hard to defend later.

**Snapshot volatile sources.** When something matters, archive it (Wayback "Save Page Now", archive.today, or a local capture in `Annexes/`) before it changes. Note the archive URL alongside the live one.

**Prefer primary over aggregator.** A people-search aggregator claiming an address rates C or D on reliability; the land registry or an official filing rates A. Climb toward the primary source whenever a finding matters, then re-rate.

**Re-read this skill's philosophy if a run drifts into a link dump.** The single most common failure mode is collecting breadth without pivoting or rating. If the output starts looking like search-results-with-extra-steps, return to "pivots, not lists" and "score every claim".
