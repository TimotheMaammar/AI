---
name: research-paper-summary
description: "Read a research paper, whitepaper, technical report, preprint, or long technical essay (up to ~150 pages, PDF/HTML/text) from any discipline (AI/ML, biology, physics, economics, social sciences, security, etc.) and produce a structured factual summary following a specific personal format with sections References, Abstract/Summary, Content. Trigger whenever the user shares a scientific paper, an academic preprint, a long technical essay, a research blog post, or a content-heavy PDF and asks for a summary, synthesis, reading note, or breakdown of it. Output is a single Markdown file YYYY-MM-DD_Short_Topic.md, focused on factual extraction (methods, results, numbers, named entities). Output language matches the user's request or defaults to the source language. Do NOT use for code review, security review of product documentation, or non-research content like marketing material or fiction."
---

# Research Paper Summary

This skill reads a research paper, whitepaper, technical report, preprint, or long technical essay from any discipline and produces a structured factual summary.

**Posture: factual extraction.** Preserve numerical data, named entities (institutions, authors, models, methods, benchmarks, datasets), and quantitative results. Avoid popularization, gratuitous criticism, hedging.

**Language**: output in the language the user requests, or by default the source paper's language. Section titles follow the output language consistently.

The format is defined by example in `references/example-summaries.md`. Read that file at the first use of this skill in a conversation. The examples there are in French (the original artifacts) but the structure transposes directly to any language and any discipline.

---

## Output

A single Markdown file named `YYYY-MM-DD_Short_Topic.md` (or `YYYY-MM_Short_Topic.md` when only the month is known), with:

1. **H1 title**: short, evocative name (may differ from the paper's full title).
2. **References section**: paper metadata.
3. **Abstract / Summary section** (optional): 1 to 3 paragraphs of synthesis.
4. **Content section**: development, structure adapted to the paper.
5. **Custom sections** (optional): `Mitigation`, `Related Studies`, or any ad hoc title when content demands.

Length scales with the source. A short article gives a short summary; a long essay or dense paper gives a long summary. No artificial target.

---

## Archetype choice (read first)

Four archetypes. Identify the source paper's type first, then fill the template.

- **A: empirical scientific paper** (method + results + benchmarks). IMRaD structure. Common across all disciplines: ML papers comparing models, biology papers reporting experiments, physics papers with measurements, social science with statistical results. Template: References, Abstract, Content with `Method` / `Results` / `Conclusions` subsections.

- **B: conceptual / theoretical paper** (thesis + framework + implications). Position papers, taxonomy papers, theoretical essays, policy briefs. Template: References, optional Abstract, Content with subsections per concept or a central table.

- **C: short article / single result** (news report, press, short blog post). Template: References, Summary carrying everything, optional Related Studies.

- **D: long essay structured by the author** (manifesto, long-form blog, book-length argument). Template: no formal References, intro in free prose, sections following the source author's own chapter structure.

Choose by structure of the source, not by discipline. A biology essay can be archetype D; a sociology paper with experiments can be archetype A.

---

## Style rules

- **No long dashes** (`—`, `–`) in prose. Use commas, colons, parentheses, periods. Ranges: simple hyphen (`50-55%`).
- **Preserve numerical data and named entities exactly**: percentages, sample sizes, effect sizes, model parameters, p-values, dosages, institution names, instrument names, organism names, etc. No rounding, no paraphrasing into vagueness.
- **Technical vocabulary stays in source form**: keep `MAP-Elites`, `CRISPR-Cas9`, `Shannon entropy`, `GDP`, `IntPhys 2`, `BERT-base`. Brief definition in parentheses on first use only if obscure.
- **Tables for structured comparisons** (multiple items compared on common dimensions). Don't invent a table when the paper doesn't compare anything.
- **Bulleted/numbered lists** for enumerations. Numbered when order matters.
- **Inline external links** as `- <URL>` bullets under the relevant paragraph, like in the Dario example. Don't invent links.
- **Direct, factual tone**: no padding ("it is worth noting", "the researchers emphasize"), no gratuitous judgment ("remarkable", "impressive").
- **Neutral voice**: no first person. Describe what the paper does, not what the summarizer thinks.

---

## Workflow

1. **Ingest.** Paper usually loads directly into context. For extraction issues (mangled text, scanned PDFs, multi-column problems), see `references/00-ingestion.md`. For arXiv/bioRxiv papers, prefer the abstract page for the References metadata (cleaner than parsing the PDF).

2. **Identify.** First pass to determine: title, authors, institutions, date, archetype, central thesis or result, key numerical data to preserve, related works mentioned.

3. **Write.** Follow the chosen archetype. Use the output language consistently. Apply style rules.

4. **Verify.** No em-dashes or en-dashes in prose. All important numbers preserved. Filename format correct. H1 evocative. Inline links in the right places.

5. **Deliver.** Write to `/mnt/user-data/outputs/`, present with `present_files`.
