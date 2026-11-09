# 09: Correlation, Rating, and Report Assembly

Phases 4 and 5. By this point the expansion (phase 3) has produced a pile of raw findings across one or more target-type references. This file is how that pile becomes the single Markdown dossier described in `SKILL.md`'s Deliverable section — not a bigger pile, a correlated and rated map.

---

## Phase 4: Correlation and rating

**Deduplicate entities before writing anything.** The same person often surfaces from three branches at once (the person tree's name search, the company tree's officer list, and a socmint hit) — these are one subject, not three. Before drafting, build a working list of distinct entities (people, companies, domains, locations) and merge every finding under its entity, not under the branch that produced it.

**Re-rate as you climb.** A fact's rating can change as corroboration accumulates. An address first seen on a C-rated people-search aggregator becomes A-rated the moment it's confirmed against the cadastre or an official filing. Conversely, a fact that looked solid from one source but conflicts with a second, independent source should be downgraded and the conflict noted explicitly rather than silently picking one. Do this re-rating pass deliberately at phase 4, not just in the moment of first finding it — a second look with the full picture in front of you catches conflicts a sequential walk through the tree misses.

**Handling contradictions.** Two sources disagreeing is a finding, not an error to resolve away. Before treating it as a genuine conflict, check the cheap explanation first: are the two sources actually measuring different things? "Company founded 2018" and "company founded 2019" both showing up isn't necessarily a contradiction — a registry's incorporation date and a founder's own account of when they "started the company" (first client, first sale) are both real, different dates. Once you've ruled that out, record a genuine contradiction explicitly rather than picking a winner:
```
Claim A: [fact], source: [URL], retrieved: [date], rated: [X#]
Claim B: [fact], source: [URL], retrieved: [date], rated: [X#]
Same thing, or different things being measured?: [checked — same claim / different
  definitions, not actually contradictory / genuinely conflicting]
Resolution: [which is treated as authoritative and why, climbing toward the more
  primary source — or "unresolved, both retained" if neither clearly wins]
```
Keep both claims in the dossier under the relevant subject's findings even once resolved — the loser is still a data point (where it came from, why it's wrong) and a future reader shouldn't have to take the resolution on faith.

**Build the pivot audit trail while it's fresh.** For each non-obvious finding, note the chain that got you there (seed → finding → source → next pivot). This is tedious to reconstruct after the fact from memory; capture it as you correlate, not as an afterthought when writing the report.

**Decide what's missing, explicitly.** Walk back through every branch of every tree you touched and note which ones returned nothing or weren't pursued (out of scope for the set depth, or genuinely absent). "No LinkedIn found" and "LinkedIn wasn't checked" are different statements — say which one is true for each gap.

**Keep correlation claims separate from direct facts.** A direct observation (a registry filing, a whois record, two images being byte-identical) gets one Admiralty rating. A correlation across signals — "this account is this person", "these companies are the same group", "this is the same site owner" — is a different kind of claim (see the confidence-grid sections in `01`, `02`, `03`, `04`, and `06`) and should never be written as a single Admiralty-rated line as if it were a direct fact. Write it as the claim, the individually-rated signals behind it, the alternative considered, the confidence level (Low/Moderate/High/Inconclusive), and — the part that's easiest to skip — what you specifically checked for that *would have* undermined the claim and what you found. "Alternative considered" names a competing hypothesis; "disconfirming evidence sought" is the harder discipline of actually going looking for the thing that would prove you wrong, not just noting the alternative existed. See the worked example below for the pattern.

---

## Phase 5: Report assembly

One Markdown file, always, following this structure (expanding on the summary in `SKILL.md`):

```markdown
# Dossier: [Target]

## 1. Target
[One paragraph: what the target is, the seed it grew from, the date of this
investigation, and the depth/scope that was set in cadrage (degree 0/1/2 — see
01-people.md's depth-control note).]

## 2. Identity Card
- Name(s) / alias(es): ... [A1]
- Date/place of birth: ... [B2] (if relevant to the engagement)
- Location(s): ... [A2]
- Primary identifiers: email ... [A1], username ... [B1], phone ... [C3],
  registration number (SIREN/SIRET/company no.) ... [A1]
- Affiliations: employer / companies / organizations ... [A2]

## 3. Findings

### 3.1 [Target]
One-line summary.

**Identifiers extracted:** emails, usernames, IDs, IPs, phones, profile URLs,
registration numbers — as a flat list, so a reader (or an automated follow-up)
can lift them directly.

**Notable findings:**
- [Finding], source: [URL], retrieved [date], rating: [X#]
- [Finding with a known validity window], source: [URL], retrieved [date],
  valid [date]–[date or "ongoing as of retrieved date"], rating: [X#]
- ...

**Pivots available:** what this subject opens onto next, and whether it was
followed (and where) or left as a flagged follow-up.

**Annexes:** links to any related files in Annexes/.

### 3.2 [Related entity / person — one subsection per subject]
(same structure as 3.1)

## 4. Pivots Followed
A short audit trail, one line per notable chain:
seed → finding → source → next pivot → outcome.

## 5. What Is Missing
- [Branch/source checked, returned nothing] — itself a signal.
- [Branch not pursued] — out of set depth / out of scope / reason.

## 6. Links Found
A flat, deduplicated list of every social-media/account/profile URL surfaced for
the target (and, if degree ≥1 and relevant, for each linked entity under its own
name) — one URL per line, no commentary, nothing else mixed in. Pulled from the
"Identifiers extracted" lines in section 3, not re-researched; this section is a
quick-reference index, not a new pass. Omit entirely if nothing was found rather
than writing "none found" here (that belongs in section 5 instead).
```

