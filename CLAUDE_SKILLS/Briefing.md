---
name: intel-briefing
description: Produce rigorous, decision-oriented research and intelligence briefings on a wide range of subjects — people, organizations, technologies, events, markets, or strategic questions — and deliver them as polished, well-designed PDF reports. Use this skill whenever the user requests an in-depth analysis, research report, briefing, synthesis, dossier, or comprehensive overview, particularly when the task requires gathering, verifying, cross-referencing, and interpreting information from multiple sources. It should also be triggered when the user seeks a thorough understanding of a subject to inform an assessment or decision, even if no specific document format is requested. Apply it whenever factual accuracy, source reliability, analytical depth, or up-to-date information is essential, regardless of the language used. Do NOT use for simple factual lookups that require no substantial research, or for purely creative and promotional writing.
---

# Intel Briefing

Write like a policy adviser or intelligence analyst briefing a busy decision-maker — not like a generic summarizer of whatever the first search results say. The reader should come out *more knowledgeable*, not just more informed about what sources wrote. This is a single self-contained skill file: the stylesheet and the PDF-rendering script below are meant to be written out to disk at run time (see "Final deliverable" at the bottom) rather than kept as separate bundled files.

## Why this matters

A briefing that just paraphrases the top 3 search results is worse than useless — it gives false confidence. The value of this skill is in: retrieving primary sources instead of stopping at snippets, cross-checking claims instead of taking one source's word, separating fact from interpretation from speculation, and surfacing the contradictions and unknowns a decision-maker actually needs to know about. Speed without rigor defeats the purpose.

## Before writing: research

Never write a substantive briefing from memory alone when the topic involves current events, named people/companies/organizations, financial/legal/regulatory facts, statistics, or anything disputed or time-sensitive. Use web search and read the actual source pages — a search snippet is a lead, not evidence. If browsing isn't available, say so explicitly rather than quietly writing from stale knowledge.

**Think independently.** Sources are evidence, not authorities. For each important claim, ask: what's the underlying evidence, who produced it, what's their incentive, is it independently corroborated? Ten articles repeating one press release is still one source, not ten.

**Be selective.** This is not an encyclopedia entry. Include what's decision-relevant, recent, and well-evidenced; cut trivia, padding, and repeated facts.

## Workflow

1. **Scope it.** Pin down the exact subject, time period, and the real question behind the request. If the user names something ambiguous (a person, an acronym, an org), don't silently guess which one — ask if it materially changes the research. Otherwise just proceed.

2. **Map the dimensions that actually matter** for this subject (history, actors, legal/institutional framework, financials, technical substance, controversies, recent developments...) — don't mechanically force every possible angle onto every topic.

3. **Search and read, don't skim snippets.** Search in the original language of the relevant country/institution as well as English when useful. Vary query phrasing to avoid confirmation bias. Follow links to the primary document (filing, transcript, dataset, legal text, paper) whenever one exists.

4. **Rank sources by tier:**
   - **Tier 1 (primary):** official texts, filings, court decisions, transcripts, original datasets, company financial statements, original research/technical docs, direct statements from the people/orgs involved.
   - **Tier 2 (secondary, high quality):** reputable news orgs, specialist press, academic reviews, independent research institutes, named experts with visible methodology.
   - **Tier 3 (supplementary):** think tanks, advocacy groups, industry associations, blogs, forums. Useful for spotting leads and positions, not for establishing facts on their own.
   Official sources aren't automatically neutral — they're authoritative on what an institution formally did, not necessarily on how to interpret it.

5. **Cross-check every major claim, when that's realistically possible.** Aim for two genuinely independent sources per important fact — ideally one primary + one independent secondary. Watch for outlets that all cite the same original source (that's one source, not several). For numbers: check the denominator, units, time period, and whether figures are preliminary/revised/final before comparing anything.
   On a fast-moving or niche subject, a single credible source is sometimes genuinely all that exists — that's not a reason to drop the claim, and it's not a reason to present it with full confidence either. Keep it, and say so plainly in the text (e.g. "selon [source], non vérifié indépendamment ici"), especially when the sole source has a commercial or institutional interest in the claim. The goal is calibrated confidence, not a hard gate that blocks on anything short of two sources.

