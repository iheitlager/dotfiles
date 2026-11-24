---
model: sonnet
---
Deep research on a topic using parallel subagents across academic and web sources, with critical analysis against the knowledge base and iterative deepening.

## Usage

```
/research <topic>              Full pipeline (all 4 passes)
/research <topic> --quick      Pass 1 only — gather + validate, no critique
/research <topic> --no-deepen  Pass 1+2, skip deepening
/research validate <file>      Validate references in an existing file
```

## Architecture

Four-pass pipeline: Gather → Critique → Deepen → Integrate.

```
┌─────────────────────────────────────────────────────────────────┐
│  PASS 1: GATHER                                                 │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ arXiv +  │  │ Semantic │  │ Web +    │   3 parallel agents   │
│  │ OpenAlex │  │ Scholar  │  │ HN/blogs │                       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       └──────────────┼──────────────┘                           │
│                      ▼                                          │
│           Deduplicate → Rank → Validate (refcheck)              │
│                      │                                          │
│  ════════════════════╪══════════════════════════════════════     │
│                      ▼                                          │
│  PASS 2: CRITIQUE                                               │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ KB Relevance │ │ Novelty      │ │ Conflict     │            │
│  │ Agent        │ │ Agent        │ │ Agent        │  3 parallel │
│  │              │ │              │ │              │            │
│  │ grep KB for  │ │ New vs known │ │ Contradicts  │            │
│  │ connections. │ │ vs extends.  │ │ findings or  │            │
│  │ Score 0-3.   │ │ Justify.     │ │ KB? How?     │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│                 Critical Synthesis                               │
│                          │                                      │
│  ════════════════════════╪══════════════════════════════════     │
│                          ▼                                      │
│  PASS 3: DEEPEN (conditional: relevance ≥ 2 AND novel)          │
│                                                                 │
│  For each qualifying finding:                                   │
│    → Forward citations (who cites this?)                        │
│    → Backward citations (what does it build on?)                │
│    → Rebuttal search (critiques, responses)                     │
│    → Re-validate new papers                                     │
│                          │                                      │
│  ════════════════════════╪══════════════════════════════════     │
│                          ▼                                      │
│  PASS 4: INTEGRATE                                              │
│                                                                 │
│  Recommend KB updates (don't auto-write):                       │
│    → Which domain files to update                               │
│    → Which ideas.md entries supported/refuted                   │
│    → ADR or spec changes warranted?                             │
└─────────────────────────────────────────────────────────────────┘
```

## Process

### 1. Parse Query

Extract from input:
- **Topic**: the research subject
- **Scope**: narrow (specific paper/claim) vs broad (literature review)
- **Time range**: recent (last 2 years) vs comprehensive (all time)
- **Flags**: `--quick`, `--no-deepen`

---

## PASS 1: GATHER

### 2. Launch Search Agents (parallel)

Spawn three agents simultaneously:

**Agent 1: Academic Search (arXiv + OpenAlex)**
```
Agent tool:
  subagent_type: Explore
  prompt: |
    Search for academic papers on: "$TOPIC"

    Sources to query:
    1. arXiv (cs.AI, cs.SE, cs.LG, cs.CL sections)
       - Use WebFetch on: https://arxiv.org/search/?query=$ENCODED_TOPIC&searchtype=all
    2. OpenAlex API
       - Use WebFetch on: https://api.openalex.org/works?search=$ENCODED_TOPIC&per_page=20

    For each paper found, extract:
    - Title (exact)
    - Authors (first author + "et al" if multiple)
    - Year
    - arXiv ID or DOI if available
    - Abstract snippet (1-2 sentences)
    - Citation count if available

    Return as a numbered list, most relevant first. Max 15 papers.
```

**Agent 2: Citation Networks (Semantic Scholar + Crossref)**
```
Agent tool:
  subagent_type: Explore
  prompt: |
    Search citation databases for: "$TOPIC"

    Sources to query:
    1. Semantic Scholar
       - Use WebFetch on: https://api.semanticscholar.org/graph/v1/paper/search?query=$ENCODED_TOPIC&limit=20&fields=title,authors,year,citationCount,abstract
    2. Crossref
       - Use WebFetch on: https://api.crossref.org/works?query=$ENCODED_TOPIC&rows=15

    For each paper found, extract:
    - Title (exact)
    - Authors
    - Year
    - DOI
    - Citation count
    - Venue/journal

    Prioritize highly-cited papers and recent work. Return max 15 papers.
```

**Agent 3: Web + Grey Literature**
```
Agent tool:
  subagent_type: general-purpose
  prompt: |
    Search web sources for: "$TOPIC"

    Sources to query (use WebSearch tool):
    1. Site-specific: "site:arxiv.org $TOPIC"
    2. Academic: "$TOPIC research paper 2024 2025 2026"
    3. Tech blogs: "$TOPIC site:distill.pub OR site:lilianweng.github.io OR site:karpathy.github.io"
    4. HN discussions: "site:news.ycombinator.com $TOPIC"
    5. Industry: "$TOPIC Anthropic OR OpenAI OR DeepMind research"

    For each source found, extract:
    - Title
    - URL
    - Author/org if identifiable
    - Date if available
    - 1-sentence summary

    Filter for substantive sources (not news articles about papers — the papers themselves).
    Return max 15 sources.
```

