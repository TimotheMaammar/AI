# 06: Image / Geolocation

Pivoting on an image or photo. Seed is a picture file, an embedded image on a page, a screenshot, or a frame from a video. Before anything else, be clear about which of three different questions you're actually answering — see "Three distinct goals" below, right after evidence preservation.

The pivot tree below is transcribed from a field-tested mind map. From the central node IMAGE, each branch is an independent analysis you can run on the same file; they combine (EXIF plus reverse-image plus observation together narrow a location far faster than any one alone). Read every branch as producing a **lead with a confidence level**, not a verdict — the confidence grid further down gives the vocabulary for that.

---

## Step 0: scoping and evidence preservation

Before running any analysis, fix what you're actually looking at and where it came from. Skipping this is how an analysis silently drifts onto a re-saved, re-compressed, or substituted copy of the image, and it's what lets a finding be audited or challenged later.

Record this before anything else:
- **The original file, untouched.** Work from a copy; never overwrite or re-save the source through a viewer/editor (most re-saves re-encode the file and can silently strip or alter EXIF).
- **Provenance.** The URL, account, or person the file came from, and the date/time it was collected.
- **Analysis timestamp**, with timezone — later findings ("Street View still showed this as of...") need to be dated against something.
- **A SHA-256 hash of the file** (`exiftool -SHA256Sum` isn't a thing, use `sha256sum image.jpg` or PowerShell's `Get-FileHash`), taken on receipt. This is what proves you analyzed the same file throughout, and it's the first thing to recheck if a "new" copy of the image surfaces mid-investigation — a hash mismatch means it isn't the same file, whatever it looks like.

This costs under a minute and is the difference between a defensible analysis and one that can't survive "are you sure that's the same file you started with?"

---

## Three distinct goals — keep them separate

Everything in this file serves one of three different questions, and conflating them is the most common way an image analysis overclaims:

1. **Authenticating the image** — is it consistent with the source and context it's claimed to come from? (Always relative to a claimed context, not "real" in some absolute sense.)
2. **Geolocating the scene** — where was this taken, based on what's visible in it?
3. **Identifying a person in it** — who is this, by name or account?

Authentication and geolocation work from what the image itself shows and corroborate against public reference data (OSM, Street View, satellite imagery, news archives). Identifying a person is a higher bar: a real false-positive rate, and look-alikes/homonyms that pass a casual check. Don't let a geolocation finding slide into a person-identification claim (or vice versa) without re-checking which bar applies — see "Identifying a person" near the end of this file before pursuing that branch.

---

## Pivot tree: IMAGE

```
IMAGE
├── EXIF data
│   ├── date taken
│   ├── device / camera model
│   ├── software version (editing history, re-saves)
│   └── GPS coordinates  ──► candidate location, if present (still corroborate — see below)
│
├── file name / file properties
│   ├── date / file properties (creation, modification, size, format)
│   └── general search on the file name  ──► where else it was posted, original context
│
├── manipulation / tampering check
│   ├── FotoForensics, Forensically  ──► Error Level Analysis, clone/splice detection (indicators, not proof)
│   └── steganography check  ──► hidden payload in the file
│
├── visual observation (read the image itself)
│   ├── street signs, shop signs, license plates, notable features
│   │   └── targeted search on those elements (brand, sign text, architecture style)
│   └── Overpass Turbo  ──► query OpenStreetMap for the combination of features seen
│
├── reverse image search (Google Lens/Images, Bing, Yandex, TinEye)
│   ├── location identification
│   │   ├── Maps / Street View / Photosphere  ──► visually match the scene
│   │   ├── reviews/comments left by other users on a matched place
│   │   └── the same photo posted by a person/pseudo elsewhere  ──► pivot to that account
│   └── candidate identification of a person / profile / pseudo  ──► the photo (or a crop
│       of it) surfaces on a profile or in a post tied to a name or handle (lead, not proof)
│
└── face recognition (PimEyes, Yandex, Facecheck.id)
    └── candidate identification of a person / profile / pseudo (lead, not proof — see below)
```

