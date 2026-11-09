# 05: Breaches, Leaks, and Pastes

Checking whether an identifier (email, username, phone, domain) appears in a data breach, a leak corpus, or a paste. This is one of the highest-signal, lowest-effort branches in the whole skill — a breach record can hand you a password-reuse pattern, a secondary email, a real name behind a pseudonym, or a phone number, all in one query.

Reached from: the person tree's email/phone branches, the company tree's data-breach branch, and the socmint file's account-binding step.

---

## What the tools actually give you

HIBP/DeHashed/LeakCheck/etc. tell you *whether* and *where* an identifier was exposed, and sometimes which data classes (password, phone, address) — that's the exposure fact, and it's enough evidence on its own (a dated screenshot/export of the "exposed in [breach name]" result). A raw dump itself is a different, heavier thing to handle — most of what you need is answered by the index without ever touching one.

**Evidence without the dump.** The evidentiary record for a breach finding is the index's own confirmation screen, not raw data. Cite it the normal way (source, retrieval date, Admiralty rating) and, if it goes to `Annexes/`, store the confirmation screen only.

---

## Query-first sources

| Tool | Tag | Use |
|---|---|---|
| Have I Been Pwned (haveibeenpwned.com) | [web] | The free, authoritative first move for any email or phone. Shows which named breaches an identifier appeared in, with a short description of what data class each breach exposed (password hash, address, phone, etc. — not the data itself). Also has a "Pastes" tab and a domain-level search for verified domain owners. |
| DeHashed | [web] | Paid, deeper: searchable by email, username, phone, IP, name, and sometimes returns password hashes/plaintext fields directly. Treat anything beyond the exposure fact itself with care — see "The line" above. |
| LeakCheck | [web] | Similar to DeHashed, different corpus coverage; cross-check both. |
| Snusbase | [web] | Paid breach search, strong on username/IP pivots in addition to email. |
| Intelligence X (intelx.io) | [web] | Broader than breach dumps alone: pastes, leaked documents, darkweb-indexed selectors, historical web snapshots — searchable by email, domain, username, phone, Bitcoin address, and more. Freemium. |
| h8mail | [cli] | Aggregates breach hunting for an email across multiple sources/APIs in one run: `h8mail -t target@mail.com`. Good when you need HIBP + a couple of paid sources checked in one pass. |
| holehe | [cli] | Not a breach source per se, but adjacent: checks which online services have an account registered to an email via password-reset/signup-flow responses. `holehe target@mail.com --only-used`. **Footprint note:** some providers email the account owner about the reset/signup attempt this triggers — see `00-operational-footprint.md`. |

Start with HIBP every time (free, fast, authoritative for "was this exposed at all"). Escalate to DeHashed/LeakCheck/IntelX only when the engagement needs the specific exposed fields (e.g. to confirm a password-reuse hypothesis or pull a secondary identifier), and treat those results with the sourcing care described above.

---

## Paste sites and public leak dumps

Dorking paste/code-sharing sites directly often surfaces exposed credentials, internal configs, or API keys that never made it into a formal "breach" index:

```
site:pastebin.com "target.com"
site:pastebin.com "target@email.com"
site:ghostbin.com "target.com"
site:gist.github.com "target.com" password
site:trello.com "target.com"  (misconfigured public boards)
"target.com" site:controlc.com OR site:rentry.co OR site:paste.ee
```

GitHub/GitLab itself is a frequent accidental-leak source: dork or use GitHub's own code search for `filename:.env "target.com"`, hardcoded API keys, or committed credentials — see the `js-analysis` skill if the leak is embedded in shipped JS rather than a repo.

---

## What a breach hit gives you

- **A secondary email or username** the target used at signup — often less guarded than their primary, and a fresh pivot into `01-people.md` / `04-socmint.md`.
- **A phone number** tied to the same account — pivot into the phone-anchoring steps in `01-people.md`.
- **A password (hash or, in older/sloppier breaches, plaintext) or a password pattern.** The OSINT value is pattern analysis — does the person reuse passwords, what does the pattern suggest about other accounts to check. Testing a recovered credential against a live account is a different skill (`bug-bounty-web`'s authorized credential-stuffing tooling), not this one.
- **A physical address or other PII** present in some breach data classes — corroborate against a primary source (the cadastre, an official registry) before rating it above a C/3; breach data is frequently stale or was wrong at collection time.

---

## Rating breach findings

Breach data sits in an unusual spot on the Admiralty scale: the *index confirming exposure* (HIBP saying "this email was in the LinkedIn 2012 breach") is about as reliable as sourcing gets for the narrow fact of exposure (A1/A2 for "exposed: yes"), but any *specific data field* recovered from the breach (an address, a password, a phone number) is only as reliable as the breach's own data quality at the time of collection — rate those fields independently, typically C or lower until corroborated elsewhere, since breach data is routinely stale, deduplicated sloppily, or includes bot/junk signups.

**An exposure fact is anchored to the breach date, not to the target today.** The email/phone that was exposed belonged to whoever controlled it *at the time of the breach* — a shared family inbox, a former-employee address later reassigned to someone else, or an account the target abandoned years before the breach can all attribute a hit to the wrong current person. Before folding a breach finding into the target's identity card, check the timeline is plausible (did the target already control that identifier by the breach date?) rather than assuming current ownership backward in time.

---

## Common pivots out of this file
- Secondary email/username surfaced → `01-people.md`, `04-socmint.md`
- Phone number surfaced → `01-people.md` (phone anchoring)
- Company-wide exposure pattern (many `@company.com` hits) → `02-companies.md`, worth a note on the company's own security posture if the engagement has a defensive angle
- Credentials in scope for authorized testing → hand off to `bug-bounty-web` / the engagement's own authorized tooling, never actioned from within this skill
