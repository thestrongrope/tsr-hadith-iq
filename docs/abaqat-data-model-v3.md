# Abaqat al-Anwar — Data Model v3

## What Changed from v2

v2 was built from structural analysis (section types, entity definitions). v3 is informed by **empirical testing against real OCR data** — 10 pages of clean Gemini OCR from Vol 23 processed by Grok, measuring what the model captures (95%) and what it misses (5%).

Key changes:

1. **Three-Layer Argument Structure** — formalized as the top-level organizing principle, replacing the flat section type list
2. **Narrator Citation expanded** — now captures hadith text variants, multiple companions per citation, nested book references, and structured isnad chains with scholar_id links
3. **Poetry Evidence** — new entity for scholarly verse used as proof (e.g., al-Shafi'i's poetry about Ahl al-Bayt as Noah's ark)
4. **Scholar Registry** — master list extracted from the narrator enumeration (pages 5-9), providing death dates that individual citations don't repeat
5. **Book title normalization** — same book appears under 3+ variant titles; the registry maps variants to a canonical title
6. **Hadith text collation** — tracking different wordings of the same hadith across sources

---

## 1. Top-Level: Three-Layer Argument

Every sanad-focused volume follows this structure:

```
Volume N (Hadith X)
│
├── LAYER 1: EVIDENCE (إثبات)
│   "This hadith exists in YOUR books"
│   ├── Scholar Registry (master narrator list with death dates)
│   ├── Narrator Citation × 40 (اما شافعى...)
│   │   ├── Book Citation(s) per narrator
│   │   │   ├── Isnad chain (if given)
│   │   │   ├── Hadith text variant
│   │   │   └── Companion source
│   │   └── Author's Farsi commentary
│   └── Poetry Evidence (scholarly verses as proof)
│
├── LAYER 2: AUTHENTICATION (توثيق)
│   "The narrators are reliable per YOUR scholars"
│   ├── Biographical Dossier × N (ترجمه)
│   │   └── Rijal Evaluation × N (jarh/ta'dil)
│   └── Author's Farsi commentary
│
├── LAYER 3: REBUTTAL (ردّ)
│   "Your counter-arguments fail"
│   ├── Opponent's Claim (Ibn Taymiyyah / Dehlavi)
│   ├── Author's Response (اقول)
│   ├── Dalalah Proof × N (وجوه دلالت)
│   ├── Tanbih × N (authorial notices)
│   └── Argument/Rebuttal Lineage
│
└── APPENDIX (فهارس)
```

**Vol 23 numbers:**
- Layer 1: 169 books, 225 citations, 40 narrator citations
- Layer 2: 81 books, 109 citations
- Layer 3: 119 books, 169 citations

---

## 2. Entity Types (v3)

### 2.0 Volume

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| volume_number | int | | 23 |
| hadith_defended | ref → DefendedHadith | | Hadith al-Safinah |
| pattern | enum | SANAD_FIRST, RESPONSE_FIRST, HYBRID | SANAD_FIRST |
| total_pages | int | PDF page count | 340 |
| ocr_source | string | Path to clean OCR text | sources/abaqat/volumes-gemini/vol23-full.txt |
| layers | object | Layer 1/2/3 page ranges | {evidence: [5,200], auth: [200,250], rebuttal: [250,320]} |

### 2.1 Defended Hadith (حدیث مدافع‌عنه)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| name_arabic | string | Standard name | حديث السفينة |
| name_english | string | | Hadith al-Safinah |
| canonical_text | string | Most common Arabic wording | مَثَلُ أَهْلِ بَيْتِي كَمَثَلِ سَفِينَةِ نُوحٍ مَنْ رَكِبَهَا نَجَا وَمَنْ تَخَلَّفَ عَنْهَا هَلَكَ |
| text_variants | array | All distinct wordings found across sources (see 2.5) | 7+ variants in Vol 23 |
| volumes | array[int] | Which volumes defend this hadith | [23] |
| topic_tag | string | From book-schemas.md topic_tags | safinah |
| companions | array[string] | All sahaba through whom it's narrated | [Abu Dharr, Ibn Abbas, Ibn al-Zubayr, Abu Sa'id al-Khudri] |

### 2.2 Scholar Registry (فهرست علماء)

**NEW in v3.** The master list of scholars Mir Hamid Husain enumerates at the start of each volume (pages 5-9 in Vol 23). This is the authority for death dates and full names — individual citations reference this registry.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| scholar_id | string | Stable identifier | tahdhib-2-156 or 204-al-shafii |
| name_arabic | string | Full name as given in registry | إدريس القافعي صاحب المذهب المعروف |
| name_english | string | | Imam al-Shafi'i |
| death_ah | int | | 204 |
| position_in_list | int | Order in Mir Hamid Husain's enumeration | 1 |
| school | string | Madhab | Shafi'i |
| key_book | string | Primary book cited | his own Musnad |
| still_alive_note | string | For contemporaries: "كان حياً إلى سنة..." | null |

