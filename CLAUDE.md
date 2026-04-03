# tsr-hadith-iq

Research and data model design for Abaqat al-Anwar (عبقات الانوار) — a 23-volume polemical treatise by Mir Hamid Husain responding to Chapter 7 of Tuhfat al-Ithna Ashariyya.

## Getting Started
- New contributors: read `CONTRIBUTING.md` for setup, pipeline walkthrough, and what needs doing

## Key Facts
- Abaqat is NOT a hadith collection — it is a systematic refutation (ردیه)
- Responds to only ONE chapter (باب هفتم في الإمامة) of Tuhfat's 12 chapters
- Two Manaahij: المنهج الأول (Quranic, unpublished) and المنهج الثاني (Hadith, published)
- The user works with a local Abaqat expert scholar — all analysis must be empirically grounded

## Project Structure
- `docs/` — analysis documents, data models, structured outputs, reports
- `scripts/` — reusable Python scripts (use `uv run --with google-genai --with python-dotenv`)
- `data/` — [gitignored] project data:
  - `books/{book-name}/pdf/` — source PDFs
  - `books/{book-name}/ocr/` — OCR extracted text (Gemini/DJVU)
  - 13 books: abaqat (23 vols), tuhfat, + 11 rijal books (~1.9 GB total)
  - `indexes/` — hawramani narrator index (100K entries)
- `reference/` — [gitignored] external repos (SS, hadith-hub, hadith-data) + one-time scripts
- `.env` — [gitignored] API keys (Gemini, OpenAI, Mistral, Grok)

## Key Documents
- `docs/abaqat-data-model-v3.md` — THE data model schema (3-layer argument structure, 15 entity types)
- `docs/tuhfat-ch7-complete-structure.md` — Dehlavi's Chapter 7 arguments mapped
- `docs/book-schemas.md` — JSON schemas for all source book types
- `docs/source-books-archive-org.json` — catalog of 13 books with archive.org URLs
- `data/books/abaqat/structured/responses/` — per-volume response catalogs (all 23 volumes)
- `data/books/abaqat/structured/vol23/` — reference implementation (fully indexed volume)

## Tools
- Use `gemini-3.1-flash-lite-preview` for OCR (fastest, cheapest, good Arabic quality)
- Use `gemini-3.1-pro-preview` for complex analysis (1M token context)
- Use Grok for analysis on already-extracted text (cheaper than Gemini)
- Never re-read PDFs — extract once with Gemini, save, analyze saved text
- Use JSONL for streaming output (not monolithic JSON)
- Use `uv` for Python — never `pip`
- PDFs: use tables, not ASCII art (Arabic breaks in code blocks)
