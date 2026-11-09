# 04: Social Media Intelligence (SOCMINT)

Depth on social-media accounts once a username, name, or profile URL is in hand. `01-people.md` gets you *to* an account (via username search or name search); this file is what to *do* once you're looking at one, plus the platform-specific tricks that a generic "check the username everywhere" pass misses.

This file is reached from several places: the person tree's "pseudonym/username search" and "social-media accounts" branches, the company tree's "professional/personal social accounts" branch, and the image tree's "identification of a person/profile/pseudo" branch. Whatever got you here, the method below is the same.

---

## Step 1: find the accounts

Already covered in depth in `01-people.md` and `08-tools-catalog.md` (username section) — WhatsMyName / Instant Username Search [web] first, Sherlock / Maigret [cli] for scripted breadth. The summary: check the handle across platforms, don't stop at the first hit. Then quote-search the bare handle itself in a real browser (`07-dorks-and-search.md`'s recursive-identifier note) — a platform-by-platform tool check only looks at accounts registered under the handle, it misses the handle showing up as a comment, a forum post, or a mention on a page that has nothing to do with any of the platforms you checked.

**Binding multiple accounts to one person.** Same handle on two platforms is a weak signal alone (common handles get squatted/reused by different people). Strengthen the bind with: identical or near-identical bio text, the same external link (a personal site, a Linktree, a portfolio) listed on both, the same profile/banner photo (reverse-image it — people are lazy and reuse images across accounts, this is one of the strongest single signals in the whole skill), consistent writing style/vocabulary/posting times across platforms, and cross-links (platform A's bio links to platform B).

This is a correlation across signals, not a direct observation — rate it like the identity-binding claims in `01-people.md`, with the same Low/Moderate/High/Inconclusive confidence grid, and record the signals individually rather than asserting the bind as settled. Two failure modes cut in opposite directions and both matter: **coincidence** (a common handle, a template bio, a stock avatar producing an accidental "match" between unrelated people) and **deliberate impersonation** (a parody, catfish, or impersonator account that *intentionally* copies a real person's photo, bio, and links to look like them — here the signals agree perfectly and are still wrong). A perfect-looking match is not automatically a stronger bind than a partial one; where impersonation is plausible (a low-follower account mirroring a public figure, inconsistent posting history, a platform known for impersonation), look for a signal the real account controls and an impersonator can't fake — a cross-link the target's *other, already-confirmed* accounts point to, or a platform verification mark — before crediting the bind.

---

## Step 2: profile analysis (once an account is confirmed)

Mine every account the tree in `01-people.md` describes, in this order of yield:

- **Profile + banner photos.** Reverse-image both (`06-geolocation.md`). This is the single highest-leverage move on a fresh account: it bridges to other accounts using the same image, and sometimes to the real identity if the photo is used elsewhere under a real name (a LinkedIn headshot reused as an anonymous forum avatar is a classic unmasking pattern). Treat the hit as a lead until corroborated, not a confirmed unmasking on its own — the same image can have been scraped and reused by someone else entirely (image theft and impersonation are common enough that a photo match alone should stay a candidate link, per the confidence grid above).
- **Content and dates.** Posting timestamps reveal timezone (cluster the hours, correct for likely sleep pattern) and routine (weekday vs. weekend activity, sudden gaps = travel/life events). Topics and phrasing reveal interests, profession, and sometimes location (local slang, regional references, mentions of specific transit lines/landmarks).
- **The activity layer, not just the profile — posts, comments, and likes/reactions, wherever the platform exposes it.** A person's own posts are one data source; what they comment on and react to under *other* people's content is a separate, often richer one — it surfaces communities, opinions, and relationships their own feed never shows (a one-line comment under an unrelated creator's video can be the only public trace of an otherwise quiet account, and still carries a real date and a real opinion/interest signal). Don't stop at "do they have a profile" — check what they've actually engaged with. This is also exactly the kind of content a bare quote-search of the handle surfaces that a platform-by-platform profile check misses (see `01-people.md`'s username-seed note) — a comment left under someone else's post is indexed as that third party's page, not the commenter's own profile, so it won't show up by browsing the account itself.
- **Relations.** Followers/following, frequent likers/commenters, tagged people. This maps family, colleagues, and close contacts — each a pivot, and each a potential corroboration source (a target who locks down their own account rarely controls what their contacts post about them). Same depth budget as `01-people.md`'s associate branch: identify the relevant contacts, bounded pass on the close ones, entity-level (name + relationship) on the rest — a follower graph is the easiest branch in the whole skill to turn into an unbounded crawl.
- **Geolocation signals.** Geotags, recognizable backgrounds (cross with `06-geolocation.md`'s visual-observation method), check-ins, event photos with a venue name, and — rarely, since most platforms strip it — residual EXIF on an uploaded photo.
- **Linked accounts / cross-posting.** Auto-crossposted content (a tweet that's visibly also a Instagram caption, a "via [app]" tag) links accounts directly; a bio listing other handles does the same.

---

## Platform-specific notes

**LinkedIn.** The richest source for professional affiliation, job history, and org-chart mapping, but its own search is deliberately limited for logged-out/non-Premium users. Work around it with Google dorks (`site:linkedin.com/in "company name" "job title"`) rather than LinkedIn's native search. **Read the Activity tab (`/recent-activity/all/`, and its `/comments/`, `/reactions/` sub-tabs), not just the profile.** The profile's own fields (title, employer, education) are the identity card; the activity tab is the activity layer — what they've posted, which posts they've commented on and what they said, what they've liked. Opinions, affiliations, and relationships surface there that the static profile fields never show. Dorking can reach this too (`site:linkedin.com/posts "name"` or `"name"` combined with a quoted phrase from a comment you already have). For enumerating a company's employees at scale beyond manual dorking: **CrossLinked** [cli] (github.com/m8sec/CrossLinked) enumerates employee names via search-engine scraping only — no API key, no login, no direct hit to LinkedIn, the lowest-footprint option. **linkedin2username** [cli] goes further (requires an actual LinkedIn login, then also generates likely username/email formats from the names it scrapes) but ties the activity to your own account and searches against the target's org directly — real footprint, see `00-operational-footprint.md`. **Footprint note:** LinkedIn shows profile owners who viewed them (depending on the viewer's own privacy settings); a logged-in view is attributable, and the Activity tab is part of the same logged-in-view surface. See `00-operational-footprint.md`. **Don't trust LinkedIn's own company auto-tagging for a short or generic employer name.** When a profile's free-text employer field (e.g. "AAA") gets auto-linked to a "Companies" interest or a structured experience entry, LinkedIn's matching can resolve it to the wrong company entirely — a small, newly-created, or acronym-named real employer collides with an unrelated, much larger organization that happens to share the string (observed directly: a French teacher's "teacher chez AAA" auto-linked to a company page with ~100k followers, geographically and sectorally nothing like the real employer, a small Dijon art school also abbreviated AAA). Treat the linked company page as a lead, not a confirmed employer — check that its size/sector/geography plausibly match the person before citing it, and if it doesn't, resolve the real employer the same way as anywhere else in this skill: a dork on the literal abbreviation plus a locating term (city, sector) from the rest of the profile.

**X / Twitter.** Advanced search (`x.com/search-advanced` or query syntax directly: `from:`, `to:`, `since:`, `until:`, `near:`) is more precise than the UI's basic search. Deleted tweets sometimes survive in Wayback/archive.today snapshots or in third-party archival tools. Followers/following lists and the "who liked this" panel are relational pivots. **Twint and snscrape are dead** — X's API lockdown broke the unauthenticated scraping both relied on. Current working alternatives (**Scweet**, **twscrape** [cli]) drive X's own web GraphQL API through an authenticated account's session cookies rather than an API key — this ties the collection to a real logged-in account, so treat it with the same sock-puppet discipline as any other logged-in collection (see "Sock puppets / logged-in collection" below), not as a passive, keyless scrape.

**Facebook.** Native search has been deliberately crippled for years; Facebook "Graph Search"-style querying is mostly gone, but dorking (`site:facebook.com "name" "city"`) and the mobile/basic (`mbasic.facebook.com`) interface, which renders more without JavaScript gating, are common workarounds. Group membership and event RSVPs are strong relational/geographic pivots when visible.

**Instagram.** Geotags on posts/stories (when present), tagged-location pages (browsing a location's tagged-post feed is a reverse way to find people who were at a place), and the followers/following graph. Reverse-image the profile and any posted photos. **Osintgram** [cli] (scripted follower/following/caption/hashtag extraction via Instagram's private API) exists and can go beyond manual reading when it works — but Instagram's API changes periodically break tools like this silently. Check the repo's recent commit/issue activity before relying on it rather than assuming it still works.

**TikTok.** Bio links, duet/stitch chains (who a creator interacts with), and sound/hashtag usage can place someone in a community or location (regional trends, dialect in captions/comments).

**Telegram.** Public channels/groups are searchable and indexable (several third-party Telegram search engines exist); a username resolves to `t.me/username` directly. Unlike most platforms, Telegram often preserves EXIF on shared files, so photos posted there are worth a metadata pass.

**Discord.** No general public search; relies on knowing/finding specific server invite links (searchable via dorks and dedicated Discord-server-list sites) and then reading public channels. Usernames/handles are a direct socmint pivot like any other platform. **Server membership is not publicly enumerable** — there's no way to look up "which servers does user X belong to," and no clean way to pull a server's full member list without being its admin (Bot API + Server Members Intent); a self-bot/user-token scrape works technically but gets flagged and burned fast. Read public channels once you've joined; member-list extraction isn't worth the account risk for what it returns.

**GitHub / GitLab / dev platforms.** A strong pivot for technical targets: commit emails (`git log` on public repos often embeds a real name + email even when the GitHub profile hides it), contribution graphs (activity timezone), starred/forked repos (interests, employer's internal tooling if they starred a private-adjacent public mirror), and organization memberships.

**Dating apps.** Beyond the generic username-check pass, apps that show a "distance to this user" figure (Grindr, Bumble, Hinge, and similar) are trilaterable: read the distance from three or more vantage points (moving your own account's location, or using several accounts) and intersect the resulting distance circles to pin the target's location. This is real and currently documented — a 2024 academic study found Grindr trilaterable to within roughly 111×111m (set by how it rounds distance) and found similar flaws in Bumble/Hinge letting a target be pinned to within a couple of meters before being patched; Grindr's own "hide distance" toggle has historically still leaked the underlying figure to the client. This requires your own active account repeatedly querying the target's profile/distance feed — directly attributable (see `00-operational-footprint.md`), same sock-puppet discipline as any other logged-in collection. Treat a trilaterated location as a lead to corroborate against an independent source (the cadastre, a reverse directory) before stating it as a finding — it's a location claim, rate it with `06-geolocation.md`'s confidence grid rather than this file's.

**Niche forums, Steam/gaming profiles, Reddit.** All covered by the generic username-check pass; Reddit specifically has no reliable "real name" linkage by design, but comment history across subreddits is a strong location/interest/profession profiler (a user active in a hyper-local subreddit and a niche-profession subreddit together narrows a lot).

---

## Sock puppets / logged-in collection

Several of the richer signals above (LinkedIn connections-of-connections, Facebook group content, Instagram follower lists on a private account) require a logged-in view. See the "Sock puppets / collection identity" section of `08-tools-catalog.md` for the discipline (aged accounts, one persona per operation, consistent fingerprint, never from a device/IP tied to you) and `00-operational-footprint.md` for what a logged-in interaction exposes to the target. This skill does not automate account creation — that stays a manual, deliberate step.

---

## Confidence discipline for account-binding claims

Same grid as `01-people.md`, `02-companies.md`, `03-infrastructure.md`, and `06-geolocation.md` (Low/Moderate/High/Inconclusive, kept consistent across the skill), applied to "these accounts are the same person":

| Confidence | Criteria |
|---|---|
| **Low** | One weak signal only (shared handle, a template bio, a generic/stock avatar) — or a perfect-looking match on a low-follower account mirroring a public figure (impersonation-plausible). |
| **Moderate** | Two or more independent signals agree (e.g. distinctive avatar **and** matching writing style), none individually decisive, and nothing suggests deliberate impersonation. |
| **High** | A signal an impersonator couldn't fake: a cross-link from an *already-confirmed* account, a platform verification mark, a hard identifier (email/phone) tying both accounts together via a breach record or registration data. |
| **Inconclusive** | Signals conflict, or the account shows impersonation/parody markers (inconsistent history, disclaimer in bio, mismatched follower graph) that undercut an otherwise clean-looking match. |

Record it like the other files: the claim, each signal rated individually, the coincidence-or-impersonation alternative considered, disconfirming evidence actively sought (e.g. checked the account's history/follower graph specifically for impersonation markers, not just noted that impersonation is theoretically possible), the confidence level, and the conclusion as worded in the dossier.

---

## Common pivots out of this file
- A bound real identity → `01-people.md`
- A profile/banner photo → reverse-image: `06-geolocation.md`
- A company's employees found via LinkedIn sweep → `02-companies.md`
- An email tied to an account → `05-breaches.md`
- Scripted username/handle sweeps across platforms: `references/08-tools-catalog.md`, `references/automation.md`
