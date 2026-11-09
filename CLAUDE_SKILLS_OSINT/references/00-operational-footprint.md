# 00: Operational Footprint

Default mode is exhaustive and aggressive: pull everything, follow every pivot, leave nothing on the table. This file is not about restraint. It is a tactical note about one thing only: **which actions tip off the target.**

Most OSINT is invisible to the target (you query third parties, caches, registries). A handful of actions are different: they touch the target directly or trigger a notification on their side. Know which, so a collection step does not announce itself.

## Actions that can alert the target

- **Email registration / password-reset probes** (holehe and similar): some services email the account owner "someone tried to sign in / reset your password." Per-service behavior varies; assume the loud ones (major providers, banking, some social) may notify.
- **A tool like Ignorant checking existence is not the same action as walking the platform's own recovery flow to identify the account.** Ignorant (and holehe) stop at the initial API response — enough to confirm "an account exists," genuinely quiet. Going one step further, into the platform's own "forgot password" UI, to try to read a masked email/phone hint and identify *which* account it is, is a different and louder action: depending on the platform's flow, submitting the identifier can immediately send a real reset link or code to the account — a completed, attributable notification to the target, not a probe. Treat that as its own explicit decision, not an automatic follow-on to a positive Ignorant hit.
- **Viewing gated profiles while logged in**: LinkedIn shows "who viewed your profile." Some platforms surface viewers or send "X looked at you" nudges. A logged-in view is attributable to whatever account did it.
- **Following / liking / connecting / messaging**: any interaction writes to the target's notifications. Viewing is quieter than interacting.
- **Phone-number lookups on app-based services** (Truecaller, messaging apps): adding or querying a number can expose your account to the target or show you in "who saw my number" style surfaces.
- **Direct fetches of target-controlled pages**: hitting the target's own site, tracking pixels, or shortened links can land in their logs/analytics with your IP and user agent. Prefer search snippets, caches, and archives (Wayback, archive.today) for target-owned pages; they put you against the archive, not the target.
- **SMTP `RCPT TO` verification**: probing a mail server for whether an address exists is logged by some mail systems.
- **Dating-app proximity/distance queries**: repeatedly checking "distance to this user" from different vantage points (to trilaterate a location, see `04-socmint.md`) requires your own active account interacting with the target's profile — more attributable and invasive than most of this skill's techniques, not a passive read.

## Using the operator's own browser and accounts

Per `SKILL.md`'s "don't stay in the sandbox" rule, the normal way to run this skill is through a real browser (Claude in Chrome or the built-in browser pane), not an abstracted tool alone — and that real browser often comes with the operator's own logged-in sessions already available (their Google account, their Facebook, sometimes LinkedIn). This unlocks real depth: an activity feed, a mutual-friends count, a logged-in-only search index, uploading a local file for reverse-image search. Use it.

The discipline this adds, on top of everything above: every logged-in action through the operator's own account is attributable to *them specifically*, not to an anonymous researcher — the "who viewed your profile" and "logged-in view" notes above apply to their real identity. That's a reason to use it deliberately, not a reason to avoid it: ask before using a specific account on a specific platform for a specific target when it's not already obvious from context, note in the dossier that a finding came from a logged-in session, and don't treat "I have the operator's LinkedIn open" as blanket permission to log into every platform for every future target without it coming up again.

**A real browser's autofill can cross-contaminate an investigation with the operator's own identity.** A platform's "forgot password" or recovery field is exactly the kind of input the browser's own saved-logins autofill targets — observed directly: typing a target's phone number into Instagram's account-recovery field triggered a browser-autofill interaction that surfaced the operator's own saved account details (a linked-accounts popup naming their personal recovery email) instead of anything about the target, from a single click near the field. Before typing a target's identifier into any login/recovery/signup field in the operator's own logged-in browser, clear the field deliberately (select-all + delete, not a click that might land on an autofill suggestion) and verify what's actually in it before submitting — otherwise the step can silently act on the operator's own account, or hand back the operator's own data instead of the target's.

## Quieter substitutes

- Read cached/archived copies of target-owned pages instead of fetching live.
- Prefer logged-out or third-party viewers over logged-in views of a target's profile where possible.
- Favor passive infrastructure data (crt.sh, passive DNS, Shodan/Censys scan data) over anything that sends packets to the target.
- When a step is unavoidably loud, do it deliberately and note it, rather than tripping it by accident.

That is the whole point of this file: stay aware of the few noisy actions in an otherwise silent process.
