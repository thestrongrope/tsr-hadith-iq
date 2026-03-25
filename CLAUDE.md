# tsr-hadith-iq

Research and data model design for Abaqat al-Anwar (عبقات الانوار) — a 23-volume polemical treatise by Mir Hamid Husain responding to Chapter 7 of Tuhfat al-Ithna Ashariyya.

## Key Facts
- Abaqat is NOT a hadith collection — it is a systematic refutation (ردیه)
- Responds to only ONE chapter (باب هفتم في الإمامة) of Tuhfat's 12 chapters
- Two Manaahij: المنهج الأول (Quranic, unpublished) and المنهج الثاني (Hadith, published)
- The user works with a local Abaqat expert scholar — all analysis must be empirically grounded

## Project Structure
- `docs/` — analysis documents, data maps, Gemini outputs, PDFs for scholar review
- `scripts/` — Gemini analysis scripts (use `uv run --with google-genai --with python-dotenv`)
- `reference/` — [gitignored] cloned repos (SS, hadith-hub, hadith-data)
- `sources/abaqat/volumes-djvu/` — [gitignored] all 23 Abaqat volumes as OCR text
- `sources/tuhfat/` — [gitignored] full Tuhfat text
- `.env` — [gitignored] API keys (Gemini, OpenAI, Mistral, Grok)

## Key Documents
- `docs/abaqat-data-model-strategy.md` — THE main document for scholar review
- `docs/tuhfat-chapter7-argument-map.json` — Gemini extraction of Dehlavi's claims
- `docs/abaqat-methodology-analysis.json` — structural patterns of Abaqat
- `docs/abaqat-dossier-patterns.json` — biographical dossier internal structure
- `docs/abaqat-responses/` — per-volume response catalogs (all 23 volumes)

## Tools
- Use `gemini-3.1-pro-preview` for text analysis (1M token context, no chunking needed)
- Use `uv` for Python — never `pip`
- PDFs: use tables, not ASCII art (Arabic breaks in code blocks)