### 3. Collect and Deduplicate

When all agents return:

1. **Merge results** into a single list
2. **Deduplicate** by title similarity (>80% match = same paper)
3. **Rank** by:
   - Citation count (if available)
   - Recency (prefer last 3 years)
   - Source authority (peer-reviewed > preprint > blog)
4. **Keep top 20** for validation

### 4. Validate References

Run the reference checker on each paper:

```bash
for each paper in top_20:
  refcheck \
    --title "$TITLE" \
    --author "$FIRST_AUTHOR" \
    --year $YEAR
```

Mark each reference as:
- ✓ **Validated** — found in academic database with matching metadata
- ⚠ **Partial** — found but metadata differs (title variant, different year)
- ✗ **Unverified** — not found in any database (may be hallucinated)

**If `--quick` flag: stop here. Generate Pass 1 report and offer storage.**

---

## PASS 2: CRITIQUE

### 5. Launch Critique Agents (parallel)

Take the deduplicated, validated findings from Pass 1 and launch three critical agents simultaneously. Each agent receives the full findings list.

**Agent 4: KB Relevance**
```
Agent tool:
  subagent_type: Explore
  prompt: |
    You are a relevance analyst. Given these research findings:

    $FINDINGS_LIST

    Search the knowledge base for connections. For EACH finding, determine:
    1. Which existing project or file does this advance?
    2. How directly actionable is it?

    Search strategy — grep these directories for keyword overlaps:
    - study/ (papers, research, frameworks)
    - work/ (projects, AAE, Cog, agents.md, SBP philosophy)
    - ideas.md (idea backlog)

    Score each finding 0-3:
    - 0 = no connection to any current work
    - 1 = tangentially related (same broad field)
    - 2 = relevant to a specific project or paper
    - 3 = directly actionable (changes a decision, fills a gap, answers an open question)

    Output format per finding:
    | Finding | KB File(s) | Score | Connection |
    |---------|-----------|-------|------------|

    Also flag findings that are ALREADY KNOWN — i.e., the same insight exists
    in the KB under a different source. These are confirming, not novel.
```

**Agent 5: Novelty Assessment**
```
Agent tool:
  subagent_type: Explore
  prompt: |
    You are a novelty analyst. Given these research findings:

    $FINDINGS_LIST

    And the KB relevance hits (files where similar content exists):

    $RELEVANCE_HITS

    Read the matched KB files and classify each finding into exactly one category:

    **NEW** — This information does not exist in the KB in any form.
    Genuinely new concept, data, framework, or empirical result.

    **CONFIRMING** — The KB already contains this insight (possibly from a
    different source or expressed differently). This finding provides
    independent validation. Note WHICH KB entry it confirms.

    **EXTENDING** — The KB has the base concept, but this finding adds
    something: new data, a new angle, a refinement, an application.
    Note WHAT it extends and HOW.

    Output format:
    ### New Knowledge
    - Finding X: <why it's new, what gap it fills>

    ### Confirming Evidence
    - Finding Y confirms `study/ten_laws.md` Law 3 — <explanation>

    ### Extensions
    - Finding Z extends `work/aae.md` AAE-3 — <what it adds>

    Be strict. "New" means genuinely not present, not "phrased differently."
```

**Agent 6: Conflict Detection**
```
Agent tool:
  subagent_type: Explore
  prompt: |
    You are a conflict analyst. Given these research findings:

    $FINDINGS_LIST

    Search for contradictions in two directions:

    1. **Between findings** — do any of the research results contradict each
       other? Different conclusions from similar experiments? Conflicting
       recommendations? Note methodology differences that might explain it.

    2. **Between findings and KB** — read the matched KB files and check:
       does any finding contradict what's already stored? Especially check:
       - study/ten_laws.md (architectural principles)
       - projects/mvl/research.md (language requirements)
       - work/aae.md (maturity framework)
       - study/intent_preservation.md (ISPE model)
       - ideas.md (active ideas and assumptions)

    For each conflict found:
    | Claim A (source) | Claim B (source) | Type | Evidence strength | Resolution suggestion |
    |------------------|------------------|------|-------------------|----------------------|

    Types: factual-contradiction, methodology-disagreement, scope-difference,
    superseded (newer invalidates older), nuance (both right in different contexts)

    If NO conflicts found, say so explicitly — that's a valid finding.
```

### 6. Critical Synthesis

When all three critique agents return:

1. **Merge** relevance scores, novelty classifications, and conflict register
2. **Build the critical analysis section** of the report
3. **Identify deepening candidates**: findings where relevance ≥ 2 AND novelty = "new" or "extending"
4. **If `--no-deepen` flag: stop here. Generate Pass 1+2 report and offer storage.**