**Vol 23 evidence:** ~70 scholars listed on pages 5-9, from al-Shafi'i (d. 204) to contemporaries (alive in 1280s AH).

### 2.3 Narrator Citation (اما... — إخراج / رواية)

**Expanded from v2.** Now a container holding one or more Book Citations, with structured data from empirical extraction.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| opening_formula | string | Always starts with "اما" | اما شافعى |
| narrator_scholar | ref → Scholar | Who narrated | al-Shafi'i |
| position_in_tawatur | int | Order in the stacking sequence | 1 of 40 |
| book_citations | array[BookCitation] | One or more books this narrator's version appears in | see 2.4 |
| author_commentary | string | Mir Hamid Husain's Farsi commentary | ونيز شافعى تنها بروايت كردن... |
| page_start | int | | 7 |
| page_end | int | | 9 |

### 2.4 Book Citation (استناد به كتاب)

**NEW in v3.** Replaces the flat Citation entity from v2. Each Book Citation is one specific reference to a book, with optional isnad and hadith text.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| book_arabic | string | Title as it appears in text | فرائد السمطين |
| book_canonical | string | Normalized standard title | فرائد السمطين في فضائل المرتضى والبتول والسبطين |
| book_english | string | | Fara'id al-Samtayn |
| author_arabic | string | | صدر الدين الحموي |
| author_id | ref → Scholar | | 741-al-hamawi |
| layer | enum | EVIDENCE, AUTHENTICATION, REBUTTAL | EVIDENCE |
| citation_context | enum | HADITH_SOURCE, TAWATUR_PROOF, AUTHOR_TAWTHIQ, AUTHOR_TAJRIH, PRIMARY_REBUTTAL, REBUTTAL_LINEAGE, ARGUMENT_LINEAGE, LINGUISTIC, etc. | HADITH_SOURCE |
| isnad | Isnad or null | Transmission chain if given | see 2.6 |
| hadith_text_variant | ref → TextVariant or null | Specific wording in this source | see 2.5 |
| companion | string or null | Sahabi the chain goes through | أبو ذر الغفاري |
| nested_in | ref → BookCitation or null | When cited through another book | e.g., "al-Hakim from al-Tabari's Tafsir" |
| vol_page | string or null | Volume/page reference if given | ج٣ ص٥١٧ |
| edition | object or null | Edition info from footnotes | see book-schemas.md |
| page_in_abaqat | int | PDF page where this citation appears | 15 |
| verbatim_arabic | string | Exact text as it appears in Abaqat | |

### 2.5 Hadith Text Variant (نص الحديث)

**NEW in v3.** Tracks different wordings of the same hadith across sources. Critical for textual criticism — some variants say "هلك" (perished), others say "غرق" (drowned), others say "زُخَّ به في النار" (thrown into the fire).

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| variant_id | string | | safinah-v1 |
| arabic_text | string | Exact wording | مثل أهلبيتي فيكم كمثل سفينة نوح من ركبها نجا ومن تخلف عنها هلك |
| key_differences | string | What's different from canonical | "هلك" instead of "غرق" |
| sources | array[ref → BookCitation] | Which books use this wording | |
| companion | string | Which sahabi's narration produces this wording | أبو ذر |

**Vol 23 variants observed:**
1. `من ركبها نجا ومن تخلف عنها هلك` — standard (via Abu Dharr)
2. `من ركبها نجا ومن تخلف عنها غرق` — "drowned" variant (via Ibn Abbas)
3. `من تخلّف عنها زُخَّ به في النار` — "thrown in fire" variant (via Ibn Mundhir)
4. `ألا إن مثل أهلبيتي فيكم مثل سفينة نوح في قومه` — "among his people" addition
5. `مثل أهلبيتي مثل سفينة نوح` — shortened form
6. `من ركبها نجى ومن تركها غرق` — "تركها" instead of "تخلف عنها"
7. `فيكم كسفينة نوح من ركب فيها نجا ومن تخلف عنها غرق` — "فيها" addition

### 2.6 Isnad (سلسلة السند)

**NEW in v3.** Structured chain representation replacing the flat string in v2.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| full_chain_arabic | string | Complete chain as written | الحسين بن منصور عن عبدالله بن عبدالقدوس عن الأعمش عن أبي اسحق عن حنش بن المعتمر |
| chain_links | array[ChainLink] | Parsed individual links | see below |
| chain_type | enum | FULL, PARTIAL, REFERENCE_ONLY | FULL |
| companion | ref → Scholar | Terminal sahabi | Abu Dharr |

**ChainLink:**

| Field | Type | Description |
|-------|------|-------------|
| name_arabic | string | حنش بن المعتمر |
| scholar_id | ref → Scholar or null | Links to ScholarEntry for cross-referencing |
| role | string | حدثنا / عن / أنبأنا / أخبرنا / سمعت |
| position | int | Position in chain (1 = closest to compiler) |

### 2.7 Poetry Evidence (شعر استدلالى)

