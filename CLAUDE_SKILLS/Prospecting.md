---
name: prospecting
description: >
  Find genuine, verified opportunities (job postings, leads, contacts, etc.) at scale
  using targeted Google dorks across a wide diversity of unknown domains, then confirm
  each candidate in a real browser before adding it to a deliverable.

  Deliberately excludes major aggregators (LinkedIn, Indeed, Glassdoor, Monster, etc.),
  since those are usually already covered separately. This skill complements them
  instead of duplicating them.

  Useful for any task that calls for a scaled, verified list of direct links to apply,
  contact, or reach out through.
---

# Prospecting - Dork-driven sourcing with browser verification

## Goal

Produce a list of verified, direct links, with one genuine action page per result
(application form, apply button, contact form, lead form, etc.).

Target:

* At least 30-40 unique sources to start.
* One domain counts as one source.
* Do not pad the count with many listings from the same domain.
* Diversity of domains matters more than raw volume.

---

## Excluded by default

Do not source from major generalist aggregators that the user is likely already
covering independently:

* LinkedIn
* Indeed
* Glassdoor
* Monster
* Similar broad job or lead boards

This skill exists to complement those sources, not duplicate them.

Including one of these domains should be treated as a deliberate, explicit exception.

---

# Step 1 - Build and run dorks

Use combinations of:

* `inurl:`
* `intitle:`
* quoted phrases
* `OR`
* `-site:`
* every other dork you can think of

to surface domains we do not already know about.

### Important

Avoid using `site:` as a targeting operator.

Querying a specific known domain simply re-finds information we would already think
to check ourselves.

The purpose of dorking is discovery of unknown or secondary sources, not searching
within known targets.

The only legitimate use of `site:` is exclusion:

```text
-site:linkedin.com
-site:indeed.com
-site:glassdoor.com
-site:monster.com
```

so that results surface direct company pages and lesser-known sources.

### Process

1. Start from the dork list contained in `dorks.txt`.
2. Each dork is stored on its own line and prefixed with `-`.
3. Replace the `<keyword>` placeholder with the current topic, role, niche, or lead type.
4. If a dork returns few usable results:

   * derive variations,
   * swap keywords,
   * change operators,
   * try alternate phrasings,
   * continue exploring that line of inquiry.
5. New dorks may be created whenever the existing list runs dry.
6. Paginate manually through results.
7. Rough guideline:

   * approximately 10-20 pages per dork,
   * fewer if several consecutive pages produce no new domains.

### Search engine blocking

If a search engine presents a CAPTCHA or blocks requests:

* Don't attempt to bypass it.
* Slow down.
* Space out requests.
* Pause for an extended period if necessary.
* Fall back to Bing or DuckDuckGo when appropriate.

---

# Step 2 - Verify every candidate in a real browser

Never include a raw search result without opening and validating it.

### Verification workflow

#### 1. Initial filtering

Skip excluded aggregator domains unless explicitly instructed otherwise.

#### 2. Open the candidate URL

Navigate directly to the page.

#### 3. Look for an action mechanism

Examples:

* Apply button
* Application form
* Contact form
* Lead submission form
* Direct response mechanism
* ...

Use:

* visual inspection,
* page text review,
* natural-language element search.

#### 4. Classify

##### VERIFIED

The action mechanism is present and active.

Keep the exact URL.

##### REJECTED

The page is:

* expired,
* closed,
* unavailable,
* removed,
* clearly inactive.

Discard it.

##### NEEDS DIGGING

The page exists but is not yet actionable.

Examples:

* homepage instead of listing,
* category page,
* company careers page.

Continue navigating until the real target page is found.

#### 5. Work in batches

Perform browser actions in batches whenever possible to increase throughput.

#### 6. Deduplicate

Remove duplicates by exact URL before adding them to the final deliverable.

The same page may appear under multiple dorks.

---

# Step 3 - Export

Compile verified results into the requested deliverable.

Spreadsheet format is preferred by default.

For each row include:

* Title
* Exact verified URL
* Source domain
* Originating dork
* Short verification note

Track unique domains separately to ensure the diversity target has been met.

---

# Constraints (always apply)

### No form submission

Never:

* submit,
* complete,
* fake-complete,
* test-submit

any application form, contact form, or lead form.

Detection only.

The user performs any actual interaction afterward.

### No CAPTCHA circumvention

Never attempt to bypass:

* CAPTCHAs,
* anti-bot protections,
* access restrictions.

Acceptable responses:

* normal browsing pace,
* spacing requests,
* long pauses,
* alternate search engines.

If a page is blocked by a CAPTCHA and cannot be verified, do not discard it. Collect it separately and append it to the end of the deliverable with a note indicating that verification was not possible.

### Diversity over volume

Prefer:

* 30-40 domains with one result each

over:

* 30-40 results from only a handful of domains.

Domain diversity is the primary objective.

---

# Companion file

`dorks.txt`

A continuously maintained list of reusable dorks.

Rules:

* One dork per line.
* Each line prefixed with `-`.
* Use `<keyword>` placeholders where appropriate.
* Extend over time as:

  * new niches are discovered,
  * new ATS platforms appear,
  * new search patterns prove effective.

The dork library is a living asset and should improve with every sourcing session.

# References

- Google search operators:
  https://ahrefs.com/blog/google-advanced-search-operators/

