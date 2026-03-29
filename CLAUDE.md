# tsr-hadith-iq

Research and data model design for Abaqat al-Anwar (عبقات الانوار) — a 23-volume polemical treatise by Mir Hamid Husain responding to Chapter 7 of Tuhfat al-Ithna Ashariyya.

## Key Facts
- Abaqat is NOT a hadith collection — it is a systematic refutation (ردیه)
- Responds to only ONE chapter (باب هفتم في الإمامة) of Tuhfat's 12 chapters
- Two Manaahij: المنهج الأول (Quranic, unpublished) and المنهج الثاني (Hadith, published)
- The user works with a local Abaqat expert scholar — all analysis must be empirically grounded

## Project Structure
- `docs/` — analysis documents, data models, structured outputs, reports
- `scripts/` — reusable Python scripts (use `uv run --with google-genai --with python-dotenv`)
- `reference/` — [gitignored] all large/binary data:
  - `books/abaqat/pdf/` — 23 Abaqat volume PDFs (608 MB)
  - `books/abaqat/ocr/` — OCR text (DJVU legacy + Gemini clean)
  - `books/tuhfat/pdf/` — Tuhfat PDF (54 MB)
  - `books/tuhfat/ocr/` — Clean Gemini OCR of Chapter 7
  - `books/rijal/` — 11 rijal books as PDFs (1.16 GB)
  - `indexes/` — hawramani narrator index (100K entries)
  - `scripts/` — one-time/exploratory scripts
  - `SS/`, `hadith-hub/`, `hadith-data/` — cloned external repos
- `.env` — [gitignored] API keys (Gemini, OpenAI, Mistral, Grok)

## Key Documents
- `docs/abaqat-data-model-strategy.md` — THE main document for scholar review
- `docs/tuhfat-chapter7-argument-map.json` — Gemini extraction of Dehlavi's claims
- `docs/abaqat-methodology-analysis.json` — structural patterns of Abaqat
- `docs/abaqat-dossier-patterns.json` — biographical dossier internal structure
- `docs/abaqat-responses/` — per-volume response catalogs (all 23 volumes)

## Tools
- Use `gemini-3.1-flash-lite-preview` for OCR (fastest, cheapest, good Arabic quality)
- Use `gemini-3.1-pro-preview` for complex analysis (1M token context)
- Use Grok for analysis on already-extracted text (cheaper than Gemini)
- Never re-read PDFs — extract once with Gemini, save, analyze saved text
- Use JSONL for streaming output (not monolithic JSON)
- Use `uv` for Python — never `pip`
- PDFs: use tables, not ASCII art (Arabic breaks in code blocks)
