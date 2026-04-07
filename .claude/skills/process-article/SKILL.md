---
name: process-article
description: Process a new raw article or source file into a summary and integrate it into the wiki. Use when the user wants to add a new article to the knowledge base.
argument-hint: <path-to-article>
---

A new article or source needs to be processed into this knowledge base. Follow the steps below exactly and in order.

## Article path

$ARGUMENTS

If no path is given, ask the user which file to process.

---

## Step 1 — Fix images (if applicable)

Check whether the article contains broken image references (inline images whose paths start with a URL like `https%253A` instead of pointing to a local file).

If broken image paths are found, run the fix script:

```bash
python knowledge-base/fix_images.py "$ARGUMENTS"
```

Report how many image references were fixed, or confirm that no fixes were needed.

---

## Step 2 — Read the article

Read the full article. If it is too long to read in one call, read it in sequential chunks until you have covered all of it. Do not skip sections — the summary and wiki integration depend on complete coverage.

---

## Step 3 — Create a summary

Write a structured summary and save it to:

```
knowledge-base/summaries/<Article Title>.md
```

The summary filename must exactly match the article filename (without the directory prefix).

### Summary format

```markdown
# <Article Title>

**Source:** [[raw/articles/<Article Title>]]
**Author:** <author if known>
**Related:** [[summaries/RelatedSummary1]] · [[summaries/RelatedSummary2]]

---

## Core Idea

One short paragraph describing the central thesis or purpose of the article.

---

## <Major Section>

Content synthesized from the article. Use tables where comparisons exist.
Use code blocks for formulas, algorithms, or code snippets.
Use `[[wikilinks]]` to reference other summaries or wiki pages where relevant.

...repeat for each major section...

---

## Key Takeaways

Bullet list of the most important things to remember from this article.
```

### Quality criteria for the summary

- **Comprehensive:** covers every major concept and result in the article
- **Synthesised:** written in your own words — not copied verbatim
- **Concrete:** includes numbers, formulas, and specific results where they matter
- **Cross-linked:** uses `[[wikilinks]]` to connect to related summaries and wiki pages
- **No filler:** omit introductory padding; lead every section with the substance

---

## Step 4 — Identify affected wiki pages

Review the concepts introduced or significantly expanded by this article against the existing wiki pages under `knowledge-base/wiki/`. Ask: which existing wiki pages should mention this article's findings?

Check the wiki index at `knowledge-base/wiki/index.md` for the full page list.

Common mappings:
- Architecture changes → `wiki/architecture/`
- New training technique → `wiki/training/`
- New inference / prompting strategy → `wiki/inference/`
- Evaluation methodology → `wiki/evaluation/`
- Scaling or paradigm shift → `wiki/concepts/`
- RAG, agents, applications → `wiki/applications/`

---

## Step 5 — Update existing wiki pages

For each affected wiki page identified in Step 4:

1. Read the current page
2. Determine where the new information fits (which section, or as a new section)
3. Add the new content — keeping the page's existing style and structure
4. Add a `[[summaries/<Article Title>]]` backlink to the **Sources** line at the top of the page

Do not rewrite sections that are unaffected. Add, don't replace.

---

## Step 6 — Create a new wiki page (if needed)

A new wiki page is warranted when the article introduces a **concept cluster that has no existing home** in the wiki — not just a new detail that fits within an existing page.

If a new page is needed:

1. Choose the correct subdirectory (`architecture/`, `training/`, `inference/`, `evaluation/`, `concepts/`, or `applications/`)
2. Create the file at `knowledge-base/wiki/<subdir>/<concept-name>.md`
3. Follow the wiki page format:

```markdown
# <Concept Name>

**Related:** [[wiki/page1]] · [[wiki/page2]]
**Sources:** [[summaries/<Article Title>]]

---

## <Section>

...content...
```

4. Cross-link from related existing wiki pages to the new page

---

## Step 7 — Update the wiki index

If a new wiki page was created in Step 6, add it to `knowledge-base/wiki/index.md` in the correct section table:

```markdown
| [[subdir/page-name]] | One-line description of what it covers |
```

---

## Step 8 — Report

Summarise what was done:
- Path of the summary file created
- Number of wiki pages updated (list them)
- New wiki page created (if any)
- Image fixes applied (if any)