And once a location is a genuine candidate (not yet confirmed — see the geolocation method below):

```
CANDIDATE LOCATION
└── postal address
    ├── cadastre / land registry  ──► owner: person / company / organization
    ├── reverse directory (annuaire inversé)  ──► who/what is registered at that address
    └── search on the address  ──► news, listings, other mentions
```

Two structural points worth internalizing:
- **EXIF and reverse-image are complementary, not interchangeable.** EXIF (when present) is the fastest path to a candidate location and timestamp, but it is self-reported data embedded by a camera/app and can be edited or copied between files just like any other metadata — it narrows the search, it doesn't close it. Reverse-image is what carries the weight once EXIF has been stripped (the default on most social platforms, see below) and is the only branch that surfaces *publication history*.
- **A location pivots straight into `02-companies.md` and `01-people.md`.** An address is not an endpoint; the cadastre and the reverse directory turn it back into entities and people — but only once the location itself has cleared the verification steps below.

---

## Step 1: metadata (EXIF / IPTC / XMP)

A good first move — free and instant when it works — but EXIF alone is a lead, not proof of authenticity. A plausible `DateTimeOriginal` and GPS tag are consistent with the claimed origin; they don't rule out the file having been edited, had its metadata copied from another file, or had fields hand-set by a tool. Treat anything EXIF tells you as one clue to corroborate, not a conclusion.

| Tool | Tag | Use |
|---|---|---|
| exiftool | [cli] | The reference tool. `exiftool image.jpg` dumps every tag: GPS, camera make/model, lens, timestamps (original vs. modified — a gap flags editing), software (Photoshop/GIMP/Lightroom signature), thumbnail (sometimes an older, uncropped version survives inside the thumbnail). |
| Jeffrey's EXIF Viewer (exif.regex.info/exif.cgi) | [web] | No-install EXIF reader, plots GPS on a map directly. |
| Metadata2Go, Pic2Map | [web] | Quick web-based EXIF + GPS plot, good for a one-off check. |
| ExifTool GUI / Metapicz | [web] | Alternative web viewers; cross-check two readers since some strip/misparse odd fields. |

