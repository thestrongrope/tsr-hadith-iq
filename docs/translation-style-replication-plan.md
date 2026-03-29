# Translation Style Replication Pipeline

## Context
The scholar has translated 4 Abaqat volumes (DOCX) and 350 Arabic traditions (HTML/plain text) into English. We want to capture his translation style and replicate it to translate the remaining Abaqat volumes. The approach: extract a style profile, build a RAG retrieval system, fine-tune gpt-4o-mini via OpenAI API, then combine them into a production translator.

## Directory Layout

```
scripts/tsr/                        # All new scripts (10 total)
data/tsr/                           # All generated data (gitignored)
  corpus/                           # Parallel corpus + splits
  style/                            # Style guide (MD + JSON)
  vectorstore/                      # Embeddings (numpy) + metadata
  finetune/                         # OpenAI fine-tune JSONL + job log
  translations/volNN/               # Per-volume output with chunk caching
```

## Phase 0: Data Preparation

### `scripts/tsr/01_parse_docx.py`
- Parse 4 DOCX volumes using `python-docx`
- Detect source vs. English via Unicode Arabic block analysis (no LLM needed)
- Group consecutive same-language paragraphs, pair adjacent source/english blocks
- Output: per-volume JSON in `data/tsr/corpus/docx-raw/`

### `scripts/tsr/02_parse_traditions.py`
- Parse 350 traditions from HTML/plain text using `beautifulsoup4`
- Same Unicode-based language detection
- Flexible `--format` flag (html/text/auto) since exact format TBD
- Output: `data/tsr/corpus/traditions-raw/traditions.json`

### `scripts/tsr/03_build_corpus.py`
- Merge all raw extractions, normalize Arabic diacritics (NFC), deduplicate
- Filter pairs too short (<20 chars) or too long (>4000 chars)
- Split 90/10 train/eval, stratified by source type
- Output: `parallel-pairs.jsonl`, `train.jsonl`, `eval.jsonl`

## Phase 1: Style Extraction

### `scripts/tsr/04_extract_style.py`
- Sample ~200 diverse parallel pairs from corpus
- Send to Gemini (1M context) with detailed extraction prompt
- Analyze: vocabulary choices, honorific patterns, sentence structure, transliteration conventions, quotation handling, terminology glossary, tone/register
- Output: `data/tsr/style/style-guide.md` (for scholar review) + `style-guide.json` (machine-readable)

## Phase 2: RAG System

### `scripts/tsr/05_build_vectorstore.py`
- Embed source texts using OpenAI `text-embedding-3-large` (1024 dims)
- Store as numpy `.npz` + parallel `metadata.jsonl`
- Brute-force cosine similarity (corpus is ~2000 pairs, no FAISS needed)

### `scripts/tsr/06_rag_translate.py`
- Standalone RAG translator (usable before fine-tuning exists)
- Embed input passage, retrieve top-K similar pairs
- Prompt: system (style guide) + user (retrieved examples + source text)
- Configurable model (default gpt-4o, also supports Gemini)

## Phase 3: OpenAI Fine-Tuning

### `scripts/tsr/07_prepare_finetune.py`
- Convert corpus to OpenAI chat format JSONL
- Condensed style guide (~500 tokens) as system message in every example
- Token counting via `tiktoken` — warn/split examples exceeding 16K tokens
- Output: `train-openai.jsonl`, `eval-openai.jsonl`

### `scripts/tsr/08_run_finetune.py`
- Upload files, create fine-tuning job (`gpt-4o-mini`, suffix `abaqat-translator`)
- Poll status, log events to `job-log.json`
- `--resume` flag to check existing job status
- Estimated cost: ~$8 for 1800 examples x 3 epochs

### `scripts/tsr/09_eval_finetune.py`
- Compare 3 methods on eval set: base gpt-4o-mini, RAG approach, fine-tuned model
- Metrics: BLEU score, terminology adherence, length ratio
- Optional: Gemini-as-judge for style similarity rating (1-5)
- Output: `eval-results.json` + printed comparison table

## Phase 4: Production Translator

### `scripts/tsr/10_translate_volume.py`
- Translates full Abaqat volumes using hybrid: RAG + fine-tuned model
- Chunks volumes by structural sections (reuse `detect_sections()` pattern from `parse_volume_full.py`), further split at paragraph boundaries if >2000 chars
- Per-chunk: embed → retrieve 3 examples → prompt fine-tuned model → cache result
- Fallback chain: fine-tuned model → base gpt-4o → Gemini Flash
- Caching per chunk (`chunk-NNN.json`) for resumability
- Assembly into interlaced markdown (source block + translation block)

## Execution Order

```
Phase 0:  01 + 02 (parallel) → 03
Phase 1:  04 (depends on 03)
Phase 2:  05 (depends on 03) → 06
Phase 3:  07 (depends on 03 + 04) → 08 → 09
Phase 4:  10 (depends on 05 + 08)
```

Phases 2 and 3 can run in parallel once Phases 0-1 are done. RAG translator (06) is usable immediately for testing before fine-tuning completes.

## Conventions
- All scripts: `uv run --with <deps>` pattern, `python-dotenv`, argparse CLI
- Follow patterns from `translate_pdf_batched.py` (caching, fallbacks, progress)
- `data/tsr/` added to `.gitignore`

## Verification
1. After Phase 0: check corpus stats — expect 1500-2000 parallel pairs, review alignment quality
2. After Phase 1: scholar reviews `style-guide.md` for accuracy
3. After Phase 2: translate 5 held-out passages, compare with scholar's reference
4. After Phase 3: eval script compares all 3 methods quantitatively
5. After Phase 4: scholar reviews a sample chapter from a new volume