6. **Actively hunt contradictions, not just confirmations.** Look for conflicting numbers, different definitions of the same metric, missing context, selective quotation, outdated info presented as current, and institutional incentives behind a given framing. When sources genuinely disagree: pin down *what* they disagree about (often it's a methodology or date difference, not a real dispute), compare the underlying evidence, and say which side is better supported *if* that's determinable — otherwise preserve the disagreement and say why it can't be resolved. Never manufacture a fake consensus to look decisive.

7. **Build a short chronology** for anything that evolved over time — key dates, decisions, announcements — and note the date something happened versus the date it was reported.

8. **Then analyze:** what matters most and why, who gains/loses, what could change the picture, which conclusions are solid versus shaky. Don't force a recommendation the evidence doesn't support; for decision-oriented asks, lay out options and trade-offs instead of declaring one answer inevitable.

## Content structure

Adapt length to the ask — a quick question gets a short answer, a genuinely complex strategic question earns the full structure below. Never pad length just to fill it.

- **Executive summary** — 3-7 bullets: the central conclusion, the key facts, the main risk/opportunity, the most important recent development, the main uncertainty if any.
- **Background** — only the history needed to understand the current situation.
- **Key facts and findings** — the verified substance. Tables for comparisons, chronologies, specs, numbers. Every important claim traceable to a source, cited right after the claim.
- **Actors and interests** — who's involved, documented positions and incentives, not inferred motives.
- **Analysis** — what the evidence means: dynamics, implications, trade-offs, competing interpretations, clearly marked as analysis rather than fact.
- **Risks, controversies, counterarguments** — the strongest objections and failure modes. Don't fake balance where the evidence clearly leans one way.
- **Recent developments** — dated, and say whether they change the prior assessment. Skip if purely historical.
- **Key takeaways** — what to remember; for decisions, options/trade-offs/risks and when each makes sense, without prescribing a decision the user's own constraints should drive.
- **Sources** — grouped (primary / secondary / other), title, publisher, date, URL. Only sources that materially matter, not a log of every page opened.

## Writing rules

- Distinguish, explicitly, established fact / stated claim by a named actor / expert interpretation / your own inference / open question. Never dress an inference up as a fact.
- Cite the actual page read, placed right after the claim it supports, not a bibliography dump. If a source was paywalled or unreachable, say so rather than faking having read it.
- Be precise on dates, units, definitions — especially when comparing numbers across sources.
- Neutral tone, dense prose, short paragraphs, bullets and tables where they help scanning. No filler phrases, no false drama, no hedging for its own sake.
- **Default output language: French.** The user is French and expects the briefing itself — title, body, labels, footer — in French by default, even though this skill file is written in English (the usual convention for skill files; it doesn't dictate the output language). Switch to another language only when the user explicitly asks for one, or the context clearly calls for it (e.g. the briefing is meant to be handed to an English-speaking audience). When writing in a language other than French, also pass that language to `--lang` when rendering the PDF (see below) so the HTML's `lang` attribute is correct.

## Final deliverable: a rendered PDF

The reader gets a polished PDF, not a raw Markdown file — this skill's whole point is decision-grade output, and a dense wall of Markdown reads like a draft, not a briefing. The look is an editorial "note de synthèse": serif headline/body, sans-serif labels, a red accent, numbered sections, callout boxes, pull-quotes, a comparison table with status pills, and stat call-outs — not a generic PDF export.

1. **Draft the content first** in plain prose/notes to get the substance and structure right before touching layout.
2. **Materialize the two files below** into a scratch/working directory (e.g. `style.css` and `render_pdf.py`, copied verbatim from the code blocks) — do this once per session, they don't change between briefings.
3. **Write the briefing body as HTML**, reusing the CSS classes shown in "HTML markup pattern" below as-is — don't invent new classes or reinvent the visual system per briefing. Not every element fits every briefing: use the stat call-outs only when there are real standout numbers, the comparison table only when comparing discrete options/items, etc. — pick what fits the content, skip what doesn't.
4. **Render it to PDF**:
   ```
   python render_pdf.py <input.html> <output.pdf> --css style.css --title "<short doc title>" --date "<date, e.g. 19 novembre 2026>" --lang fr
   ```
   `input.html` can be just the body markup — the script wraps it with the stylesheet and Google Fonts automatically. Under the hood it drives a headless browser via Playwright and adds a running footer with the title/date and page numbers. It tries the system's own Edge, then Chrome, before falling back to Playwright's bundled Chromium — so on a normal Windows machine `pip install playwright` is enough, no separate ~300 MB browser download needed. `--lang` defaults to `fr`; pass `--lang en` (or whatever applies) when the briefing is written in another language. If `ModuleNotFoundError: No module named 'playwright'` shows up, run `pip install playwright` once. Only if no Edge/Chrome is found either (rare) do you need `playwright install chromium` as a last resort.
5. Save the PDF somewhere the user will find it and tell them the path.

### HTML markup pattern

The bracketed placeholders below are filled with real content in whatever language the briefing is written in (French by default — see "Writing rules"). The structural labels (class names, section mechanics) stay as shown regardless of language.

```html
<div class="eyebrow">[EYEBROW LABEL — e.g. "NOTE DE SYNTHÈSE" in French, "RESEARCH BRIEFING" in English] · [PLACE, MONTH YEAR]</div>
<h1 class="title">[Briefing title, punchy, 1-2 lines]</h1>

<p class="lead">[Dense lead paragraph, 3-5 lines, with
<strong>key actors</strong> and <strong>stakes</strong> in bold.]</p>

<h2 class="section"><span class="num">1</span> [Section title]</h2>
<p>[Section intro text.]</p>

<!-- Pair/trio of key points in 2 columns (optional) -->
<div class="grid-2">
  <div>
    <h4><span class="num-badge">1</span> [Point A]</h4>
    <p>[Short explanation.]</p>
  </div>
  <div>
    <h4><span class="num-badge">2</span> [Point B]</h4>
    <p>[Short explanation.]</p>
  </div>
</div>

<!-- Callout box for a structuring fact / definition / executive summary -->
<div class="box">
  <p class="box-title">[Box title]</p>
  <ul>
    <li>[Item 1]</li>
    <li>[Item 2]</li>
  </ul>
  <p class="limit">[Caveat or limitation, smaller/greyed out.]</p>
</div>

<!-- Quote or point worth isolating -->
<blockquote class="pull">[Quote or standout point.]</blockquote>

<h3 class="subhead">[Small subsection subhead, uppercase]</h3>

<!-- Table with status pills (the pill is optional) -->
<table class="comparison">
  <thead><tr><th>Item</th><th>Detail</th><th>Status</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>[Name]</strong></td>
      <td>[Description]<br><span class="ref">[Reference/date]</span></td>
      <td><span class="pill green">HIGH</span></td>
    </tr>
  </tbody>
</table>

<!-- Standout key figures (4 max per row) -->
<div class="stats-grid">
  <div><div class="stat-num">[X]</div><div class="stat-label">[caption]</div></div>
  <div><div class="stat-num">[X]</div><div class="stat-label">[caption]</div></div>
</div>

<!-- Closing paragraph -->
<p class="summary"><strong class="lead-in">[Summary lead-in — e.g. "En résumé" / "Key takeaways"]</strong>[final synthesis.]</p>

<!-- Grouped sources -->
<div class="source-group">
  <h4>Primary sources</h4>
  <ul><li><a href="[url]">[Title]</a> — [Publisher], [date]</li></ul>
</div>
```

### style.css

```css
:root {
  --accent: #9c2b22;
  --ink: #1c1a18;
  --muted: #6b655f;
  --rule: #ddd6cd;
  --paper: #fcfaf7;
  --box-bg: #f4f0ea;
  --pill-green-bg: #dcefdd; --pill-green-fg: #1f6b35;
  --pill-amber-bg: #f6ecc9; --pill-amber-fg: #8a6a0a;
  --pill-gray-bg: #e9e5df;  --pill-gray-fg: #57524c;
}

* {
  box-sizing: border-box;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

html { background: var(--paper); }

body {
  font-family: "Source Serif 4", Georgia, "Times New Roman", serif;
  color: var(--ink);
  background: var(--paper);
  font-size: 10.6pt;
  line-height: 1.52;
  max-width: 800px;
  margin: 0 auto;
  -webkit-font-smoothing: antialiased;
}

.eyebrow, .stat-label, th, .pill, h3.subhead, .box .box-title,
.grid-2 h4, .source-group h4, table.comparison td.ref {
  font-family: "Inter", Arial, Helvetica, sans-serif;
}

.eyebrow {
  color: var(--accent);
  font-weight: 700;
  font-size: 8.2pt;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

h1.title {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 23pt;
  font-weight: 700;
  letter-spacing: -0.005em;
  line-height: 1.18;
  margin: 0 0 16px 0;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--ink);
}

p.lead {
  font-size: 11.4pt;
  line-height: 1.55;
  color: #2b2824;
  margin: 0 0 18px 0;
}
p.lead strong { font-weight: 700; color: var(--ink); }

h2.section {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 14.5pt;
  font-weight: 700;
  color: var(--ink);
  margin: 28px 0 11px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--rule);
}
h2.section .num {
  color: var(--accent);
  margin-right: 8px;
}

h3.subhead {
  font-size: 8.6pt;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 18px 0 7px 0;
}

p { margin: 0 0 11px 0; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 30px; margin: 10px 0; }
.grid-2 > div { margin-bottom: 13px; }
.grid-2 h4 {
  font-size: 9.6pt; font-weight: 700; margin: 0 0 4px 0;
  display: flex; align-items: center; gap: 8px;
  color: var(--ink);
}
.grid-2 h4 .num-badge {
  flex: none; width: 18px; height: 18px; border-radius: 50%;
  border: 1.3px solid var(--accent); color: var(--accent);
  background: none; font-size: 8.6pt; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.grid-2 p { margin: 0; font-size: 9.5pt; line-height: 1.45; }

.box {
  background: var(--box-bg);
  border-radius: 2px;
  padding: 13px 17px;
  margin: 15px 0;
}
.box .box-title {
  font-weight: 700; font-size: 8.6pt; letter-spacing: 0.04em; text-transform: uppercase;
  color: var(--muted); margin: 0 0 8px 0;
}
.box ul { margin: 4px 0 0 0; padding-left: 16px; }
.box li { margin-bottom: 5px; font-size: 9.7pt; line-height: 1.42; }
.box li::marker { color: var(--accent); }
.box p.limit { margin: 9px 0 0 0; font-size: 9.1pt; color: var(--muted); line-height: 1.4; }

blockquote.pull {
  border-left: 2.5px solid var(--accent);
  margin: 16px 0;
  padding: 1px 0 1px 15px;
  font-style: italic;
  font-size: 10.1pt;
  color: #3a3631;
}

table.comparison {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0 16px 0;
  font-size: 8.7pt;
}
table.comparison th {
  text-align: left;
  font-size: 7.4pt;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  border-bottom: 1px solid var(--ink);
  padding: 0 8px 6px 0;
}
table.comparison td {
  vertical-align: top;
  padding: 9px 8px 9px 0;
  border-bottom: 1px solid var(--rule);
  line-height: 1.42;
}
table.comparison td strong { display: block; font-family: "Source Serif 4", Georgia, serif; font-size: 9.4pt; }
table.comparison td.ref { color: var(--muted); font-size: 7.8pt; line-height: 1.4; }

.pill {
  display: inline-block;
  font-weight: 700;
  font-size: 7.4pt;
  letter-spacing: 0.02em;
  padding: 3px 9px;
  border-radius: 9px;
  white-space: nowrap;
}
.pill.green { background: var(--pill-green-bg); color: var(--pill-green-fg); }
.pill.amber { background: var(--pill-amber-bg); color: var(--pill-amber-fg); }
.pill.gray  { background: var(--pill-gray-bg);  color: var(--pill-gray-fg); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0 18px;
  margin: 18px 0 20px 0;
}
.stats-grid .stat-num {
  font-family: "Inter", Arial, sans-serif;
  font-size: 20pt; font-weight: 800; color: var(--ink);
  letter-spacing: -0.01em;
  line-height: 1.1;
}
.stats-grid .stat-label {
  font-size: 7.9pt; color: var(--muted); line-height: 1.32; margin-top: 4px;
}

.summary {
  border-top: 1px solid var(--ink);
  padding-top: 12px;
  margin-top: 24px;
  font-size: 10.3pt;
  line-height: 1.5;
}
.summary strong.lead-in {
  font-family: "Inter", Arial, sans-serif;
  font-size: 8.6pt; letter-spacing: 0.05em; text-transform: uppercase;
  display: block; margin-bottom: 6px; color: var(--accent);
}

ul.plain { margin: 6px 0 14px 0; padding-left: 17px; }
ul.plain li { margin-bottom: 6px; font-size: 10.1pt; line-height: 1.48; }
ul.plain li::marker { color: var(--accent); }

a { color: var(--accent); text-decoration: none; }

.source-group h4 {
  font-size: 8.4pt; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
  color: var(--muted); margin: 14px 0 6px 0;
}
.source-group ul { margin: 0 0 4px 0; padding-left: 15px; }
.source-group li { font-size: 8.8pt; margin-bottom: 5px; line-height: 1.4; }

@media print {
  .page-break { break-before: page; }
}
```

### render_pdf.py

```python
#!/usr/bin/env python3
"""Render a briefing HTML file (built with the intel-briefing CSS classes) into a styled PDF.

Usage:
    python render_pdf.py <input.html> <output.pdf> --css <style.css> [--lang fr] [--title "Footer title"] [--date "19 novembre 2026"] [--format A4]

The input HTML only needs a <body> with the briefing markup (eyebrow/title/lead/sections/etc) --
this script wraps it with the stylesheet and Google Fonts, then prints it via headless Chromium
(Playwright), with a running footer (title/date on the left, page number on the right).
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright


def build_full_html(body_html: str, css_path: pathlib.Path, lang: str) -> str:
    # utf-8-sig strips a BOM if one is present (e.g. a tool that materialized this file
    # added one) and behaves exactly like utf-8 otherwise. A stray BOM right before
    # ":root {" silently invalidates that selector, so every var(--...) falls back to
    # transparent/initial -- text styling still works, but box backgrounds, pills and
    # stat colors vanish with no error anywhere. Always read CSS this way.
    css = css_path.read_text(encoding="utf-8-sig")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{body_html}
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_html")
    ap.add_argument("output_pdf")
    ap.add_argument("--css", required=True, help="Path to the briefing stylesheet")
    ap.add_argument("--lang", default="fr", help="HTML lang attribute for the output (default: fr)")
    ap.add_argument("--title", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--format", default="A4", choices=["A4", "Letter"])
    args = ap.parse_args()

    in_path = pathlib.Path(args.input_html).resolve()
    out_path = pathlib.Path(args.output_pdf).resolve()
    css_path = pathlib.Path(args.css).resolve()

    raw = in_path.read_text(encoding="utf-8-sig")
    # Accept either a full <html> doc or a bare body fragment.
    if "<html" in raw.lower():
        full_html = raw
    else:
        full_html = build_full_html(raw, css_path, args.lang)

    staged = in_path.with_suffix(".rendered.html")
    staged.write_text(full_html, encoding="utf-8")

    footer_left = " · ".join(p for p in [args.title, args.date] if p)

    with sync_playwright() as p:
        browser = None
        for channel in ("msedge", "chrome", None):
            try:
                browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
                break
            except Exception:
                continue
        if browser is None:
            raise RuntimeError(
                "No usable browser found. Install Chrome/Edge, or run "
                "'playwright install chromium' and remove the channel loop above."
            )
        page = browser.new_page()
        page.goto(staged.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.pdf(
            path=str(out_path),
            format=args.format,
            print_background=True,
            margin={"top": "16mm", "bottom": "14mm", "left": "16mm", "right": "16mm"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=f"""
            <div style="font-family:Arial,Helvetica,sans-serif;font-size:7.3pt;color:#6b6b6b;
                        width:100%;padding:0 16mm;display:flex;justify-content:space-between;">
              <span>{footer_left}</span>
              <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
            </div>""",
        )
        browser.close()

    staged.unlink(missing_ok=True)
    print(f"PDF written to {out_path}")


if __name__ == "__main__":
    sys.exit(main())
```
