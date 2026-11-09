---
name: osint-investigation
description: "Use whenever the user or another skill needs OSINT on a target: researching a person, company, domain, email, username, phone, IP, brand, or image to build a dossier, find pivots, identify assets, map relationships, or prepare a pretext. Covers direct requests ('trouve tout sur X', 'identifie cette photo', 'qui dirige cette boite', 'a qui appartient ce site') and recon phases invoked from other skills (e.g. a pentest or doc-review skill needing recon on an organization or individual), in any language. Spans people, companies, websites/infrastructure, and images, including grey-area techniques (LinkedIn scraping, breach data, sock-puppets, headless collection) for thorough offensive and investigative recon. Dorks-and-sources-first: leans on search operators and directly queryable sources (Pappers, Companies House, SEC EDGAR, crt.sh, DNSDumpster, Have I Been Pwned, Wayback) plus a generalized headless-browser engine rather than install-heavy tooling. Do NOT use for actively scanning live infrastructure (use identifying-network-services), source code review, or neutral background reading that needs no pivoting."
---

# OSINT Investigation

The goal is not to dump every URL a search returns. It is to **build a dossier of correlated, source-rated facts about a target by pivoting between sources**, exhaustively.

A list of links is a failure of this skill. So is a generic "here is what the web says about X". The deliverable is a **structured, rated map of the target and its surroundings**, with concrete pivot trails an analyst can audit and extend.

The seed (a name, email, domain, username, phone, IP, brand, or image) comes from the request or from the calling context (another skill's recon phase). This skill does not actively scan or attack live infrastructure: it reads, searches, correlates, rates, and (when configured) collects via a headless browser.

---

## Philosophy

Internalize these before touching the workflow. Every decision in this skill descends from them.

**Dorks and queryable sources first.** The fastest, most reliable OSINT runs on three things: well-built search-operator queries (dorks), light scraping, and sources that answer a direct query without setup. A query gets you most of the way before any tool does. Reach first for things you can hit straight from a browser or a one-line request: search dorks, DNSDumpster and crt.sh for infrastructure, Societe.com and Pappers and Companies House and SEC EDGAR for companies, Have I Been Pwned for breach exposure, the Wayback Machine and archive.today for history. These are stable, fast, and need no install. Anything that requires `git clone`, a build step, an API key dance, or a fragile install is a last resort, not a first move, and usually a heavyweight wrapper around a query you could have written yourself.

**Build on the source, not the wrapper.** Whatever surfaces a finding, anchor the finding to the underlying authoritative source (the registry, the filing, the certificate log, the archived page). Sources are durable and citable; the thing that helped you find them is interchangeable. This keeps the dossier defensible and keeps the method working even as individual tools come and go.

**Don't stay in the sandbox.** An abstracted search/fetch tool is a convenience layer, not the ceiling of what's available this session. When a real browser is reachable (Claude in Chrome, or the built-in browser pane), default to using it for anything that matters rather than stopping at whatever an abstracted tool returns — the same query run by a human in a real browser tab routinely surfaces what the abstracted version missed entirely (observed directly: an exact-phrase name search came back empty through the abstracted tool, then immediately surfaced a LinkedIn profile and press coverage in a live browser — see `07-dorks-and-search.md`). This extends past search: click into a profile, scroll an activity feed, upload a local screenshot for reverse-image search, log into a platform the operator already has open. When the operator offers one of their own logged-in accounts (LinkedIn, Facebook, a paid tool) for deeper access on a given target, use it — that's a deliberate, per-target call each time (see the footprint note on attributable logged-in actions in `00-operational-footprint.md`), not a standing default to log in as them on every investigation.

**Pivots, not lists.** Every finding has value as data AND as a bridge. A username on one platform is a fact, but it is also the pivot to GitHub, Steam, Disqus, breach corpora, and Gravatar. An address pivots to the land registry, the reverse directory, and every company domiciled there. Always ask: what does this finding let me reach next? The pivot trees in the reference files (transcribed from field-tested mind maps) are the backbone of this method.

**Score every claim.** Findings range from "pulled from an authoritative registry" to "inferred from weak circumstantial signals". The reader must see which is which. Rate every direct fact with the NATO Admiralty code (source letter + credibility digit, e.g. A1, C3, F4), defined below. A *correlation* across signals — this account is this person, these companies are the same group, this is the same site owner, this photo places the scene here — is a different kind of claim and is never compressed into a single Admiralty rating as if it were a direct observation; it gets its own Low/Moderate/High/Inconclusive confidence level instead. See the confidence-grid sections in `01-people.md`, `02-companies.md`, `03-infrastructure.md`, `04-socmint.md`, and `06-geolocation.md`, and the recording rule in `09-deliverables.md`.

**Exhaustive by default, but mind the footprint.** Pull everything, follow every pivot, leave nothing on the table. The only operational constraint is awareness: a few actions tip off the target (registration probes, logged-in profile views, interactions, direct fetches of target-owned pages). Know which, so you do not announce the collection by accident. See `references/00-operational-footprint.md`.

**Absence is a finding.** No LinkedIn, no breach hits, no domain registration, no press: each absence says something (privacy-conscious target, fresh identity, scrubbed history, or wrong seed). Record what is not there, not only what is.

**The seed must be right before anything else.** A flawless dossier on the wrong John Smith is worse than nothing: it is confidently misleading. Disambiguate before expanding.

**A contradiction is a finding, not a bug to silently fix.** Two sources disagreeing (a company "founded in 2018" vs "founded in 2019") is common and is itself informative — before picking a winner, check whether they're actually measuring different things (incorporation date vs. first commercial activity, for instance — both can be true at once). Keep both claims, their sources, and the resolution (or the fact that it's unresolved) in the dossier; never silently overwrite one with the other. See "Handling contradictions" in `references/09-deliverables.md`.

