# Contributing to tsr-hadith-iq

This guide helps new contributors get set up and start indexing Abaqat al-Anwar volumes and Tuhfat Chapter 7 sections.

## What This Project Is

**Abaqat al-Anwar** (عبقات الانوار) is a 23-volume polemical treatise by Mir Hamid Husain (d. 1306 AH). It responds to **Chapter 7** (باب هفتم في الإمامة — on the Imamate) of *Tuhfat al-Ithna Ashariyya* by Shah Abd al-Aziz al-Dehlavi.

Abaqat is **not** a hadith collection. It is a systematic refutation (ردیه) structured in three layers:

| Layer | Arabic | Purpose | Vol 23 Stats |
|-------|--------|---------|-------------|
| **Evidence** | إثبات | "This hadith exists in YOUR books" | 169 books, 225 citations |
| **Authentication** | توثيق | "The narrators are reliable per YOUR scholars" | 81 books, 109 citations |
| **Rebuttal** | ردّ | "Your counter-arguments fail" | 119 books, 169 citations |

Each volume defends one or more hadiths (Ghadir, Manzila, Thaqalayn, Safinah, etc.) using this structure, citing hundreds of Sunni source books against Dehlavi's claims.

**The goal:** make every page of Abaqat queryable — every citation verified, every narrator cross-referenced against rijal source books.

## What's Already Done

- **Vol 23 (Hadith al-Safinah)** — fully OCR'd (340 pages), structured into 76 sections, 348 unique books extracted, 3-layer argument model complete
- **Tuhfat Chapter 7** — fully OCR'd (125 pages), 1,272 content units extracted via dual-model (GPT 4.1 + Gemini 3 Flash)
- **13 source books downloaded** — Abaqat (23 vols), Tuhfat, + 11 rijal books (1.8 GB total PDFs)
- **Hawramani narrator index** — 100K+ entries cached locally as parquet (5.8 MB)
- **Data model v3** — finalized with 15 entity types, empirically tested against real OCR data

**22 Abaqat volumes still need OCR and structuring.** That's where you come in.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_ORG/tsr-hadith-iq.git
cd tsr-hadith-iq
```

### 2. Install uv (Python package runner)

We use `uv` exclusively — never `pip` or bare `python`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See [uv docs](https://docs.astral.sh/uv/) for details.

### 3. Set up API keys

Create a `.env` file at the repo root (it's git-ignored):

```bash
GEMINI_API_KEY=your_google_ai_key_here
OPENAI_API_KEY=your_openai_key_here     # Also used for Grok via XAI endpoint
XAI_API_KEY=your_xai_grok_key_here
MISTRAL_API_KEY=your_mistral_key_here    # Optional
```

You need at minimum **Gemini** (for OCR) and **Grok/OpenAI** (for analysis).

### 4. Download the PDF corpus

The source PDFs (1.8 GB) are shared via OneDrive since they're too large for git.

**Download link:** [OneDrive — tsr-hadith-iq-pdfs.tar.gz](https://imantix-my.sharepoint.com/:u:/g/personal/asif_imantix_ai/IQCfvMZoAORhRrv6j8VK5z-EAbrU_czsbfIBF6CNH_vLNHM?e=3BgQoL)

```bash
# Extract to data/pdfs/
tar -xzf tsr-hadith-iq-pdfs.tar.gz -C data/

# Restore PDFs to the expected project structure
./scripts/restore-pdfs.sh
```

This places PDFs into `data/books/{book-name}/pdf/` for each of the 13 books:

| Book | Size | Volumes | Description |
|------|------|---------|-------------|
| abaqat | 608 MB | 23 | The main work (Mir Hamid Husain) |
| tuhfat | 54 MB | 1 | The counter-text (Dehlavi) |
| tahdhib-al-kamal | 288 MB | 35 | Al-Mizzi — master narrator compendium |
| siyar-alam-al-nubala | 260 MB | 25 | Al-Dhahabi — lives of eminent scholars |
| tarikh-baghdad | 148 MB | 14 | Al-Khatib — history of Baghdad scholars |
| tahdhib-al-tahdhib-hindi | 138 MB | 12 | Ibn Hajar — narrator evaluations |
| tabaqat-al-shafiyya-kubra | 89 MB | 6 | Al-Subki — Shafi'i jurist biographies |
| wafayat-al-ayan | 73 MB | 6 | Ibn Khallikan — deaths of notable men |
| mizan-al-itidal | 49 MB | 4 | Al-Dhahabi — weak narrators |
| al-ibar | 31 MB | 3 | Al-Dhahabi — universal history |
| mirat-al-janan | 27 MB | 2 | Al-Yafi'i — chronicle |
| tadhkirat-al-huffaz | 27 MB | 1 | Al-Dhahabi — memorizers of hadith |
| tabaqat-al-huffaz | 13 MB | 1 | Al-Suyuti — generations of memorizers |

### 5. Verify setup

```bash
# Check OCR data exists
ls data/books/abaqat/ocr/vol23-gemini-full.txt