**Add a validity window whenever the fact itself can change, not just a retrieval date.** `retrieved` is when you looked it up; `valid [date]–[date]` is the separate window during which the fact was actually true (see SKILL.md's "when it was true" vs. "when you found it" note). An address, an employer, a company's status, and a breach-exposed identifier all have this distinction; a static fact like a birth date or a company's incorporation date usually doesn't need one.

**Grouping in section 3.** Group by subject, not by source or technique — a reader wants everything known about "the target's business partner" in one place, not everything whois ever returned scattered across the document. Within a subject, order notable findings roughly by significance, not by the order they were discovered.

**The identity card is a summary, not a dump.** It holds the handful of facts that anchor identity (names, core identifiers, location, affiliation). Everything else — however interesting — belongs in section 3's findings, not padded into the card.

---

## The `Annexes/` folder

Create it only when there's non-textual material worth keeping: profile photos, screenshots of pages likely to change or be deleted, downloaded documents, exported CSVs from the headless collector (`automation.md`), video frames. Reference every annex file from the finding that produced it (`see Annexes/profile-photo-jdupont.jpg`), never leave an annex orphaned with no inbound reference. For volatile evidence (a tweet that could be deleted, a listing that could be taken down), snapshot it — Wayback "Save Page Now", archive.today, or a local screenshot into Annexes/ — and keep both the live URL and the archive URL in the finding.

Keep raw harvester output (a CSV from `automation.md`'s collector, a bulk `exiftool` dump) separate from the polished report — if worth keeping, it lives in Annexes/ as supporting material, not inline in the Markdown body.

---

## A worked example (abridged)

```markdown
## 3.1 Jean Dupont (target)
Gérant of Société X SARL, based in Reims; LinkedIn + personal domain confirmed.

**Identifiers extracted:**
- Email: j.dupont@societex.fr [A2]
- LinkedIn: linkedin.com/in/jeandupont-reims [B2]
- SIREN (Société X SARL): 123 456 789 [A1]

**Notable findings:**
- Registered gérant of Société X SARL since 2019-03, source: Pappers.fr
  (societe-x-sarl), retrieved 2026-10-28, rating: A1
- Personal domain jeandupont.fr registered to the same name, whois retrieved
  2026-10-28 via AFNIC, rating: A2 (registrant field not privacy-shielded)
- Home address "possibly 12 rue de la Paix, Reims" per a people-search
  aggregator, rating: D3 — NOT corroborated against the cadastre, flagged
  as unverified rather than included in the identity card
- LinkedIn profile states "Fondateur de Société X, 2018", while Pappers
  gives incorporation 2019-03 — contradiction check: not actually
  conflicting, LinkedIn is dating first commercial activity (pre-
  incorporation freelance work under the same brand), Pappers is dating the
  legal entity's formation. Both retained: LinkedIn claim [B2, valid
  2018–ongoing], Pappers incorporation [A1, valid_from 2019-03].

**Identity-binding claim:** the LinkedIn profile linkedin.com/in/jeandupont-reims
is the same Jean Dupont as the registered gérant.
- Signals: profile photo matches societex.fr's "About" page photo (TinEye,
  exact match) [A1]; profile name matches the registered gérant's name [A1];
  profile's stated employer matches Société X SARL [B2].
- Alternative considered: a different Jean Dupont using the company's own
  staff photo — ruled out, the photo appears on the company's own official
  page, not a third-party source an impersonator could copy from.
- Disconfirming evidence sought: checked whether "Jean Dupont" is a common
  enough name in Reims for a coincidental namesake (queried the name +
  city alone) — the only other regional hits were a different age bracket
  and unrelated profession, nothing that fit as an alternative candidate.
- Confidence: High (three independent signals, one of them a hard image
  match sourced from the target's own domain, plus an active check for a
  namesake that came back empty).

**Pivots available:** Société X SARL co-gérant (→ 3.2, followed); personal
domain's other registrations under the same whois identity (→ not pursued,
beyond set depth).

## 4. Pivots Followed
Seed "Jean Dupont, gérant Société X" → Pappers SIREN record → confirmed
gérant since 2019 → LinkedIn name+employer dork → profile found → profile
photo reverse-imaged (TinEye) → exact match on societex.fr About page →
identity-binding claim recorded at High confidence (name + employer + image,
see 3.1).

## 5. What Is Missing
- No Have I Been Pwned hits for j.dupont@societex.fr — checked, genuinely
  absent as of 2026-10-28.
- Co-gérant's own social presence — not pursued (degree-1 scope; co-gérant
  covered at entity level only, per cadrage).

## 6. Links Found
linkedin.com/in/jeandupont-reims
jeandupont.fr
```

Note the discipline in the example: a juicy-looking aggregator address is flagged D3 and deliberately kept out of the identity card rather than smoothed into an A-rated fact; the identity-binding claim is written out with its own signals and confidence level instead of being compressed into a single misleading Admiralty rating; the apparent founding-date contradiction is checked for a mundane explanation (two different dates, both real) before either source is discarded, and both are kept; the identity binding records an actively-sought namesake check, not just a passively-noted alternative; and "not pursued" is stated explicitly rather than silently omitted.

---

## Common pivots out of this file
- If correlation surfaces a conflict between two sources, climb toward whichever is more primary (`references-by-region.md` for the authoritative registry in a given country) before resolving it.
- If the volume of raw findings is large, a link-graph tool (Maltego CE) or even a plain `draw.io`/`yEd` diagram referenced as an annex can make the entity relationships easier to audit than prose alone — see the visualization row in `references/08-tools-catalog.md`.
