# Roadmap

## Vision

Build a complete digital index of Abaqat al-Anwar — every page structured, every citation verified, every narrator cross-referenced — making the largest work in Sunni-Shia hadith scholarship fully queryable.

## Where We Are

### Done

- **Data models finalized** — 5 schemas for source books (A-E) + Abaqat internal model (v3, 15 entities)
- **JarhGrade system** — standard 6+6 from al-Suyuti, verified against classical sources, mapped to Ibn Hajar's 12-grade
- **Scholar ID strategy** — Tahdhib entry numbers as primary key, hawramani.com cross-reference (100K narrators cached locally)
- **13 books downloaded** — PDFs organized in `data/books/`, 1.9 GB total
- **OCR pipeline** — Gemini Flash Lite, ~5s/page, JSONL output, resumable
- **Vol 23 deep analysis** — 340 pages OCR'd, 518 citations extracted, 28 Dehlavi claims mapped, 3-layer argument structure documented
- **Tuhfat Ch 7 analyzed** — 125 pages OCR'd, 26 Shia proofs identified (8 Quranic + 12 Hadith + 6 Rational), 3 rebuttal methods documented
- **7 citations verified** verbatim against source PDFs — 0 discrepancies

### In Progress

- Clean OCR exists for Vol 23 and Tuhfat Ch 7 only — 22 volumes remaining
- Book classification done for Vol 23 (389 books) — other volumes not yet
- No structured JSON produced from any rijal book yet

## Next Steps

### Phase 1: Complete OCR (all 23 volumes)

OCR all Abaqat volumes with Gemini Flash Lite. ~340 pages/vol × 23 vols = ~7,800 pages.
Estimated: ~13 hours of API time, ~$5-6 total.

Output: `data/books/abaqat/ocr/vol{NN}-gemini-pages.jsonl` for each volume.

### Phase 2: Index Abaqat Vol 23 (pilot)

Full page-by-page extraction of Vol 23 into data model v3 entities using Grok on saved OCR text.
Every page → structured JSON. Nothing left out.

Output: `data/books/abaqat/structured/vol23.json`

Entities to extract per page:
- Narrator Citations (book, author, isnad, hadith text variant, companion)
- Rijal Evaluations (evaluator, term, grade, source)
- Author Commentary (Farsi)
- Poetry Evidence
- Rebuttals
- Dalalah Proofs
- Tanbihat

### Phase 3: Index source books (Tahdhib first)

OCR Tahdhib al-Tahdhib (13 vols, 5,764 pages) → extract every entry into ScholarEntry JSON.
~8,000 narrator entries with teachers, students, evaluations.

Then: Mizan al-I'tidal, Wafayat al-A'yan, remaining T1 books.

### Phase 4: Cross-reference

Link Abaqat citations to indexed source book entries via scholar_id.
Query: "Show me every narrator Dehlavi attacks and what every rijal book says about them."

### Phase 5: All 23 volumes

Extend Phase 2 to all volumes. Map every Dehlavi claim to every Abaqat response across the full work.

### Phase 6: Verification

Verify every Abaqat citation against the indexed source books. Flag any discrepancy for scholar review.

## Principles

1. **Extract once, analyze many times** — OCR with Gemini (expensive), analyze with Grok (cheap)
2. **JSONL for streaming** — append-only, resumable, crash-safe
3. **Nothing uncategorized** — every page fits the model, or the model expands
4. **Scholar review** — all outputs designed for expert validation
5. **Empirically grounded** — models validated against real data before scaling