# Check structured data
ls data/books/abaqat/structured/vol23/parsed.json

# Check indexes
ls data/indexes/hawramani-index.parquet

# Check PDFs restored
ls data/books/abaqat/pdf/
```

## Key Files to Read First

| File | What It Tells You |
|------|-------------------|
| `CLAUDE.md` | Project conventions — tools, formats, rules |
| `ROADMAP.md` | Where the project is and what's next |
| `docs/abaqat-data-model-v3.md` | **THE schema** — 3-layer structure, 15 entity types |
| `docs/tuhfat-ch7-complete-structure.md` | Dehlavi's 4 sections, 7 rebuttal methods |
| `data/books/abaqat/structured/vol23/parsed.json` | Reference implementation — what a fully-indexed volume looks like |

## The Data Pipeline

Every volume goes through 4 phases:

### Phase 1: PDF to OCR text

```bash
uv run --with google-genai --with pymupdf --with python-dotenv \
  python scripts/ocr_volume_gemini.py --volume 5
```

- Renders each PDF page at 200 DPI, sends to Gemini Flash Lite
- Outputs per-page JSON + concatenated full text
- **Resumable** — if interrupted, re-run with `--start-page N`
- Cost: ~$0.20-0.30 per volume (~340 pages)
- Time: ~28 min per volume (5s/page)

Output:
- `data/books/abaqat/ocr/vol05-gemini-pages.jsonl`
- `data/books/abaqat/ocr/vol05-gemini-full.txt`

### Phase 2: Detect sections (regex, no LLM)

```bash
uv run --with openai --with python-dotenv \
  python scripts/parse_volume_structure.py --volume 5
```

- Detects section types: table of contents, narrator citations, biographical dossiers, rebuttals, dalalah proofs, etc.
- Pure regex — deterministic, no API cost

Output: `data/books/abaqat/structured/vol05/structure.json`

### Phase 3: Extract structured data (Grok)

```bash
uv run --with openai --with python-dotenv \
  python scripts/parse_volume_full.py --volume 5
```

- Sends each section to Grok with type-specific prompts
- Extracts entities per the v3 data model: citations, isnad chains, rijal evaluations, rebuttals
- **Section-level caching** — re-runs skip completed sections
- Cost: ~$3-5 per volume

Output: `data/books/abaqat/structured/vol05/parsed.json`

### Phase 4: Quality check (optional)

```bash
uv run --with openai --with google-genai --with python-dotenv \
  python scripts/compare_models_citations.py --models grok,flash-lite --volume 5
```

- Compares extraction results across multiple LLMs
- Identifies missed citations and discrepancies

## Adding New Books

### Downloading from archive.org

Most rijal books are available on archive.org. Use the download script:

```bash
# Preview what would be downloaded (dry run)
uv run python scripts/download_rijal_books.py --tier 1 --dry-run

# Download a specific book
uv run python scripts/download_rijal_books.py --book "Tahdhib al-Tahdhib"
```

The book catalog is in `docs/source-books-archive-org.json` — it lists archive.org URLs, volume counts, and page counts for all 13 books.

### OCR for non-Abaqat books

The OCR script currently targets Abaqat volumes. For rijal books, you'll need to adapt the PDF path handling, but the Gemini OCR pipeline is the same. The key pattern:

1. Render PDF page as image
2. Send to `gemini-3.1-flash-lite-preview` with the OCR prompt
3. Save per-page JSONL + concatenated text
4. **Never re-read a PDF once OCR'd** — all analysis runs on saved text

## Working with Parquet

We use **Apache Parquet** for large index/lookup data. It's a compressed columnar format that shrinks JSON dramatically:

| Dataset | JSON Size | Parquet Size | Reduction |
|---------|-----------|-------------|-----------|
| Hawramani narrator index | 25 MB | 5.8 MB | 77% |
| Hawramani categories | 200 KB | 12 KB | 94% |

### When to use Parquet

Convert to parquet when:
- The data is **tabular** (rows of similar records)
- Size exceeds **5 MB** as JSON
- The data is **read-mostly** (lookup/query, not append)

Keep JSONL when:
- You're **streaming/appending** (OCR output, extraction results)
- The data has **nested/variable structure** per record
- You need human-readable output

### Reading and writing Parquet

```python
import pandas as pd

