---
name: health-check
description: Run an LLM health check over the knowledge base to surface inconsistent, conflicting, or outdated information across wiki pages and summaries.
argument-hint: [topic or wiki page, optional — omit to run across the full wiki]
---

Run a health check over the knowledge base. Find claims that contradict each other, concepts described differently across sources, outdated information superseded by newer sources, and gaps where related pages make incompatible assumptions.

## Scope

$ARGUMENTS

If no argument is given, run the health check across the full wiki. If a topic or wiki page path is given (e.g. `training/fine-tuning` or `continual learning`), scope the check to that area and its related sources.

---

## Step 1 — Load the index

Read `knowledge-base/qa-index.md` to get an overview of all processed sources: what each covers, its topic tags, and its summary file path.

---

## Step 2 — Identify the scope

**If a specific topic was given:**
- Identify the relevant wiki pages from `knowledge-base/wiki/index.md`
- Identify the relevant summaries from the qa-index entries whose topic tags overlap
- Limit the check to those files

**If no argument was given (full check):**
- Read `knowledge-base/wiki/index.md` to get the full list of wiki pages
- The full check covers all wiki pages and all summaries in `knowledge-base/summaries/`

---

## Step 3 — Read the material

Read all wiki pages and summaries in scope. For each file, note:
- The key claims and quantitative results it makes
- The concepts it defines and how it defines them
- Any explicit comparisons it draws between techniques or approaches

Do not summarize — extract claims precisely, preserving numbers and qualifications.

---

## Step 4 — Detect issues

Look for the following categories of issue across the material you have read:

### Contradictions
Two or more sources make directly opposing claims about the same concept, technique, or result. Examples:
- Different descriptions of what a term means
- Conflicting statements about which approach is better under what conditions
- Numerical results that disagree

### Inconsistent framing
The same concept is described using different terminology, categorization, or framing across pages, in a way that could confuse a reader comparing them. This is softer than a contradiction — both may be technically correct but create a misleading impression when read together.

### Superseded claims
A newer source updates or refutes a claim made in an older source, but the older wiki page has not been updated to reflect this. Look especially at quantitative benchmarks and "state of the art" claims.

### Missing cross-links
Two pages discuss closely related concepts but neither links to the other. Note these only if the missing link would materially help a reader understand the relationship.

### Gaps
A concept is mentioned in passing on multiple pages but has no dedicated wiki entry, and the passing mentions are inconsistent or incomplete.

---

## Step 5 — Write the health check report

Save the report to:

```
knowledge-base/health-checks/YYYY-MM-DD.md
```

Use today's date. Create the `health-checks/` directory if it does not exist.

### Report format

```markdown
# Knowledge Base Health Check — YYYY-MM-DD

**Scope:** full wiki | <topic>  
**Sources checked:** N wiki pages, M summaries  

---

## Contradictions

### [Short title of the issue]
**Pages involved:** [[wiki/page-a]], [[summaries/source-b]]  
**Issue:** One sentence describing the conflict.  
**Detail:** Quote or paraphrase the conflicting claims with enough context to verify them.  
**Suggested fix:** What should be changed, added, or clarified.

...repeat for each contradiction...

---

## Inconsistent Framing

...same structure...

---

## Superseded Claims

...same structure...

---

## Missing Cross-Links

### [Page A] ↔ [Page B]
**Why it matters:** One sentence on the relationship.

...

---

## Gaps

### [Concept name]
**Mentioned in:** [[page-a]], [[page-b]]  
**Issue:** Brief description of what's missing or inconsistent.

---

## Summary

- **Contradictions:** N
- **Inconsistent framing:** N
- **Superseded claims:** N
- **Missing cross-links:** N
- **Gaps:** N
- **Total issues:** N
```

### Quality criteria for the report

- **Specific:** every finding cites the exact pages and quotes or paraphrases the conflicting text — no vague "these pages disagree about X"
- **Actionable:** every finding includes a suggested fix
- **No false positives:** do not flag stylistic variation or intentional nuance as a contradiction; only flag genuine conflicts that could mislead a reader
- **No noise:** missing cross-links are only worth flagging if they would materially help understanding; omit trivial ones

---

## Step 6 — Report

Print a brief summary of findings:
- Path of the report file
- Count of issues by category
- The single most important issue to fix first (your judgment call)