**NEW in v3.** Scholarly verses used as proof. Found on ~5% of pages — not noise, but evidence. Al-Shafi'i's famous poem about Ahl al-Bayt being like Noah's ark is one of the most cited proofs.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| poet | ref → Scholar | Who composed the verse | al-Shafi'i |
| arabic_text | string | Full verse text | ركبت على اسم الله في سفن النجا / وهم أهل بيت المصطفى خاتم الرسل |
| source_book | string | Where the poem is quoted from | ذخيرة المآل |
| evidential_value | string | What it proves | Al-Shafi'i equates Ahl al-Bayt with Noah's ark — a founder of Sunni fiqh endorsing the hadith's meaning |
| page_in_abaqat | int | | 8 |

### 2.8 Opponent's Claim (نقل كلام الخصم)

*Unchanged from v2.* See v2 section 2.2.

### 2.9 Author's Response (جواب / اقول)

*Unchanged from v2.* See v2 section 2.4.

### 2.10 Dalalah Proof (وجه دلالت)

*Unchanged from v2.* See v2 section 2.5.

### 2.11 Biographical Dossier (ترجمه)

*Expanded.* Now links to the JarhGrade system from book-schemas.md.

| Field | Type | Description |
|-------|------|-------------|
| heading | string | « ترجمة [Scholar] از [Rijal Book] » |
| subject_scholar | ref → Scholar | Who is being evaluated |
| dossier_type | enum | FULL_BIOGRAPHICAL, BRIEF_EVALUATION, COMPARATIVE, POLEMICAL |
| argumentative_purpose | string | Why the author evaluates this scholar here |
| evaluations | array[RijalEvaluation] | See 2.12 |
| source_citations | array[BookCitation] | Books quoted in this dossier |

### 2.12 Rijal Evaluation (جرح / تعدیل)

*Expanded.* Now uses the 6+6 JarhGrade system and includes domain qualifier.

| Field | Type | Description |
|-------|------|-------------|
| evaluator | ref → Scholar | Who made the judgment |
| term_arabic | string | The exact rijal term used |
| grade | string | From 6+6 system: tadil_1...tadil_6, jarh_1...jarh_6, majhul_hal, majhul_ayn |
| domain | string or null | Domain-limited evaluation (e.g., "أمور الإسلام فقط") |
| verbatim_arabic | string | Exact quote |
| source_book | ref → BookCitation | Which rijal book this comes from |
| nested_source | string or null | If quoted through an intermediary |

### 2.13 Tanbih (تنبيه وايقاظ)

*Unchanged from v2.* See v2 section 2.8.

### 2.14 Argument Lineage (سلسلة الاستدلال)

*Unchanged from v2.*

### 2.15 Rebuttal Lineage (سلسلة الجواب)

*Unchanged from v2.*

---

## 3. Book Title Registry

**NEW in v3.** The same book appears under multiple variant titles in Abaqat's OCR text. This registry maps variants to a canonical form.

| Variant in text | Canonical title | Book ID |
|----------------|-----------------|---------|
| معجم صغیر | المعجم الصغير | mujam-saghir-tabarani |
| معجم الصغير | المعجم الصغير | mujam-saghir-tabarani |
| المعجم الصغیر | المعجم الصغير | mujam-saghir-tabarani |
| فرائد السمطين | فرائد السمطين في فضائل المرتضى والبتول والسبطين | faraid-samtayn |
| فرائد الشمطین | فرائد السمطين في فضائل المرتضى والبتول والسبطين | faraid-samtayn |

Built incrementally during extraction. Each new book title is checked against existing variants before creating a new entry.

---

## 4. What's Captured vs What's Lost

Based on empirical testing (10 pages, 42 extractions):

| Category | Coverage | Notes |
|----------|----------|-------|
| Hadith citations (book + author + isnad + text) | 76% of extractions | Core evidence layer — fully modelled |
| Author's Farsi commentary | 10% | Captured as free text |
| Rebuttals | 2% | Low in test sample (tawatur section); more in later pages |
| Rijal evaluations | 0% | Not present in test pages (tawatur section); present in authentication section |
| Poetry as evidence | 3% | **NEW in v3** — now modelled |
| Uncategorized (rhetoric, praise) | 5% | Decorative prose — genuinely outside scope |

**95% coverage overall.** The 5% lost is rhetorical/decorative prose that doesn't carry argumentative weight.

---

## 5. Relationship to book-schemas.md

| This model (Abaqat internals) | book-schemas.md (source books) |
|-------------------------------|-------------------------------|
| BookCitation.author_id | → ScholarEntry.scholar_id |
| RijalEvaluation.grade | Uses JarhGrade 6+6 system |
| BookCitation.book_canonical | → maps to a Schema A/B/C/D/E/F book |
| Isnad.chain_links[].scholar_id | → ScholarEntry for cross-referencing |
| BookCitation.edition | Uses edition reference format |
| Scholar.external_refs | → hawramani_id |

The two models work together: this model structures Abaqat's **internal argument**, book-schemas.md structures the **external source books** Abaqat cites.