# Read
df = pd.read_parquet('data/indexes/hawramani-index.parquet')
print(df.columns)  # id, name, slug, categories, ...
print(len(df))     # 100K+ rows

# Query
matches = df[df['name'].str.contains('جعفر', na=False)]

# Write (when creating new indexes)
df.to_parquet('data/indexes/my-new-index.parquet', index=False)
```

Dependencies: `uv run --with pandas --with pyarrow python your_script.py`

## What Needs Doing

Priority order:

### 1. OCR remaining Abaqat volumes (22 volumes)

The biggest task. Run `ocr_volume_gemini.py` for volumes 1-22 (vol 23 is done). Each volume takes ~28 min and costs ~$0.25. Total: ~$5-6 for all 22.

### 2. Structure each OCR'd volume

Run `parse_volume_structure.py` then `parse_volume_full.py`. Use vol 23 as your reference — the output should look like `data/books/abaqat/structured/vol23/parsed.json`.

### 3. OCR and index rijal books

Starting with **Tahdhib al-Tahdhib** (the most-cited rijal source). Extract each narrator entry into structured JSON matching the `ScholarEntry` schema in `docs/book-schemas.md`.

### 4. Cross-reference citations

Once both Abaqat and rijal books are indexed: link every Abaqat citation to the corresponding source book entry via scholar ID. The query we're building toward: "Show me every narrator Dehlavi attacks and what every rijal book says about them."

## Conventions

- **Python:** Always `uv run --with [deps]` — never `pip install`
- **Output format:** JSONL for streaming/append operations, JSON for final structured output
- **OCR:** Extract once with Gemini, analyze many times with Grok (cheaper)
- **Caching:** Cache intermediate results at section level — makes re-runs instant
- **API cost awareness:**
  - Gemini Flash Lite (OCR): ~$0.075/1M input tokens
  - Grok (analysis): ~$0.60/1M input tokens
  - Gemini Pro (complex analysis): ~$1.50/1M input tokens — use sparingly
- **Git:** Commit OCR text and structured JSON. Never commit PDFs or `.env`
- **Parquet:** Use for any index/lookup data over 5 MB
- **Scholar review:** All outputs are designed for expert validation — don't assume extraction is correct without verification

## Project Structure Quick Reference

```
tsr-hadith-iq/
├── CLAUDE.md                          # Project conventions
├── ROADMAP.md                         # Phased plan
├── CONTRIBUTING.md                    # This file
├── data/
│   ├── books/
│   │   ├── abaqat/
│   │   │   ├── ocr/                   # Gemini OCR output (vol23 done)
│   │   │   └── structured/            # Parsed data models
│   │   │       ├── all-volumes.json   # 23-volume summary
│   │   │       ├── responses/         # Per-volume summaries
│   │   │       └── vol23/             # Deep analysis (reference impl)
│   │   ├── tuhfat/
│   │   │   ├── ocr/                   # Ch7 OCR'd
│   │   │   └── structured/            # 1,272 content units
│   │   └── [11 rijal books]/          # Awaiting OCR
│   ├── indexes/
│   │   ├── hawramani-index.parquet    # 100K narrators
│   │   └── hawramani-categories.parquet
│   └── pdfs/                          # [gitignored] from OneDrive
├── docs/
│   ├── abaqat-data-model-v3.md        # THE schema
│   ├── book-schemas.md                # Source book JSON schemas
│   ├── tuhfat-ch7-complete-structure.md
│   └── source-books-archive-org.json  # Archive.org catalog
└── scripts/
    ├── ocr_volume_gemini.py           # PDF → text (Gemini)
    ├── parse_volume_structure.py      # text → sections (regex)
    ├── parse_volume_full.py           # sections → data model (Grok)
    ├── compare_models_citations.py    # quality check
    ├── download_rijal_books.py        # archive.org → PDFs
    ├── fetch_hawramani_index.py       # hawramani.com → parquet
    ├── restore-pdfs.sh               # OneDrive → data/books/*/pdf/
    ├── translate_pdf_batched.py       # PDF → English (Gemini)
    └── translate_markdown.py          # Markdown → English
```