---

## PASS 3: DEEPEN

### 7. Iterative Deepening (conditional)

For each finding that qualifies (relevance ≥ 2 AND novel/extending), spawn a deepening agent:

```
Agent tool:
  subagent_type: Explore
  prompt: |
    Deep dive on: "$PAPER_TITLE" by $AUTHORS ($YEAR)

    This paper was flagged as high-relevance and novel for: $CONNECTION_REASON

    Perform three searches:

    1. FORWARD CITATIONS — who cites this paper?
       - Semantic Scholar: https://api.semanticscholar.org/graph/v1/paper/$PAPER_ID/citations?fields=title,authors,year,citationCount&limit=20
       - Look for: extensions, applications, replications

    2. BACKWARD CITATIONS — what does it build on?
       - Semantic Scholar: https://api.semanticscholar.org/graph/v1/paper/$PAPER_ID/references?fields=title,authors,year,citationCount&limit=20
       - Look for: foundational work we should know about

    3. REBUTTALS — does anyone disagree?
       - WebSearch: "$PAPER_TITLE critique OR rebuttal OR response OR comment"
       - WebSearch: "$FIRST_AUTHOR $YEAR response"
       - Look for: methodological critiques, failed replications, corrections

    For each new paper found, extract title, authors, year, DOI/arXiv ID.

    Return:
    - Top 5 forward citations (most cited or most relevant)
    - Top 5 foundational references
    - Any rebuttals or critiques found (even 0 is useful info)
    - One-paragraph assessment: how robust is this finding?
```

### 8. Validate Deeper Papers

Run refcheck on all newly discovered papers from the deepening pass.

---

## PASS 4: INTEGRATE

### 9. Integration Recommendations

Based on all passes, generate actionable recommendations. **Do NOT auto-write to KB files.** Present as a checklist:

```markdown
## Integration Recommendations

### Update existing files
- [ ] `study/ten_laws.md` — Finding X extends Law 3 with empirical data from $PAPER
- [ ] `work/aae.md` line 47 — Finding Y provides a counter-example to the claim that...
- [ ] `projects/mvl/research.md` — Finding Z adds a 12th candidate requirement (session types revisited)

### New knowledge to store
- [ ] New idea for `ideas.md`: "$CONCEPT" — $ONE_LINE_DESCRIPTION
- [ ] New research file: `study/research_$SUBTOPIC.md` — $SCOPE

### Conflicts to resolve
- [ ] `study/intent_preservation.md` claims X, but Finding W says Y — investigate

### Architectural implications
- [ ] Consider ADR: Finding V changes assumption about $TOPIC
- [ ] Spec update: `.openspec/specs/NNN-name/spec.md` — requirement N may need revision

### Papers to read in full
- [ ] $PAPER_1 — highest relevance, likely to change approach to $PROJECT
- [ ] $PAPER_2 — foundational, should be in references.bib
```

---

## Report Format

```markdown
# Research: $TOPIC

**Date:** YYYY-MM-DD
**Passes:** 1-4 (or note which were skipped)
**Status:** N papers validated, M critique findings, K deep-dived

---

## Summary
<3-5 paragraph synthesis — lead with the most important finding>

## Key Papers (validated)

### Foundational
| # | Paper | Authors | Year | Citations | Status |
|---|-------|---------|------|-----------|--------|

### Recent Advances
| # | Paper | Authors | Year | Status |
|---|-------|---------|------|--------|

### Controversial/Emerging
...

## Grey Literature
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|

## Critical Analysis

### Relevance to Current Work
| Finding | KB File(s) | Score | Connection |
|---------|-----------|-------|------------|

### New Knowledge
- <genuinely novel findings, with justification>

### Confirming Evidence
- <things we already knew, now with additional sources>

### Conflicts & Tensions
| Claim A | Claim B | Type | Resolution |
|---------|---------|------|------------|

## Deep Dives
<only for findings that qualified for Pass 3>

### $PAPER_TITLE ($YEAR)
- **Why deepened:** relevance $SCORE, novel because $REASON
- **Forward citations:** <top 5, one line each>
- **Built on:** <top 5 foundational refs>
- **Rebuttals:** <any found, or "none found — finding appears uncontested">
- **Robustness assessment:** <one paragraph>

## Integration Recommendations
- [ ] Update `file.md` — ...
- [ ] New idea: ...
- [ ] Conflict to resolve: ...
- [ ] Read in full: ...

## Validation Summary
- Total sources found: N
- Validated: X (Y%)
- Partial match: Z
- Unverified: W (list for manual review)
- Deep-dive papers validated: D
```

### 10. Offer Storage

Ask: "Store this research to `study/research_$TOPIC.md`?"

If yes:
- Write report to `study/`
- Add validated references to `study/reading_log.md`
- Commit: `research: $TOPIC`

Do NOT auto-execute integration recommendations — present them for human decision.

Input: $ARGUMENTS
