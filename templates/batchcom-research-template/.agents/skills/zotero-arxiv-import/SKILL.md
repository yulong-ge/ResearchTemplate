---
name: zotero-arxiv-import
description: Use when adding arXiv papers (with PDFs and auto-recognized metadata) to a Zotero collection programmatically, including batch import of reference lists from existing papers.
---

# Zotero arXiv Import

## Overview

Upload arXiv PDFs directly to Zotero via the local connector API. Zotero auto-recognizes metadata (title, authors, arXiv ID, date) and creates a fully populated parent item with the PDF attached — no manual entry needed.

**Key insight:** Use `POST /connector/saveStandaloneAttachment` with binary PDF data, NOT `saveItems`. The `saveItems` endpoint creates metadata-only items without PDFs.

## Prerequisites

- Zotero 7 running locally (exposes `http://localhost:23119`)
- No API key required for local API
- Target collection selected in Zotero UI (items land in the currently selected collection)

## Core Workflow

### Single Paper

```bash
# 1. Download PDF
curl -L --max-time 60 "https://arxiv.org/pdf/XXXX.XXXXX" -o /tmp/paper.pdf

# 2. Upload to Zotero (auto-recognizes metadata)
SESSION="import_$(date +%s)"
curl -s -X POST "http://localhost:23119/connector/saveStandaloneAttachment" \
  -H "Content-Type: application/pdf" \
  -H "X-Metadata: {\"sessionID\": \"$SESSION\", \"url\": \"https://arxiv.org/pdf/XXXX.XXXXX\", \"title\": \"XXXX.XXXXX.pdf\"}" \
  --data-binary @/tmp/paper.pdf

# Expected response: {"canRecognize":true}  HTTP 201

# 3. Wait for metadata recognition (10-15 seconds)
sleep 12

# 4. Verify
curl -s "http://localhost:23119/api/users/<USER_ID>/items?limit=3&sort=dateAdded&direction=desc" \
  -H "Zotero-API-Version: 3"
```

### Batch Import (Python)

```python
import urllib.request, json, subprocess, time, os

ZOTERO_USER_ID = "<zotero-library-id>"  # from http://localhost:23119/api/users
ARXIV_IDS = [
    "2410.06940",  # REPA
    "2502.03444",  # MAE Tokenizers
    # ... more IDs
]

def item_exists(arxiv_id):
    """Check if paper already in Zotero by arXiv ID."""
    url = f"http://localhost:23119/api/users/{ZOTERO_USER_ID}/items?q=arXiv:{arxiv_id}&limit=5"
    req = urllib.request.Request(url, headers={"Zotero-API-Version": "3"})
    with urllib.request.urlopen(req) as r:
        items = json.load(r)
    return any(
        i["data"].get("archiveID", "").endswith(arxiv_id)
        for i in items
    )

def upload_pdf(arxiv_id, pdf_path):
    """Upload PDF to Zotero via saveStandaloneAttachment."""
    session = f"import_{arxiv_id}_{int(time.time())}"
    url_arxiv = f"https://arxiv.org/pdf/{arxiv_id}"
    metadata = json.dumps({"sessionID": session, "url": url_arxiv, "title": f"{arxiv_id}.pdf"})
    
    req = urllib.request.Request(
        "http://localhost:23119/connector/saveStandaloneAttachment",
        data=open(pdf_path, "rb").read(),
        headers={
            "Content-Type": "application/pdf",
            "X-Metadata": metadata,
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        resp = json.load(r)
    return resp.get("canRecognize", False)

for arxiv_id in ARXIV_IDS:
    print(f"[{arxiv_id}] ", end="", flush=True)
    
    # Skip duplicates
    if item_exists(arxiv_id):
        print("SKIP (already in Zotero)")
        continue
    
    # Download PDF
    pdf_path = f"/tmp/{arxiv_id}.pdf"
    try:
        subprocess.run(
            ["curl", "-L", "--max-time", "60", "-o", pdf_path,
             f"https://arxiv.org/pdf/{arxiv_id}"],
            check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print("ERROR (download failed)")
        continue
    
    # Upload to Zotero
    try:
        ok = upload_pdf(arxiv_id, pdf_path)
        print(f"{'OK' if ok else 'WARN: canRecognize=false'}")
    except Exception as e:
        print(f"ERROR ({e})")
    finally:
        os.remove(pdf_path)
    
    time.sleep(3)  # Rate limit: avoid hammering arXiv

print("Done. Wait 15s for Zotero to finish metadata recognition.")
```