---

## Deliverable

One format, always: a single Markdown report containing everything found, plus an `Annexes/` folder for anything non-textual (images, screenshots, videos, downloaded documents) when there is any. No variation by use case: collect and report exhaustively. See `references/09-deliverables.md` for the full template, correlation method, and a worked example.

1. **Target in one paragraph.** What the target is and the seed it grew from.
2. **Identity card.** Core facts as a labelled list, each rated with the Admiralty code.
3. **Findings**, grouped by subject, each with identifiers extracted, notable findings (source + date + rating), and pivots available.
4. **Pivots followed.** A short audit trail: seed → finding → source → next pivot.
5. **What is missing.** Coverage gaps and sources that returned nothing.

### Source/information rating (NATO Admiralty system)

Rate every fact with the NATO Admiralty code (STANAG 2511): a letter for source reliability and a digit for information credibility, written as a pair such as A1, B2, or F6. The two axes are independent: a reliable source can report something uncorroborated, and an unreliable source can report something that turns out true.

Source reliability: **A** completely reliable (authoritative registry, official filing, primary document) · **B** usually reliable (established outlet, the target's own verified channel) · **C** fairly reliable · **D** not usually reliable · **E** unreliable · **F** cannot be judged (new/unknown source).

Information credibility: **1** confirmed by independent sources · **2** probably true (consistent with other known facts) · **3** possibly true (plausible, not corroborated) · **4** doubtful · **5** improbable · **6** cannot be judged.

So an official corporate filing read directly is A1 or A2; a single unsourced forum post is F3 or F4; two independent reputable outlets reporting the same thing is B1. Never silently merge axes or round a guess up to look solid. People-search aggregators are typically C or D on reliability: treat their output as a lead, climb to a primary source, then re-rate.

**A second, separate grid for correlation claims.** The Admiralty code rates a single source's reliability and a single piece of information's credibility. It does not fit a claim built by correlating several signals (an identity binding, a corporate-group link, a cross-site ownership link, an image-based identification) — for those, each file above uses a shared internal working grid: **Low** (one weak/common signal), **Moderate** (two-plus independent signals, none decisive), **High** (a hard, independently-verifiable link), **Inconclusive** (signals conflict or don't rule out a plausible alternative). State both: the individual signals' Admiralty ratings, and the correlation's confidence level — never collapse a correlation into a bare Admiralty rating.

---

## Workflow

Five phases. On a first run, read the phase references in order. On a follow-up ("now pivot on this username", "dig the infrastructure", "geolocate this photo"), jump straight to the relevant reference.

| Phase | Goal | Reference |
|---|---|---|
| 0 | Footprint awareness (what tips off the target) | `references/00-operational-footprint.md` |
| 1 | Cadrage + seed validation | this file (below) |
| 2 | Identification + anchoring | router below → target-type reference |
| 3 | Expansion via pivots | target-type references |
| 4 | Correlation + rating | `references/09-deliverables.md` |
| 5 | Report assembly | `references/09-deliverables.md` |

### Router by target type

Load the reference that matches the seed. Most investigations cross over (a person leads to a company, a company to its website, a website to its registrant, an image to a person), so load several as the pivots demand.

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

**Set the graph depth.** Decide how far the recursion runs (the target only, the target plus direct relations/entities, or wider) and how much effort each degree gets — a bound on *how far* without a bound on *how much per entity* still sprawls. See the depth-control note (with a search budget per degree) in `references/01-people.md`.

Only once the seed is solid do you move to Phase 2 and the target-type reference.

---

## Operating notes

**Cite as you go.** Every fact carries a URL and a retrieval date. OSINT findings decay (profiles deleted, pages edited, companies dissolved); a finding without a timestamped source is hard to defend later.

**Keep "when it was true" separate from "when you found it."** These are different timestamps and conflating them is a recurring OSINT failure (see `05-breaches.md`'s "an exposure fact is anchored to the breach date, not to the target today" for a worked instance). Track, when relevant to a finding:
- **`retrieved_at`** — when you looked it up. Always record this; it's the baseline "cite as you go" timestamp.
- **`valid_from` / `valid_until`** — the window during which the fact was/is actually true in the world (an address held 2015–2020, a company status valid until dissolution). Often only partially known — record what you can (e.g. "valid_until: unknown, still current as of retrieved_at").
- **`first_seen` / `last_seen`** — for a fact drawn from an evolving or aggregated source (a Wayback-captured page, a breach corpus, a heatmap), the range over which the evidence itself was observed to hold.
Not every finding needs all four — a one-off registry read just needs `retrieved_at`. Add the others when the fact's validity window is itself part of the finding (which is most of the time for addresses, affiliations, and anything that can change).

**Snapshot volatile sources.** When something matters, archive it (Wayback "Save Page Now", archive.today, or a local capture in `Annexes/`) before it changes. Note the archive URL alongside the live one.

**Prefer primary over aggregator.** A people-search aggregator claiming an address rates C or D on reliability; the land registry or an official filing rates A. Climb toward the primary source whenever a finding matters, then re-rate.

**Re-read this skill's philosophy if a run drifts into a link dump.** The single most common failure mode is collecting breadth without pivoting or rating. If the output starts looking like search-results-with-extra-steps, return to "pivots, not lists" and "score every claim".

**Scope note.** This skill reads, queries, and correlates — it doesn't actively exploit or take over accounts; for that, see `identifying-network-services` / `bug-bounty-web`.
