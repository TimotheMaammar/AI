# Phase 0: Ingestion (adaptive)

**Default path: read directly.** When the file is in context and readable, skip everything below and go straight to phase 1. Most documents land in this case.

Reach for tooling only when something forces it (size, scanned PDF, bad extraction). The rest of this file is the recovery toolbox, not a mandatory checklist.

---

## 0.1 Decide the path (30 seconds)

| Situation | Path |
|---|---|
| File is in context, text reads cleanly, fits comfortably | **Direct read** → go to phase 1 |
| File is in context but text is mangled (encoding artifacts, mojibake, columns interleaved) | **Re-extract** (section 0.3) |
| File is in context but pages are images / I can see them but can't grep them and I need to | **OCR if grep is needed** (section 0.4), else read visually |
| File is very large (rough rule: 300+ dense pages, or 500+ light pages) | **Chunk + map first** (section 0.5) |
| File is referenced but not provided (URL, path, "see also") | **Fetch first** (section 0.2) |
| Multiple related docs exist (admin guide + SDK + release notes) | **Ask for the others** before starting; they're often the juicy ones |

Note the path chosen in one line at the top of the deliverable. Everything else flows from there.

---

## 0.2 Fetching what's not in context

If the doc is a URL the user shared, or the doc references companion docs, fetch them before reading:

- Web doc sites: `web_fetch` for single pages, `wget --mirror --no-parent` for full crawls if many pages.
- JS-rendered doc sites (sometimes return empty HTML on plain fetch): try the search index file (`searchindex.json`) or use a headless browser.
- "See also: Plugin SDK Guide" references in the main doc: ask the user explicitly whether the companion doc is available. Often the most interesting one.

Always check before assuming a doc is the only one: vendors typically publish admin guide + developer/API ref + deployment guide + release notes + security/hardening guide. The doc the user shares is rarely the only useful one.

---

## 0.3 Re-extraction when native reading is bad

Symptoms that warrant re-extraction:
- Mojibake (replacement chars, garbled accented letters)
- Columns interleaved into garbage
- Tables that became unreadable runs of words
- Custom font / glyph mapping causing nonsense even though the file is searchable in a PDF viewer

Tools:

```bash
# PDF: preserve layout (handles columns)
pdftotext -layout input.pdf output.txt

# PDF: per-page range
pdftotext -f 100 -l 120 -layout input.pdf -

# PDF with broken glyph mapping: render to image then OCR (see 0.4)
pdftoppm -png -r 300 input.pdf out_prefix

# HTML: strip nav/footer/chrome
pandoc -f html -t markdown_strict input.html -o output.md
# or
readability-cli input.html > output.md

# DOCX: extract structure + comments + tracked changes
pandoc -f docx -t markdown --track-changes=all input.docx -o output.md

# DOCX raw inspection (it's just zipped XML)
unzip -l input.docx
unzip -p input.docx word/comments.xml
unzip -p input.docx word/document.xml

# Structured table extraction from PDF
python3 -c "
import pdfplumber
with pdfplumber.open('input.pdf') as pdf:
    for page in pdf.pages:
        for table in page.extract_tables():
            print(table)
"
```

---

## 0.4 Scanned / image-only PDFs

If pages are images and reading them visually works for the task, just read visually. OCR is needed only when you'll grep or process the text programmatically.

```bash
# Whole-file OCR (adds a text layer, preserves original)
ocrmypdf input.pdf output.pdf

# Single page OCR
tesseract page.png stdout

# Detect: try extraction first; if output is empty or near-empty, it's scanned
pdftotext input.pdf - | head -50
```

For multi-language docs, specify `-l fra+eng` (or whatever) to tesseract / ocrmypdf.

---

## 0.5 Very large documents (300+ dense pages)

Reading 600 pages exhaustively in one shot loses context. Strategy:

1. **Map first.** Build a section index from the TOC. Don't read content yet.
2. **Pick a reading order.** HIGH-relevance sections first. Within HIGH, parsers/IPC/plugins/auth before generic API.
3. **Per-section reading**: each section gets phases 2 and 3 applied in one pass. Output goes into the annex immediately.
4. **Cross-references.** If a section says "see chapter 18", note it and don't follow immediately. Finish the current section's pass first, then queue chapter 18.
5. **Re-check the synthesis after each major section.** Top juicy findings may shift as new content is read.

Tagging guidance for the section index:

- **HIGH**: API reference, plugin/SDK chapters, admin features, auth/security chapter, configuration deep-dives, "advanced features" appendices, file format specs, IPC details, scripting/templating, integrations, release notes / changelog.
- **MED**: deployment guide, troubleshooting (often reveals failure modes that are themselves bugs), CLI reference, performance tuning.
- **LOW**: UI walkthroughs, theming, installation tutorials, marketing prose, "what is X" intros, branding.
- **NONE**: legal notices, license texts, raw TOC, indexes.

The relevance tagging is a first-pass guess. It's allowed to be wrong; the point is to set a reading order.

---

## 0.6 Set the page-reference scheme

Pick one and use it consistently throughout the deliverable. State it at the top.

- **PDF**: `p.<number>` (Acrobat-displayed page, not internal PDF page index, they often differ by front-matter).
- **HTML**: full URL with section anchor.
- **DOCX / MD**: heading path, e.g. `> Administration > Plugins > Loading custom plugins`.

---

## 0.7 Useful one-time inspections

Worth a single look regardless of path chosen:

```bash
# PDF: metadata sometimes reveals internal codenames, build dates, authoring tools
pdfinfo input.pdf
exiftool input.pdf

# PDF: list embedded attachments (vendor docs occasionally ship sample configs / payloads inside)
pdfdetach -list input.pdf
pdfdetach -saveall input.pdf

# HTML doc sites: the search index is often a flat dump of every searchable term
curl -s https://docs.example.com/searchindex.json | jq .

# DOCX: comments and tracked changes sometimes show internal debate
unzip -p input.docx word/comments.xml
```

These are quick wins, not mandatory. Skip when irrelevant.

---

## 0.8 What ingestion should produce

When this phase is done, you should have:

- The file readable (in context, or extracted, or with a tooling-driven plan to read it).
- A page-reference scheme established.
- A list of any companion docs that exist but weren't provided.
- For very large docs: a section index with HIGH/MED/LOW/NONE tags.

Then move to phase 1. Don't over-engineer this phase. The value is in phases 2 to 5.