## Duplicate Detection

Before uploading, check by arXiv ID:

```python
# Search by arXiv ID
curl -s "http://localhost:23119/api/users/<USER_ID>/items?q=arXiv:2410.06940" \
  -H "Zotero-API-Version: 3" | python3 -c "
import sys, json
items = json.load(sys.stdin)
for i in items:
    d = i['data']
    print(i['key'], d.get('archiveID',''), d.get('title','')[:50])
"
```

## Verify Results

```python
# Check last N items: key, type, title, arXiv ID, PDF count
python3 << 'EOF'
import urllib.request, json

USER_ID = "<zotero-library-id>"
req = urllib.request.Request(
    f"http://localhost:23119/api/users/{USER_ID}/items?limit=20&sort=dateAdded&direction=desc",
    headers={"Zotero-API-Version": "3"}
)
with urllib.request.urlopen(req) as r:
    items = json.load(r)

for i in items:
    d = i["data"]
    if d.get("itemType") in ("preprint", "journalArticle", "conferencePaper"):
        # Count PDF children
        req2 = urllib.request.Request(
            f"http://localhost:23119/api/users/{USER_ID}/items/{i['key']}/children",
            headers={"Zotero-API-Version": "3"}
        )
        with urllib.request.urlopen(req2) as r:
            children = json.load(r)
        pdfs = sum(1 for c in children if c["data"].get("contentType") == "application/pdf")
        print(f"{i['key']} | PDF={pdfs} | {d.get('archiveID',''):20} | {d.get('title','')[:45]}")
EOF
```

## Collection Targeting

Items land in whichever collection is **currently selected in the Zotero UI**.

To target a specific collection programmatically, use `updateSession` after `saveStandaloneAttachment`:

```bash
curl -s -X POST "http://localhost:23119/connector/updateSession" \
  -H "Content-Type: application/json" \
  -d "{\"sessionID\": \"$SESSION\", \"target\": {\"id\": \"C38\", \"filesEditable\": true}}"
```

Get collection IDs from `getSelectedCollection`:
```bash
curl -s -X POST "http://localhost:23119/connector/getSelectedCollection" \
  -H "Content-Type: application/json" -d '{}'
# Returns full collection tree with "id" fields (e.g., "C38" for 表示探索)
```

## API Limitations

| Need | Solution |
|------|----------|
| Add item + PDF | `POST /connector/saveStandaloneAttachment` (binary PDF) |
| Add metadata only | `POST /connector/saveItems` (no PDF attached) |
| Read items/search | `GET /api/users/<ID>/items` (read-only) |
| Delete items | Not supported via API — use Zotero UI |
| Update item fields | Not supported via local API |
| Attach PDF to existing item | Requires Better BibTeX plugin (`/debug-bridge/execute`) |

## Common Issues

**`canRecognize: false`** — PDF downloaded correctly but Zotero can't extract metadata. Usually means the PDF is corrupted or not a proper arXiv paper. Check file size > 50KB.

**Item created but no PDF** — You used `saveItems` instead of `saveStandaloneAttachment`. Delete and re-import with the correct endpoint.

**Item lands in wrong collection** — Check which collection is selected in Zotero UI before running the script, or use `updateSession` to target explicitly.

**arXiv rate limiting (HTTP 429)** — Add `time.sleep(3)` between downloads. Use `--max-time 60` on curl.

**Metadata not recognized after upload** — Zotero needs 10-15 seconds to process. Poll `/items?sort=dateAdded&direction=desc` until the parent preprint item appears.