**What to pull out specifically:** `DateTimeOriginal` (capture date/time, often more trustworthy than file dates which change on every copy — but still just a tag, not a cryptographic timestamp), `Make`/`Model`/`LensModel` (device, sometimes narrows to a specific phone generation), `Software` (editing tool + version — a photo edited in an app that didn't exist yet contradicts a claimed date, which is a genuinely strong *negative* signal even though a clean `Software` field is not a positive one), `GPSLatitude`/`GPSLongitude`/`GPSAltitude` (candidate location when present), `GPSImgDirection` (compass heading the camera was pointed), `ThumbnailImage` (extract and compare to the main image — mismatches reveal cropping/editing history).

**Pull the embedded thumbnail out and look, don't just note it exists.** Editors are supposed to leave metadata they don't recognize alone, so a JPEG's embedded EXIF thumbnail is frequently the *original, pre-edit* frame even after the main image has been cropped or censored — a crop that removed a face or a license plate from the visible image can leave both intact in the thumbnail. Extract it directly: `exiftool -b -ThumbnailImage image.jpg > thumb.jpg`, then look at it. Compare *content*, not just dimensions — a size mismatch alone isn't proof of anything (thumbnails are legitimately regenerated at their own resolution), but content that differs from the main image is a real, checkable finding.

**Expect EXIF to be stripped.** Facebook, Instagram, Twitter/X, WhatsApp, and most messaging apps strip EXIF (including GPS) on upload for privacy; Telegram and direct file shares/email attachments often don't. A clean EXIF-free file with no GPS is the common case, not a dead end — it just means the rest of the tree carries the weight.

---

## Step 2: file name and file properties

Before anything visual: the filename itself is a lead. A camera's default naming (`IMG_1234.JPG`, `DSC00456.JPG`) tells you little; a renamed, descriptive, or platform-specific filename (`20240512_mairie-reims_manif.jpg`, a WhatsApp `IMG-20240512-WA0007.jpg`, a CMS-generated hash name) tells you the platform of origin, sometimes the uploader's own description, and gives a literal string to search.

- Search the filename verbatim across engines and reverse-image tools — identical filenames across sites indicate re-hosting/scraping, and the earliest indexed instance is a lead on provenance (not necessarily the true original — see the tools-and-limits table below).
- File properties beyond EXIF: exact byte size, dimensions, and format/codec can match (or fail to match) a claimed source (e.g. a "straight from the camera" image that is actually a re-encoded, downscaled copy consistent with a social-media re-upload).
- `strings`/`exiftool -a -G1 -s` on the raw bytes sometimes surfaces embedded comments, GPS in a non-standard field, or editor fingerprints that structured EXIF readers miss.

---

## Step 3: manipulation and tampering check

| Tool | Tag | Use |
|---|---|---|
| FotoForensics (fotoforensics.com) | [web] | Error Level Analysis (ELA): recompression artifacts can highlight spliced/edited regions. Also shows available EXIF/metadata. |
| Forensically (29a.ch/photo-forensics) | [web] | ELA, clone detection, noise analysis, level sweep, magnifier — a fuller forensic toolkit in one page. |
| InVID-WeVerify (browser extension) | [web] | Built for verifying social-media images/videos: forensic filters, keyframe extraction from video, reverse-image shortcuts, metadata viewer, all in one. |
| Ghiro | [cli] | Self-hosted automated forensic image analysis if you need this at scale/repeatedly. |

**Read ELA results as indicators, not verdicts, and expect to need several of them together.** A localized bright patch in an ELA pass is *consistent with* a paste/splice, but differing original compression levels between regions, a simple resave, non-uniform lighting, or JPEG block artifacts near high-contrast edges can produce the same visual signature with no manipulation at all — ELA has a real false-positive rate. The inverse matters just as much: **a uniform ELA response does not establish that an image is unedited.** Careful edits (consistent re-compression, simple color/levels adjustments, crops that don't introduce a splice boundary) routinely leave little or no visible ELA signal. Treat a manipulation call as requiring **multiple independent indicators pointing the same way** — an ELA anomaly plus a metadata inconsistency (e.g. `Software` field showing an editor, or a `ModifyDate` later than `DateTimeOriginal`) plus a context mismatch (the claimed scene doesn't match what geolocation turns up) is a real case; an ELA anomaly alone is not.

**Steganography check.** If there's reason to suspect a hidden payload (unusually large file for its visual complexity, a deliberately shared "innocuous" image in a context that calls for it): `zsteg` [cli] (PNG/BMP, LSB and common stego plugins), `StegOnline` [web] (browser reimplementation of common stego tools, no install), `binwalk` [cli] (carve any embedded/appended file regardless of format), `steghide` [cli] (if a passphrase is suspected/known). This is a rare branch outside CTF/steganography-specific contexts, but costs one command to rule out.

---

## Reproducible geolocation method

Geolocation is the part of this file most worth doing carefully, because it's the branch where a disciplined process pays off the most and a sloppy one fails silently (a confident wrong answer looks identical to a confident right one unless the process is explicit). Work it in four steps.

### Step A — Extract clues
Read the image closely before searching anything (zoom into corners, signage, reflections):
- **Street signs, shop signs, storefronts, license plates, road markings.** A shop sign or chain storefront is searchable by name; road-marking style and signage typography vary distinctively by country. A plate's script/alphabet (Cyrillic, Arabic, Latin-with-diacritics) is a reasonably solid country/region signal — plate *color scheme* claims from random blog guides are frequently wrong (sources disagree with each other on specifics), so verify a color-based claim against each country's own Wikipedia vehicle-registration-plate article rather than a GeoGuessr-meta guide before relying on it.
- **Architecture and infrastructure style.** Building materials, roof style, utility poles vs. buried lines, right-hand vs. left-hand traffic (visible in any street scene). Street-furniture guides claim nationally distinctive styling (pole-base paint colors, bollard shapes) is a strong country signal — treat this the same way as plate colors: a real category of clue, but community "meta" guides visibly contradict each other on the specifics for a given country, so verify against a current, dated photo or an authoritative source before citing a color/shape claim as fact, and never cite the guide itself as the source.
- **Terrain, relief, and vegetation.** Topography and plant species/climate narrow latitude bands and regions independently of anything man-made in frame.
- **Reflections and shadows.** Shop windows, sunglasses, car windows, and puddles can contain a mirrored second scene or the photographer. Shadow length/direction plus capture date/time (from EXIF or stated context) feeds sun-position estimation for time-of-day and, with more work, a latitude band — see the shadow-chronolocation method below.
- **Text in any visible language/script** — narrows country/region and gives literal search strings.
- **A visible WiFi network name (SSID)** in a screenshot, a router's label in frame, or a device's WiFi settings panel — searchable on WiGLE.net (crowdsourced WiFi-AP database) to place it at a specific building. SSIDs aren't unique on their own; cross-check the BSSID (the AP's MAC address) when WiGLE returns more than one plausible hit.
- **If the image itself is (or includes) a Street View capture: the camera generation is a clue in its own right.** Google's Street View rigs have gone through visually distinct generations — a low-resolution capture with a circular blur/"halo" stitching artifact around the sky and the capture vehicle is an older generation; sharper but dull/desaturated colors is a middle generation; high-resolution, vibrant (sometimes oversaturated) colors is the current one. Most countries only ever received one or two generations, and a given generation was only shot across a bounded date range, so identifying it narrows both country/region and capture year at once. A handful of countries (reported: Switzerland, Liechtenstein, Japan) used a distinct low-cost rig with its own visual signature; a visible Street View car/trike with a roof rig is itself sometimes in-frame (reported as common in Nigeria and Tunisia specifically). Documented by the GeoGuessr community's "Plonk It" meta guide and cross-confirmed by independent player write-ups — plonkit.net's own pages render as a JS app that couldn't be fetched directly to double-check the specifics firsthand, so treat the generation-identification method itself as solid but verify any single country's exact camera-era dates against current Street View coverage before relying on them.

