# Citation Management & Hallucination Prevention

This reference provides a complete workflow for managing citations with the tools already available in this template, preventing AI-generated citation hallucinations, and maintaining clean bibliographies.

---

## Contents

- [Why Citation Verification Matters](#why-citation-verification-matters)
- [Citation APIs Overview](#citation-apis-overview)
- [Verified Citation Workflow](#verified-citation-workflow)
- [BibTeX Management](#bibtex-management)
- [Common Citation Formats](#common-citation-formats)
- [Troubleshooting](#troubleshooting)

---

## Why Citation Verification Matters

### The Hallucination Problem

Research has documented significant issues with AI-generated citations:
- **~40% error rate** in AI-generated citations (Enago Academy research)
- NeurIPS 2025 found **100+ hallucinated citations** slipped through review
- Common errors include:
  - Fabricated paper titles with real author names
  - Wrong publication venues or years
  - Non-existent papers with plausible metadata
  - Incorrect DOIs or arXiv IDs

### Consequences

- Desk rejection at some venues
- Loss of credibility with reviewers
- Potential retraction if published
- Wasted time chasing non-existent sources

### Solution

**Never generate citations from memory—always verify against authoritative sources.**

---

## Citation APIs Overview

### Primary Sources and Tools

| Tool | Best For |
|------|----------|
| **Semantic Scholar MCP** | ML/AI paper search, citation graphs, author lookups |
| **alphaxiv MCP** | Reading and checking arXiv full text |
| **Zotero MCP** | Saving verified references into a project bibliography |
| **CrossRef / DOI lookup** | DOI metadata and BibTeX retrieval |

### API Selection Guide

```
Need ML paper search? → Semantic Scholar MCP
Need to read the paper body? → alphaxiv MCP
Need to save references? → Zotero MCP
Have DOI, need BibTeX? → CrossRef content negotiation
```

### No Official Google Scholar API

Google Scholar has no official API. Scraping violates ToS. Use SerpApi ($75-275/month) only if Semantic Scholar coverage is insufficient.

---

## Verified Citation Workflow

### 5-Step Process

```
1. SEARCH → Query Semantic Scholar MCP with specific keywords
     ↓
2. VERIFY → Confirm paper exists in 2+ sources
     ↓
3. RETRIEVE → Get BibTeX via DOI content negotiation
     ↓
4. VALIDATE → Confirm the claim appears in source
     ↓
5. ADD → Add verified entry to .bib file
```

### Step 1: Search

Use Semantic Scholar MCP for ML/AI papers. Capture title, year, DOI, arXiv id, and citation count in your notes or bibliography workflow.

### Step 2: Verify Existence

Confirm paper exists in at least two sources:

1. Check the paper in Semantic Scholar MCP.
2. Check DOI metadata via CrossRef or DOI resolution.
3. If it is an arXiv paper, confirm the arXiv entry through alphaxiv.

Accept the citation only when at least two sources agree on the core metadata.

### Step 3: Retrieve BibTeX

Use DOI content negotiation for guaranteed accuracy:

```python
import requests

def doi_to_bibtex(doi: str) -> str:
    """Get verified BibTeX from DOI via CrossRef content negotiation."""
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"},
        allow_redirects=True
    )
    response.raise_for_status()
    return response.text

# Example: "Attention Is All You Need"
bibtex = doi_to_bibtex("10.48550/arXiv.1706.03762")
print(bibtex)
```

### Step 4: Validate Claims

Before citing a paper for a specific claim, verify the claim exists in the abstract or full text. Use alphaxiv for full-text inspection when the abstract is insufficient.

### Step 5: Add to Bibliography

Add the verified entry to your `.bib` file with a consistent key format such as `author_year_firstword`. If you are maintaining a project bibliography in Zotero, save the verified record there as well.

---

## Tool-First Workflow

This template expects citation work to start with MCP tools and DOI metadata checks. Use local scripts only when the user explicitly wants automation and the required environment is already available.

---

## BibTeX Management

### BibTeX vs BibLaTeX

| Feature | BibTeX | BibLaTeX |
|---------|--------|----------|
| Unicode support | Limited | Full |
| Entry types | Standard | Extended (@online, @dataset) |
| Customization | Limited | Highly flexible |
| Backend | bibtex | Biber (recommended) |

**Recommendation**: Use BibLaTeX with Biber for new papers.

### LaTeX Setup

```latex
% In preamble
\usepackage[
    backend=biber,
    style=numeric,
    sorting=none
]{biblatex}
\addbibresource{references.bib}

% In document
\cite{vaswani_2017_attention}

% At end
\printbibliography
```

### Citation Commands

```latex
\cite{key}      % Numeric: [1]
\citep{key}     % Parenthetical: (Author, 2020)
\citet{key}     % Textual: Author (2020)
\citeauthor{key} % Just author name
\citeyear{key}  % Just year
```

### Consistent Citation Keys

Use format: `author_year_firstword`

```
vaswani_2017_attention
devlin_2019_bert
brown_2020_language
```

---

## Common Citation Formats

### Conference Paper

```bibtex
@inproceedings{vaswani_2017_attention,
  title = {Attention Is All You Need},
  author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and
            Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and
            Kaiser, Lukasz and Polosukhin, Illia},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {30},
  year = {2017},
  publisher = {Curran Associates, Inc.}
}
```

### Journal Article

```bibtex
@article{hochreiter_1997_long,
  title = {Long Short-Term Memory},
  author = {Hochreiter, Sepp and Schmidhuber, J{\"u}rgen},
  journal = {Neural Computation},
  volume = {9},
  number = {8},
  pages = {1735--1780},
  year = {1997},
  publisher = {MIT Press}
}
```

### arXiv Preprint

```bibtex
@misc{brown_2020_language,
  title = {Language Models are Few-Shot Learners},
  author = {Brown, Tom and Mann, Benjamin and Ryder, Nick and others},
  year = {2020},
  eprint = {2005.14165},
  archiveprefix = {arXiv},
  primaryclass = {cs.CL}
}
```

---

## Troubleshooting

### Common Issues

**Issue: Semantic Scholar returns no results**
- Try more specific keywords
- Check spelling of author names
- Use quotation marks for exact phrases

**Issue: DOI doesn't resolve to BibTeX**
- DOI may be registered but not linked to CrossRef
- Try arXiv ID instead if available
- Generate BibTeX from metadata manually

**Issue: Rate limiting errors**
- Add delays between requests (1-3 seconds)
- Use API key if available
- Cache results to avoid repeat queries

**Issue: Encoding problems in BibTeX**
- Use proper LaTeX escaping: `{\"u}` for ü
- Ensure file is UTF-8 encoded
- Use BibLaTeX with Biber for better Unicode

### Verification Checklist

Before adding a citation:

- [ ] Paper found in at least 2 sources
- [ ] DOI or arXiv ID verified
- [ ] BibTeX retrieved (not generated from memory)
- [ ] Entry type correct (@inproceedings vs @article)
- [ ] Author names complete and correctly formatted
- [ ] Year and venue verified
- [ ] Citation key follows consistent format

---

## Additional Resources

**APIs:**
- Semantic Scholar: https://api.semanticscholar.org/api-docs/
- CrossRef: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- arXiv: https://info.arxiv.org/help/api/basics.html
- OpenAlex: https://docs.openalex.org/

**Verification Tools:**
- Citely: https://citely.ai/citation-checker
- ReciteWorks: https://reciteworks.com/