### Step B — Generate multiple hypotheses
Don't anchor on the first candidate that "looks right." For each clue (or clue combination), list more than one candidate location where plausible, especially early on. The main failure mode in geolocation is anchoring bias: seizing on the first visually-similar Street View hit and then unconsciously interpreting every subsequent clue to fit it, rather than genuinely testing alternatives. **Combine clues with Overpass Turbo** (overpass-turbo.eu): translate 2–3 solid visual anchors into an OpenStreetMap query (e.g. a roundabout within 100m of a church, a specific chain-store name, a particular road-junction shape) and let OSM's tagged data return candidates, rather than scanning a map by eye (Bellingcat's OSM-search approach). Overpass times out or chokes on queries run against a large area (a whole country or continent) — narrow the search area first using whatever other clues you have (language/script, terrain, a rough region from any other method) before running a proximity query, rather than querying broad and hoping it resolves.

### Step C — Verify independently
Compare **fixed, permanent elements** — not clouds, parked cars, people, or seasonal foliage — against Street View, Mapillary, KartaView, or satellite imagery: a lamppost's exact position, a building facade's layout, a fixed sign. Require **multiple independent details to match**, not a single "looks similar" impression; one matching feature is coincidence-prone, three or four independently matching fixed features is a real correspondence. Note explicitly when reference imagery (Street View especially) is dated — a multi-year-old capture can show a scene that has since changed, which cuts both ways (a real match to outdated imagery, or a real mismatch because the place changed, not because the candidate is wrong). **Google Earth Pro** (the free desktop app, not Google Maps) has a historical-imagery slider (clock icon in the toolbar) that steps through past satellite captures of the same spot — useful for confirming when a building/feature appeared or changed, which the Maps web view doesn't expose.

### Step D — Document the conclusion
Keep captures/screenshots, the URL for every source checked, which clues concorded, which contradicted, and which alternative candidates were considered and why they were ruled out (or why they remain live alternatives you couldn't fully exclude). This record is what the confidence grade below is actually grounded in, and it's what lets someone else audit or challenge the conclusion later. Use the "Image analysis record" template at the end of this file to capture it.

---

## Chronolocation: pinning down *when*, not just *where*

Two methods narrow the capture time independently of EXIF, useful when metadata is stripped (the common case) or when the claimed date/time itself needs checking.

**Shadow chronolocation.** Once a candidate location is in hand, a visible shadow can estimate time-of-day (and, with more work, help confirm/refute a claimed date): in SunCalc (suncalc.org) or a similar sun-position tool, enter the candidate location, set a reference object's real-world height (a person, a pole, a building edge of known height), then move the time slider until the tool's simulated shadow length-to-height ratio matches what's visible in the image — only the *ratio* matters, not getting the object's exact height right. Bellingcat's **Shadow Finder** tool (search "Bellingcat Shadow Finder" — a 2024 release) automates this across candidate locations instead of manual slider-matching. Reliability conditions: the object and its shadow should be roughly perpendicular to the camera (a shadow running straight toward/away from the lens is hard to measure), the shadow should fall on a level surface (not a slope or steps), and the lens should have minimal distortion (wide-angle/fisheye skews apparent shadow length).

**Transport tracking.** Once location and a rough time window are established some other way, a visible or audible aircraft or vessel in the frame can be matched against historical flight/vessel-tracking data to narrow the time further. FlightRadar24 and ADS-B Exchange give historical flight tracks; OpenSky Network is the research-oriented option with a 30-day history window and an open API. A few concrete gotchas: an aircraft's **ICAO24 hex code** is the identifier to match on, since it persists across repaints and registration changes (unlike the visible tail number, which can change); many military and some corporate/private aircraft are **deliberately excluded** from these public feeds, so absence of a matching track is not proof nothing was flying there. For vessels, MarineTraffic and VesselFinder give historical AIS tracks — AIS position data is self-reported by the vessel and is spoofable, so treat a match as corroborating evidence, not standalone proof.

**Syncing multiple videos of the same event by audio.** When two or more videos of the same event share no common visual frame to line up, a shared sound spike in both audio tracks (a gunshot, an explosion, a camera shutter click, a distinctive bang) can be aligned to synchronize them in time — once synced, you can cross-reference what each camera saw at the same instant, which is often how a scene is reconstructed from several eyewitness angles. This is a forensic-video-analysis technique (the commercial tool Amped FIVE implements it; it's also documented in forensic patent literature), not something tied to any particular investigative outlet — treat the synced timeline itself as solid once the alignment point is a genuinely sharp, shared transient, but still corroborate what each video appears to show rather than over-reading a single frame.

---

## Crowd-sourced activity data (fitness-app heatmaps)

A different kind of source from everything else in this file: instead of analyzing one image, aggregated or individual exercise-tracking data can locate a facility or a person directly.

**Facility/area discovery from an aggregate heatmap.** Strava publishes a continuously-updated global heatmap of subscriber activity (heatmap.strava.com). Dense, geometrically regular jogging/running tracks in an otherwise empty area (a desert, a remote compound) can expose the location and layout of a facility whose personnel use the app during exercise — this is how analysts spotted the outlines of US military bases in Syria/Iraq in a widely-reported January 2018 case. The heatmap is opt-out, not opt-in, and still live today. This is a lead toward a location/facility, not a confirmed one — corroborate the outline against satellite imagery and OSM data (Step C above) before treating it as more than that.

**Home-address inference from an individual's activity map.** The same mechanism works on a single public profile: a person's personal activity heatmap (not just the aggregate) tends to cluster and repeatedly start/stop at the same point — usually home — because routes begin and end there. This is pattern-of-life inference from *repeated* activity, not a single tagged point, and is a distinct technique from reading one photo's EXIF GPS. See `01-people.md`'s socmint/geolocation section for where this fits as a person-pivot, and apply the same scope caution as any other technique that can reveal a private individual's home address.

---

## Confidence grid

Use this grid to state how strong a geolocation (or authentication, or identification) determination actually is, rather than presenting a lead as a certainty. It's an **internal working grid for this skill, not a universal or scientific scale** — state that it's this grid when citing a confidence level in a dossier, so the reader can calibrate against it rather than assume a standardized meaning.

| Level | Criterion |
|---|---|
| **Low** | One ambiguous clue, or a mere resemblance. |
| **Moderate** | Several compatible clues, but plausible alternatives remain. |
| **High** | Several distinctive clues concord, and plausible alternatives have been actively examined and ruled out. |
| **Inconclusive** | The available elements don't allow a determination either way. |

This is a different axis from the NATO Admiralty rating in `SKILL.md`: the Admiralty code rates how reliable a *source* is and how credible a single *claim* from it is; this grid rates how strong the *overall determination* is once multiple clues and sources have been combined. Use both — cite each individual clue with its own Admiralty rating where relevant, and state the combined finding's confidence using this grid. The same grid is reused for correlation claims in `01-people.md`, `02-companies.md`, `03-infrastructure.md`, and `04-socmint.md` — one vocabulary for "how strong is this combined conclusion," wherever in the skill it comes up.

---

## Tools and their limits

Every tool below answers a narrower question than it looks like it does. Know the limit before treating a result as settled.

| Analysis type | Tools | Main limitation |
|---|---|---|
| Metadata | exiftool, Jeffrey's EXIF Viewer, Metadata2Go | Metadata can be absent, stripped by the platform, or deliberately falsified; plausible EXIF is consistent with authenticity, not proof of it. |
| Reverse image search | Google Lens, Yandex, Bing Visual Search, TinEye | Indexes are incomplete and vary by region/subject; no match found means "not indexed by this engine," not "original." |
| Geolocation references | OpenStreetMap / Overpass Turbo, Street View, Mapillary, satellite imagery | Map data and imagery are sometimes outdated or incomplete; a scene can have changed since the reference was captured. |
| Manipulation detection | FotoForensics, Forensically, InVID-WeVerify | An anomaly alone doesn't prove tampering, and a manipulated image can show no obvious artifact — needs multiple independent indicators (see Step 3). |
| Source / publication verification | web search, Wayback Machine, archive.today | The earliest indexed or archived date is not necessarily the true original publication date — an archive only captures what it was pointed at, and when. |

---

## Step 4: reverse image search

Engine performance varies by what's in the image and the index's regional coverage — there isn't a single engine that dominates every case, and claims that one is universally "best" age badly as indexes change. Pick based on what you're trying to find, and cross-check when it matters:

| Image type / goal | Engine(s) worth prioritizing | Why |
|---|---|---|
| Faces, people | Yandex, PimEyes, Facecheck.id | These indexes and models are tuned for facial/visual similarity on partial matches and crops — but see "Identifying a person" before treating a hit as confirmed. |
| Products, brands, objects, in-image text | Google Lens | Strong general object/product recognition plus OCR-in-image. |
| Exact-copy provenance, first-seen date | TinEye | Indexes exact/near-exact duplicates and sorts by first-seen date — the most direct way to find the earliest indexed instance of a re-hosted image (still not necessarily the true original — see the limits table). |
| General scenes, landmarks | Google Lens, Bing Visual Search | Broad general-purpose coverage. |
| Non-Western subjects/locations, Cyrillic-script context | Yandex | Comparatively stronger regional index for CIS/Russian-language content. |

AI-based geolocation (narrowing a scene directly from visual cues via a trained model, rather than reverse-image matching against an index) is a real and improving category — Graylark's GeoSpy, reported January 2025, could narrow a scene to a few square miles from vegetation/architecture/road-surface cues alone. It isn't currently a usable addition to this table: public access was closed after reporting surfaced misuse (stalking requests), and it's now positioned as law-enforcement/government-only. Worth knowing the category exists and keeping an eye on it, not worth treating as an available tool today.

Run more than one engine when the finding matters — faces and scenes especially benefit from cross-checking Yandex against Google and TinEye, since each surfaces different hits. Crop tightly on a face or a distinctive object and re-run if a full-frame search returns nothing; reverse search is sensitive to framing. A miss on one engine and a hit on another is itself just an index-coverage fact, not evidence either way about the image's originality — don't over-read it.

**Crop controls which mode an engine runs in, not just how precise the match is.** A full-body/suited photo fed to Google Lens is read as a clothing/product photo and returns shopping results for the jacket, not the face; the same photo cropped tight to just the face switches Lens into its person/face-similarity mode. Even then, Lens-style "visual matches" on a face are **look-alikes ranked by visual similarity, not an identity match** — this is a different, weaker thing than what PimEyes/Facecheck.id/Yandex actually do (face-recognition models trained to find the *same* person), and the two outputs should never be conflated in the dossier.

**Uploading a local file when the source URL can't be used.** A platform's CDN image URL (Facebook, Instagram, and similar) often carries a signed, session-bound query string — passing that URL through a browser-automation tool's JS/network layer can get redacted as a safety measure against leaking session tokens, which blocks the "paste the image URL" path into a reverse-search engine. The reliable workaround: screenshot the image region directly (a visual pixel capture, not a URL extraction, so no token is ever handled) and save it locally, then upload that local file into the search engine's own upload control. In practice: locate the engine's actual `<input type="file">` via the page's accessibility tree (`read_page`/`find` with an "all"/unfiltered pass, not just "interactive" — the real input is often a styled, zero-size element behind a decorative upload button) and upload to that element directly; clicking the visible "upload" button yourself can instead trigger an invisible native OS file-picker dialog that automation can't see or fill in. Observed behavior by engine: Google Images/Lens and TinEye both expose a reachable file input this way; Yandex's camera-icon flow did not expose one in the page's accessibility tree in testing (opens a native picker directly) — treat that as a known tool limitation, not a dead end, and fall back to TinEye/Google Lens or a different Yandex entry point.

**What a hit gets you:**
- **Location identification (candidate, not confirmed).** A visual match to a known place (via a travel blog, a business's own photos, a news article with a dateline) hands you a candidate location — run it through the geolocation method above (Steps C–D especially) before treating it as settled, the same as any other geolocation lead.
- **Reviews/comments from other users** on a place a reverse search ties the photo to (e.g. a restaurant's Google Maps listing with the same photo among its reviews) can date the visit and sometimes name the poster.
- **The same photo posted by a person/pseudo elsewhere.** This is a direct pivot to a social account — jump to `04-socmint.md` once you have the handle.
- **Candidate identification of a person/profile/pseudo.** If the reverse search (or a face-search engine) surfaces the image attached to a named profile or post, that's a lead bridging "photo of a person" toward "identified person" — read "Identifying a person" below before treating it as more than that.

---

## Identifying a person (read this before pursuing this branch)

This is the branch most prone to false confidence — face-match engines are tuned for recall, not certainty, and will hand you a wrong answer that looks exactly as clean as a right one. Three things to hold onto:

- **A face-recognition hit is a lead, never a confirmed identification.** Treat a PimEyes/Facecheck.id/Yandex face-match hit the way `01-people.md` treats a people-search aggregator: a C/D-rated lead needing independent corroboration — a second, unrelated signal (matching clothing/background across the source photo and the hit, a name mentioned near the hit, the same face+name pairing on a second independent platform) — before it's rated above a 3 on information credibility. Explicitly consider and rule out false positives and homonyms/look-alikes rather than taking the top-ranked result at face value; these engines are tuned for recall, not certainty, and will confidently return a wrong match.
- **State it as a candidate in the dossier, not a conclusion.** Write "candidate match, [confidence level], corroborated by [signal]" or "not yet corroborated" — never collapse a face-search hit straight into an identity-card fact. This is the same discipline `09-deliverables.md` asks for everywhere else, not an exception for images.
- **An image-derived home address pivots exactly like any other address** (`02-companies.md`/`01-people.md`'s cadastre and reverse-directory steps) — flag it in the dossier as image-derived rather than folding it in silently, since the chain to it is weaker than a direct registry hit.

---

## Step 5: from location to entities (the address pivot)

Once a location has cleared the verification steps above (not merely a first-pass candidate), convert it to a postal address and pivot onward exactly as `02-companies.md` and `01-people.md` do from any other address:

- **Cadastre / land registry** → owner of record (person, company, or organization). See `references-by-region.md` for the per-country cadastre/land-registry list (e.g. cadastre.gouv.fr and the Fichiers fonciers/DVF dataset for France).
- **Reverse directory (annuaire inversé)** → other entities registered at the same address (useful when the address is a business premises, not a private residence).
- **General search on the address** (in quotes, with and without postal code) → news mentions, listings, social posts geotagged there.

---

## Image analysis record

Fill this in for any image where authenticity, location, or identity actually matters to the engagement — it's the minimum that lets someone else audit the conclusion later, and it folds directly into the subject's "Notable findings" in the main dossier (`references/09-deliverables.md`) rather than being a separate deliverable.

```
Source file: [filename], SHA-256: [hash]
Provenance: [URL / account / person who supplied it], collected [date]
Analysis date: [date, timezone]

Hypothesis tested: [e.g. "claimed to show location X on date Y"]

Clues found:
- [clue] — source/method: [tool], consulted [date]
- [clue] — source/method: [tool], consulted [date]

Contradictory elements / alternative explanations considered:
- [anything that doesn't fit, or a competing hypothesis, and why it was or
  wasn't ruled out]

Disconfirming evidence actively sought: [what you specifically checked for
  that would have undermined the conclusion if present — not just noting
  that an alternative exists, but having gone and looked for it — and what
  you found]

Confidence level: [Low / Moderate / High / Inconclusive] — [why]

Conclusion: [one or two sentences, scoped to exactly what the evidence
supports — no further]
```

---

## Operational footprint note specific to images

- **PimEyes and other paid face-search engines** retain and sometimes log your queries — factor that into which photos you upload where.
- **Reverse-searching an image hosted at a URL you control fetching** (vs. uploading the file directly) can leak that URL to the search engine's logs; prefer uploading the file itself when the source URL should stay unlinked from the search.
- Full footprint guidance (what tips off a target) is in `references/00-operational-footprint.md` — image work rarely touches the target directly (you're searching third-party indexes), so this branch is one of the quieter ones in the skill.

---

## Common pivots out of this file
- Verified location → address → owner: `02-companies.md`, `01-people.md`
- Candidate person/handle from a reverse-image or face-search hit: `01-people.md`, `04-socmint.md`
- A fitness-app activity heatmap as a person pivot: `01-people.md`
- Region-specific cadastre/land-registry and reverse-directory sources: `references-by-region.md`
- Building better reverse-image / Overpass / dork queries: `references/07-dorks-and-search.md`
- Filing the finished analysis into the dossier: `references/09-deliverables.md`
