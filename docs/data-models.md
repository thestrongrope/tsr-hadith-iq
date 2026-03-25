# Data Models & Schemas

This document describes the data models, schemas, and relationships across all three repositories in the TSR Hadith Hub project. It includes a critical analysis of the SS (Abaqat al-Anwar) schema and where it diverges from the book's actual structure.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [SS — Abaqatul Anwar Search Engine](#ss--abaqatul-anwar-search-engine)
   - [What the Book Actually Is](#what-the-book-actually-is)
   - [Current Schema](#current-schema)
   - [Schema Mismatch Analysis](#schema-mismatch-analysis)
3. [hadith-hub — React PWA Reader](#hadith-hub--react-pwa-reader)
4. [hadith-data — Content Repository](#hadith-data--content-repository)
5. [Cross-Repo Relationships](#cross-repo-relationships)

---

## Architecture Overview

The project consists of three repositories serving two distinct systems:

```
hadith-data (624 books as ZIPs + manifest)
     │
     │  downloaded via GitHub raw URLs
     ▼
hadith-hub (React PWA — imports ZIPs into IndexedDB)
     │
     │  reads manifest.json + page .txt files
     ▼
  User's browser (offline reading, search)


SS (standalone Flask app — separate dataset)
     │
     │  Abaqatul Anwar only (21K entries)
     ▼
  SQLite + FTS5 + Gemini embeddings → semantic search + AI chat
```

- **SS** is a standalone project focused on one specific book (*Abaqatul Anwar*) with AI-powered semantic search and chat.
- **hadith-hub** + **hadith-data** form a general-purpose hadith library where `hadith-data` serves as the content store and `hadith-hub` is the offline-capable client.

---

## SS — Abaqatul Anwar Search Engine

**Stack**: Flask, SQLite, Gemini AI, NumPy

### What the Book Actually Is

Abaqat al-Anwar (عبقات الانوار) is **not a hadith collection**. It is a **polemical scholarly treatise** (ردیه / refutation) — a genre fundamentally different from tradition-based works like al-Kafi or Bihar al-Anwar.

From the book's own introduction (vol 3, raw_text):
> کتاب حاضر ردیه ای و شرحی است بر کتاب (التحفه الاثنی عشریه) اثر عبدالعزیز بن احمد دهلوی
> "This book is a refutation and commentary on *Tuhfat al-Ithna Ashariyya* by Abdul Aziz ibn Ahmad al-Dihlawi"

**Author**: Mir Syed Hamid Husain Musavi Nishapuri Hindi (d. 1306 AH)
**Editor**: Ghulam Reza Moulana al-Boroujerdi
**Languages**: Farsi (author's commentary) and Arabic (quoted sources)
**Subject**: Systematic defense of key Shia hadiths against Sunni objections, using evidence exclusively from Sunni sources

**Critical framing**: The entire 23-volume work responds to **only one chapter** (باب) of the Tuhfat — **Chapter 7 (باب هفتم), on Imamate**. The Tuhfat itself is a broader anti-Shia work with at least 12 chapters covering different topics. The fact that a single chapter required 23 volumes of refutation demonstrates the extraordinary depth with which each micro-argument is addressed.

#### The Source Work Being Refuted: Tuhfat al-Ithna Ashariyya

Abaqat al-Anwar is a **point-by-point refutation** of *Tuhfat al-Ithna Ashariyya* (التحفة الاثنی عشریة) by Shah Abdul Aziz al-Dihlawi (d. 1239 AH). The Tuhfat is a multi-chapter Sunni anti-Shia polemical work. Abaqat focuses exclusively on **Chapter 7 (باب هفتم در امامت)** — the chapter dealing with the doctrine of Imamate, which itself contains multiple sub-sections organized as عقائد (doctrines/beliefs), e.g., "عقیده ششم از باب هفتم" (the sixth doctrine of Chapter Seven).

The author organizes his entire response into **two مناهج (manaahij / approaches)**, as confirmed by both the Arabic Wikipedia article and the book's own introductions:

- **المنهج الأول** (First Manhaj): Proving Imamate from **Quranic verses (آیات قرآنیة)** — **still in manuscript, never printed**
- **المنهج الثاني** (Second Manhaj): Proving Imamate from **hadiths (أحادیث)** — this is the 23 printed volumes we have

The 23 volumes that exist in the SS repo are entirely the Second Manhaj. Within it, each hadith gets its own section (the volume-level organization shown above). Vol 6's introduction confirms this (line 29): "ان هذا هو الجزء الثانی من المجلد الاول، من مجلدات المنهج الثانی" — "This is the second part of the first volume, of the volumes of the Second Manhaj."

The author systematically works through the Tuhfat's claims within this single chapter, often citing specific page numbers ("تحفه شاهصاحب ص 559", "تحفه اثنا عشریة ص 441"). He also tracks how **later scholars echoed or copied** the same micro-arguments from the Tuhfat or from earlier authorities like Fakhr al-Din al-Razi.

#### The Book's Natural Structure

The book is **not** organized as a collection of traditions. It is a **recursive refutation architecture** — a systematic response to the opponent's claims, where each micro-argument receives its own dedicated treatment:

```
Tuhfat al-Ithna Ashariyya (the source being refuted)
└── Bab/Section (e.g., "باب مطاعن" — chapter on criticisms)
    └── Micro-claim by Shah Sahib (with page ref in Tuhfat)
        │
        ├── Later scholars who copied/echoed the same claim:
        │   Razi → Isfahani → Iji → Taftazani → Jurjani → Qushji → ...
        │   (each quoted verbatim with source reference)
        │
        └── Author's multi-pronged refutation:
            ├── "اشاره" — a specific logical remark (171 across all volumes)
            ├── Biographical dossier of a narrator/scholar under discussion
            ├── Cross-referencing of Sunni sources as counter-evidence
            ├── Exposing contradictions in opponent's own methodology
            └── Numbered sub-arguments (اولا، ثانیا، ثالثا... / اول، دوم، سوم...)
```

This pattern is observable in volume 6 (Hadith al-Ghadir, dalalat section), where the author:
1. Notes that "مقلدین رازی تقلیدا در حدیث غدیر و تواتر آن قدح کرده اند" (imitators of al-Razi have criticized Hadith al-Ghadir's tawatur by imitation)
2. Quotes **six scholars sequentially** — Isfahani, Iji, Taftazani, Jurjani, Qushji, and Ibn Hajar — each repeating variations of the same objection
3. Proceeds to refute the shared claim once with comprehensive evidence

The **"اشاره" (remark)** heading functions as the atomic structural marker — appearing 171 times across 8 volumes — marking individual logical points within the larger refutation.

#### The Genealogy of Discourse: Argument and Rebuttal Lineages

A critical structural feature is that the author tracks **the full genealogy of ideas** — both on the objection side and the rebuttal side. For any given micro-claim, the book maps:

**Argument lineage** (who made this claim, across centuries):
- The original source of the objection (e.g., al-Jahiz's *Kitab al-'Uthmaniyya*, or al-Nazzam's *Mataʿin*)
- Subsequent scholars who adopted, repeated, or adapted the claim
- How the claim eventually reached Shah Sahib's Tuhfat

**Rebuttal lineage** (who already refuted this, before the author):
- Prior Shia scholars who addressed the same objection
- Their specific works and arguments

For example, in vol 3 (lines 1048-1050), the author explicitly maps:
> "Most of these criticisms are the same ones that Shah Sahib has cited, with minor additions, in response to the sixth rational proof, quoting from the Nawasib"

He then traces the rebuttal lineage:
1. **Shaykh al-Mufid** (d. 413 AH) — first refuted these claims in *al-Majalis* and *al-'Uyun wa al-Mahasin*
2. **Sayyid al-Murtada** (d. 436 AH) — summarized al-Mufid's rebuttals in *Fusul* (a condensation of al-Mufid's work)
3. **al-Iskafi** — gave his own rebuttal ("پاسخ شافی اسکافی از هذیانات جاحظ" — "al-Iskafi's comprehensive response to al-Jahiz's ravings")
4. **The author himself** — builds on all prior rebuttals, adding new biographical evidence and Sunni source citations

This means the book functions as a **map of centuries of scholarly conversation** — tracking how objections originate, propagate through imitation, and are countered by successive generations of scholars. This genealogical dimension is entirely absent from the current schema.

Key opponent scholars addressed in the book:
- **شاه صاحب / دهلوی** (Shah Sahib / al-Dihlawi) — the primary opponent (author of the Tuhfat)
- **فخر رازی** (Fakhr al-Din al-Razi) — whose objections were widely copied
- **ابن روزبهان** (Ibn Ruzbehan) — respondent to Allamah al-Hilli
- **ابن تیمیه** (Ibn Taymiyyah) — in Minhaj al-Sunnah
- **تفتازانی** (al-Taftazani) — in Sharh al-Maqasid
- **عضد الدین ایجی** (al-Iji) — in al-Mawaqif
- **جرجانی** (al-Jurjani) — in Sharh al-Mawaqif
- **قوشجی** (al-Qushji) — in Sharh al-Tajrid
- **اصفهانی** (al-Isfahani) — in Tashyid al-Qawa'id
- **حلبی** (al-Halabi), **کشمیری** (al-Kashmiri), and others

#### The Biographical/Bibliographical Dimension (Tarajim & Rijal)

One of the most valuable aspects of Abaqat al-Anwar — and one entirely uncaptured by the current schema — is its **systematic biographical analysis** of the scholars and books it engages with.

When the author cites a Sunni scholar or book, he does not simply quote it. He builds a **comprehensive dossier** by cross-referencing what multiple rijal (biographical criticism) authorities say about that person. The pattern is clearly marked with headings following the formula:

> **ترجمه X بگفتار Y در Z**
> "Biography of [scholar X] according to [authority Y] in [book Z]"

For example, when discussing al-Waqidi's reliability as a narrator, the author compiles evaluations from:

| Heading | Translation |
|---------|------------|
| ترجمه واقدی در کتاب میزان الاعتدال | Biography of al-Waqidi in Mizan al-I'tidal |
| ترجمه واقدی در کتاب تذهیب التهذیب | Biography of al-Waqidi in Tahdhib al-Tahdhib |
| ترجمه واقدی بگفتار ذهبی در عبر فی خبر من غبر | Biography of al-Waqidi by al-Dhahabi in al-'Ibar |
| ترجمه واقدی بگفتار ذهبی در کاشف | Biography of al-Waqidi by al-Dhahabi in al-Kashif |
| ترجمه واقدی بگفتار سمعانی در انساب | Biography of al-Waqidi by al-Sam'ani in al-Ansab |
| ترجمه واقدی بگفتار ابن خلکان در وفیات الأعیان | Biography of al-Waqidi by Ibn Khallikan in Wafayat al-A'yan |

This is not incidental — it is a **core methodological feature**. Across the raw text volumes, there are at least **195 such biographical entries**. The author uses these dossiers to:

1. **Establish credibility** of narrators he relies on — showing that Sunni rijal authorities themselves authenticate them
2. **Expose contradictions** in the opponent's position — demonstrating that a scholar the opponent relies on is considered weak by the opponent's own authorities
3. **Build a bibliographical web** — showing how the same evaluation is corroborated across multiple independent rijal sources (al-Dhahabi's Mizan, Ibn Hajar's Tahdhib, al-Sam'ani's Ansab, etc.)

Each biographical dossier contains structured data:
- **Subject scholar**: name, kunya, nisba, dates (birth/death)
- **Teachers (shuyukh)**: who they narrated from
- **Students (talamidh)**: who narrated from them
- **Evaluations (ahkam)**: jarh (criticism) and ta'dil (authentication) from named authorities
- **Quoted verbatim judgments**: "قال البخاری: متروک" (al-Bukhari said: abandoned), "قال مصعب: ثقة مأمون" (Mus'ab said: trustworthy, reliable)
- **Source book references**: with volume and page numbers

This makes the book function as a **meta-rijal encyclopedia** — arguably the most comprehensive cross-referencing of Sunni biographical literature ever compiled in Farsi, built in service of a theological argument.

The rijal books most frequently cross-referenced include:

| Rijal Book | Author | Frequency |
|-----------|--------|-----------|
| میزان الاعتدال (Mizan al-I'tidal) | al-Dhahabi | Very high |
| تهذیب التهذیب (Tahdhib al-Tahdhib) | Ibn Hajar al-Asqalani | Very high |
| تذکرة الحفاظ (Tadhkirat al-Huffaz) | al-Dhahabi | High |
| عبر فی خبر من غبر (al-'Ibar) | al-Dhahabi | High |
| طبقات الحفاظ (Tabaqat al-Huffaz) | al-Suyuti | High |
| وفیات الأعیان (Wafayat al-A'yan) | Ibn Khallikan | High |
| الانساب (al-Ansab) | al-Sam'ani | High |
| مرآت الجنان (Mir'at al-Jinan) | al-Yafi'i | High |
| الکاشف (al-Kashif) | al-Dhahabi | Moderate |
| سیر اعلام النبلاء (Siyar A'lam al-Nubala) | al-Dhahabi | Moderate |
| طبقات الشافعیة (Tabaqat al-Shafi'iyya) | al-Subki / Ibn Qadi Shuhba | Moderate |
| لسان المیزان (Lisan al-Mizan) | Ibn Hajar al-Asqalani | Moderate |
| کمال فی اسماء الرجال (al-Kamal) | al-Maqdisi | Moderate |

#### Volume Organization by Hadith Topic

Each volume (or group of volumes) is dedicated to defending one specific hadith:

| Volumes | Hadith Being Defended | Notes |
|---------|----------------------|-------|
| 1–10 | Hadith al-Ghadir | 10 volumes — the largest section. Covers sanad (chain), dalalah (meaning), and refutation of all major objections |
| 11 | Hadith al-Manzila | "You are to me as Harun was to Musa" |
| 12 | Hadith al-Wilayah | "He is the wali of every believer after me" |
| 13 | Hadith al-Tayr | The roasted bird hadith |
| 14–15 | Hadith Madinat al-Ilm | "I am the city of knowledge and Ali is its gate" (2 parts) |
| 16 | Hadith al-Tashbih | The resemblance hadith |
| 17 | Hadith al-Nur | The light hadith |
| 18–22 | Hadith al-Thaqalayn | "I leave among you two weighty things" (5 parts) |
| 23 | Hadith al-Safinah | "My Ahl al-Bayt are like the Ark of Noah" |

---

### Current Schema

#### SQLite Database (`hadith.db`)

##### Table: `entries` — 21,456 rows

| Field              | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| `id`               | TEXT PK | Composite ID: `v{vol}_p{page}_{seq}`     |
| `volume`           | INTEGER | Volume number (1–23)                     |
| `page`             | TEXT    | Page reference within volume             |
| `section`          | TEXT    | Section title (Farsi/Arabic)             |
| `sunni_book`       | TEXT    | Sunni source book name (nullable)        |
| `sunni_author`     | TEXT    | Author name with death year              |
| `sunni_volume_page`| TEXT    | Volume/page in the Sunni source          |
| `original_text`    | TEXT    | Full text in Farsi/Arabic                |
| `topics`           | TEXT    | Comma-separated topic tags               |

**Entry breakdown by sunni_source presence:**
- **With sunni_source** (8,406 entries, 39%) — Passages that discuss/cite a specific Sunni book
- **Without sunni_source** (13,050 entries, 61%) — Author's own commentary/analysis passages

##### Table: `citations` — 14,907 rows

| Field      | Type        | Description                          |
|------------|-------------|--------------------------------------|
| `id`       | INTEGER PK  | Auto-increment                       |
| `entry_id` | TEXT FK      | References `entries(id)`             |
| `book`     | TEXT        | Cited book name                      |
| `ref`      | TEXT        | Citation reference (vol/page/hadith) |

- 244 unique citation books referenced
- Average ~0.7 citations per entry

##### Virtual Table: `entries_fts` (FTS5)

Full-text search index on `original_text` and `topics`. Used for BM25-ranked keyword search with LIKE fallback for short queries.

#### Embedding Vectors

| File                 | Description                                      |
|----------------------|--------------------------------------------------|
| `embeddings.npy`     | 6,800 x 768 float32 matrix (Gemini embedding-001)|
| `embedding_ids.json` | JSON array mapping row index → entry ID          |

Used for cosine-similarity semantic search. Minimum similarity threshold: 0.3; returns top 30 results. Note: only 6,800 of 21,456 entries have embeddings.

#### JSON Source Files

##### `abaqatul_anwar_database.json` — 5,874 entries (volumes 2–10)

```json
{
  "id": "v2_p1_001",
  "abaqatul_anwar_ref": {
    "volume": 2,
    "page": "1",
    "section": "مشخصات کتاب"
  },
  "sunni_source": {
    "book": "al-Ma'arif",
    "author": "Ibn Qutayba (d. 276 AH)",
    "volume_page": ""
  },
  "original_text": "...",
  "original_source_citations": [
    { "book": "al-Ma'arif", "ref": "" }
  ],
  "topics": ["Hadith al-Thaqalayn", "Caliphate/Succession"]
}
```

##### `vol1_entries.json` — 318 entries (volume 1)

Same schema. Subject: Hadith al-Ghadir — Sanad and refutation of objections.

##### `new_volumes.json` — 15,264 entries (volumes 11–23)

Same schema. Entry IDs follow `v{volume}_p{page}_{sequence}`.

##### `extracted_hadith.json` — 1,327 hadith + 35 source books

A **secondary, automated extraction** that attempts to pull actual hadith narrations out of the argumentative text using regex pattern matching. This is derivative data, not primary content.

```json
{
  "books": [
    {
      "name": "Fath al-Bari",
      "author": "Ibn Hajar al-Asqalani",
      "description": "Referenced in..."
    }
  ],
  "hadith": [
    {
      "book": "Sahih al-Bukhari",
      "chapter": "Chapter name",
      "hadith_number": "123",
      "narrator_chain": "...",
      "arabic_text": "...",
      "english_text": "...",
      "topic": "Hadith al-Ghadir"
    }
  ]
}
```

#### Topics Taxonomy (34 unique topics)

Ali ibn Abi Talib, Aisha, Bay'a, Caliphate/Succession, Companions (Sahaba), Fadak, Fakhr al-Din al-Razi, Fatimah al-Zahra, Hadith Madinat al-Ilm, Hadith al-Ghadir, Hadith al-Manzila, Hadith al-Nur, Hadith al-Qirtas, Hadith al-Safinah, Hadith al-Tashbih, Hadith al-Tayr, Hadith al-Thaqalayn, Hadith al-Wilayah, Ibn Taymiyyah, Imamate, Linguistic Analysis, Meaning of Mawla, Mubahala, Prophet Muhammad, Quranic Verses, Refutation, Sahih Muslim, Sahih al-Bukhari, Sahihayn critique, Sanad (chain of narration), Saqifa, Tawatur (mass-transmission), Wilayah of Ali, al-Taftazani.

#### Raw Text Sources

| File        | Size    |
|-------------|---------|
| vol_2.txt   | 690 KB  |
| vol_3.txt   | 900 KB  |
| vol_4.txt   | 909 KB  |
| vol_5.txt   | 839 KB  |
| vol_6.txt   | 806 KB  |
| vol_7.txt   | 1.3 MB  |
| vol_8.txt   | 15.5 MB |
| vol_9.txt   | 1.1 MB  |
| vol_10.txt  | 1.5 MB  |

Total: ~23 MB of Farsi/Arabic source text in `raw_text/`. Volumes 11–23 were extracted from `.doc` files via macOS `textutil` (source files not in the repo).

---

### Schema Mismatch Analysis

The current schema was designed as if Abaqat al-Anwar were a hadith collection (like al-Kafi or Sahih al-Bukhari). It is not. The book is **argumentative discourse** — a systematic scholarly refutation. This creates several structural mismatches:

#### 1. Entries are text chunks, not semantic units

**Problem**: The extraction scripts (`convert_vol1.py:254-325`, `extract_new_volumes.py:254-325`) split pages into entries by **character count** (~500–1200 chars), not by logical boundaries. A single argument thread may span 5–10 entries, and a single entry may contain the tail of one argument and the start of another.

**Impact**: Semantic search and AI retrieval often return fragments of arguments rather than complete reasoning chains. The embedding vectors (6,800 of them) encode these arbitrary chunks, meaning cosine similarity finds textually similar fragments, not logically complete arguments.

#### 2. `sunni_source` conflates two different things

**Problem**: The `sunni_source` field is treated as "which Sunni book this hadith comes from," but in Abaqat, it actually means "which Sunni source is being discussed or cited in this passage of argumentation."

- When populated (39% of entries): it indicates a Sunni source the author is engaging with — sometimes quoting it as evidence FOR his position, sometimes citing an opponent who relies on it, sometimes critiquing it
- When empty (61% of entries): the passage is the author's own Farsi analysis, logical reasoning, or transitional text

**Impact**: There is no way to distinguish between "the author cites Sahih al-Bukhari to support his argument" and "the author is refuting someone who cited Sahih al-Bukhari."

#### 3. Missing: the argument/objection layer

**Problem**: The book's most important structural element — the **objection-refutation thread** — is entirely absent from the schema. In the raw text, these are clearly marked with headings like:

- "ابن روزبهان در رد قضیه احراق البیت طبری را جرح کرده" (Ibn Ruzbehan, in rejecting the incident of burning the house, has impugned al-Tabari)
- "فخر رازی نیز در مطالب مذکوره بروایات واقدی اعتنا نکرده" (Fakhr al-Razi also did not attend to the narrations of al-Waqidi in these matters)

These headings identify **who** is making the objection, **what** the objection is, and set up the author's response. The current schema has no concept of this — all entries are flat.

**Impact**: It is impossible to ask "What are all the objections Ibn Taymiyyah raises against Hadith al-Ghadir?" or "How does the author respond to al-Razi's linguistic argument about the meaning of mawla?" These are the natural queries for this type of work.

#### 4. Topics are auto-detected, not scholarly

**Problem**: Topics are assigned by regex keyword matching (`convert_vol1.py:61-73`, `extract_new_volumes.py:29-74`), not by scholarly classification. This means:
- A passage mentioning "بخاری" gets tagged "Sahih al-Bukhari" even if the author is criticizing its methodology
- The distinction between the hadith being defended (volume-level) and the sub-topic of a specific argument is lost
- Some tags are source book names (Sahih al-Bukhari, Sahih Muslim) mixed with actual topic categories (Caliphate/Succession, Linguistic Analysis)

#### 5. The biographical/bibliographical layer is completely lost

**Problem**: The book contains at least 195 structured biographical dossiers (tarajim) — systematic cross-referenced evaluations of scholars compiled from multiple Sunni rijal authorities. These are clearly marked with headings ("ترجمه X بگفتار Y در Z") and contain highly structured data: scholar names, dates, teacher-student chains, jarh/ta'dil evaluations with named authorities, and precise source references.

None of this is captured in the schema. The biographical entries are simply part of the `original_text` blob, indistinguishable from any other passage. The `sunni_source` field captures at most one book name per entry, losing the multi-source cross-referencing that is the entire point of these dossiers.

**Impact**: This is arguably the book's most unique scholarly contribution — a Farsi-language meta-encyclopedia of Sunni rijal literature. The current schema makes it impossible to query "What do Sunni authorities say about narrator X?" or "Which narrators does al-Dhahabi authenticate that Ibn Taymiyyah rejects?" — exactly the types of questions this book was written to answer.

**What could be captured**:
- Scholar entity (name, kunya, nisba, birth/death dates)
- Evaluation records (evaluator, judgment, source book, volume/page)
- Teacher-student relationships
- The argumentative context (why the author compiled this dossier)

#### 6. `extracted_hadith.json` is a lossy secondary extraction

**Problem**: This file attempts to extract actual hadith narrations from the argumentative text using regex (`extract_hadith.py`). But in Abaqat, hadiths appear embedded within the author's arguments — they are evidence within discourse, not standalone records. The extraction:
- Uses bracket `[...]` and guillemet `«...»` matching to find quoted text
- Checks for hadith markers (حدثنا, قال رسول الله, etc.)
- Assigns sources based on nearby book name mentions
- Results in 1,327 entries with significant noise

**Impact**: These extracted hadiths are divorced from the argumentative context that gives them meaning. In the original book, a hadith is cited to prove a point — without that point, the citation loses its scholarly value.

#### Summary: What the Schema Captures vs. What the Book Contains

| Book's Actual Structure | Schema Representation | Gap |
|------------------------|----------------------|-----|
| **Hadith being defended** (volume-level) | `volume` number + `topics` tag | Implicit only; no explicit hadith-level metadata |
| **Opponent scholar** (who objects) | Not captured | Completely missing. Mentioned names detectable only via text search |
| **Objection** (what is claimed) | Not captured | Completely missing. Mixed into `original_text` chunks |
| **Author's refutation** (the core content) | `original_text` (fragmented) | Split into arbitrary ~800-char chunks across entries |
| **Sunni evidence cited** | `sunni_source` + `citations` | Captured but without directionality (for/against) |
| **Biographical dossiers (tarajim)** | Not captured | 195+ structured scholar evaluations lost in `original_text` blob. No scholar entities, no evaluation records, no cross-referencing of rijal sources |
| **Rijal source cross-references** | Not captured | The multi-authority evaluation pattern (what al-Dhahabi says vs. what Ibn Hajar says about the same narrator) is the book's unique scholarly contribution — entirely flattened |
| **Argument lineage** (who originated a claim, who copied it) | Not captured | The chain of imitation (Razi→Isfahani→Iji→Taftazani→Jurjani→Qushji→Shah Sahib) is flattened. No way to trace how a micro-argument propagated across centuries |
| **Rebuttal lineage** (prior scholars who already refuted) | Not captured | The author cites al-Mufid, Sayyid al-Murtada, al-Iskafi, etc. as prior responders. These chains of scholarly response are lost in text chunks |
| **Tuhfat source references** | Not captured | The author cites specific pages in the Tuhfat he's responding to ("تحفه ص 559"). No link between a refutation and the exact passage in the opponent's book being addressed |
| **Farsi commentary** | `original_text` | Present but mixed with Arabic quotations, no language separation |
| **Page/volume reference** | `volume`, `page`, `id` | Accurately captured |

---

## hadith-hub — React PWA Reader

**Stack**: React, TypeScript, Vite, IndexedDB
**Purpose**: Offline-capable progressive web app for reading hadith texts.

### IndexedDB Schema

**Database name**: `hadithHub`, **Version**: 1

#### Store: `books` (keyPath: `id`)

```typescript
interface Book {
  id: string;            // e.g., "01348"
  title: string;         // Book title (Arabic or English)
  author?: string;       // Author name
  volumes: number;       // Total number of volumes
  description?: string;
  importedAt?: number;   // Unix timestamp (ms)
}
```

#### Store: `volumes` (keyPath: `['bookId', 'volume']`)

Indexes: `bookId` (non-unique)

```typescript
interface VolumeInfo {
  bookId: string;        // References Book.id
  volume: number;        // Volume number
  totalPages: number;    // Total pages in this volume
  importedAt?: number;   // Unix timestamp (ms)
}
```

#### Store: `pages` (keyPath: `['bookId', 'volume', 'page']`)

Indexes: `bookId` (non-unique), `bookVolume` (non-unique)

```typescript
interface Page {
  bookId: string;        // References Book.id
  volume: number;        // Volume number
  page: number;          // Page number (1-indexed)
  text: string;          // JSON string array or plain text
}
```

### Additional Interfaces

#### BookManifest (inside ZIP files)

```typescript
interface BookManifest {
  id: string;
  title: string;
  author?: string;
  description?: string;
  volumes: {
    volume: number;      // May be string "001" in actual files
    totalPages: number;
  }[];
  createdAt: number;     // Unix timestamp (ms)
  version: string;       // Format version (e.g., "1.0")
}
```

#### Translation (not yet persisted in IndexedDB)

```typescript
interface Translation {
  bookId: string;
  volume: number;
  page: number;
  language: string;      // e.g., "en"
  text: string;
  translatedAt: number;  // Unix timestamp (ms)
}
```

#### SearchResult (returned from Web Worker)

```typescript
interface SearchResult {
  bookId: string;
  bookTitle: string;
  volume: number;
  page: number;
  snippet: string;       // Text excerpt with context
  matchIndex: number;    // Character position of match
}
```

#### AvailableBook (from remote manifest)

```typescript
interface AvailableBook {
  slug: string;
  bookId: string;
  sourceBookId?: string;
  bookTitle: string;
  bookTitleAr?: string;
  bookTitleEn?: string;
  author?: string;
  authorAr?: string;
  authorEn?: string;
  total: number;
  downloads: AvailableDownload[];
  bookLanguage?: 'ar' | 'fa' | 'en';
}
```

#### AvailableDownload

```typescript
interface AvailableDownload {
  filename: string;
  volume: number;
  size: number;          // Bytes
  sizeFormatted: string; // e.g., "2.5 MB"
  downloadUrl: string;
  bookId: string;
  bookTitle: string;
  language?: string;
}
```

### Static Book Metadata (`src/bookMetadata.ts`)

```typescript
interface BookMetadata {
  id: string;
  titleAr: string;
  titleEn: string;
  authorAr: string;
  authorEn: string;
  volumes?: number;
  century?: number;      // Hijri century
  deathYear?: number;    // Author's death year (Hijri)
  language?: string;     // "ar", "fa", "en"
}
```

- 60+ books catalogued
- Sect categorization: Shia (default), ~12 Sunni book IDs in `SUNNI_BOOK_IDS`

### Search System

- **Engine**: Web Worker (`search.worker.ts`)
- **Modes**: `exact` (literal match) | `root` (Arabic normalization)
- **Arabic normalization**: Strips diacritics, normalizes alef/waw/yaa variations, taa marbuta → haa, alef maqsura → yaa
- **Cache**: LRU, 50 entries max, 5-minute TTL

### Enumerations

| Type             | Values                                                          |
|------------------|-----------------------------------------------------------------|
| ViewType         | `home`, `library`, `reader`, `import`, `settings`, `search`, `searchResults` |
| Language         | `en`, `ar`                                                      |
| Theme            | `light`, `dark`                                                 |
| ArabicFont       | `amiri`, `naskh`, `nastaliq`, `scheherazade`                    |
| ReadingMode      | `pagination`, `scroll`                                          |
| SearchMode       | `exact`, `root`                                                 |
| InputMode        | `arabic`, `roman`                                               |
| SectFilter       | `all`, `shia`, `sunni`                                          |
| LanguageFilter   | `all`, `ar`, `fa`, `en`                                         |

### localStorage Keys

| Key                       | Type   | Default        |
|---------------------------|--------|----------------|
| `hadithHub_language`      | string | `"en"`         |
| `hadithHub_theme`         | string | `"light"`      |
| `hadithHub_arabicFont`    | string | `"amiri"`      |
| `hadithHub_readingMode`   | string | `"pagination"` |

---

## hadith-data — Content Repository

**Purpose**: Static data backend for `hadith-hub`, hosted on GitHub.
**Scale**: 624 books, 1,421 ZIP files, ~547 MB total.

### Manifest (`books.json`)

```json
{
  "version": 1,
  "generated": "2026-01-22T18:16:30.772Z",
  "baseUrl": "https://raw.githubusercontent.com/hadithhub12/hadith-data/main",
  "totalBooks": 624,
  "totalTranslations": 0,
  "books": [
    {
      "slug": "al-kafi-01348",
      "id": "113770",
      "titleAr": "الكافي",
      "titleEn": "Al Kafi",
      "authorAr": "كلینی، محمد بن یعقوب",
      "authorEn": "",
      "sect": "shia",
      "language": "ar",
      "volumes": [
        {
          "volume": 1,
          "filename": "al-kafi-01348-v001.zip",
          "size": 625119,
          "sizeFormatted": "0.60 MB"
        }
      ],
      "totalVolumes": 8,
      "totalSize": 625119,
      "totalSizeFormatted": "0.60 MB"
    }
  ]
}
```

### ZIP File Structure

```
{book-slug}-v{volume}.zip
├── manifest.json
└── volumes/
    └── {volume}/
        ├── 1.txt
        ├── 3.txt
        ├── 5.txt
        └── ...
```

#### In-ZIP manifest.json

```json
{
  "id": "19236",
  "title": "ترتیب الأمالي",
  "author": "محمودی، محمدجواد",
  "slug": "book-19236",
  "description": "Volume 001",
  "volumes": [
    { "volume": "001", "totalPages": 646 }
  ],
  "createdAt": 1769038776921,
  "version": "1.0"
}
```

#### Page Files (`volumes/{vol}/{page}.txt`)

JSON arrays of strings, each element is a paragraph:

```json
[
  "Text paragraph 1...",
  "Text paragraph 2...",
  "Text paragraph 3..."
]
```

### Collection Statistics

| Metric              | Value                        |
|---------------------|------------------------------|
| Total books         | 624                          |
| Total ZIP files     | 1,421                        |
| Total size          | ~547 MB                      |
| Arabic books        | 465                          |
| Persian books       | 159                          |
| Sect                | All Shia                     |
| Translations        | 0                            |
| Largest book        | Bihar al-Anwar (110 vols, 48.84 MB) |

### Notable Collections

| Book                          | Volumes | Size     |
|-------------------------------|---------|----------|
| Bihar al-Anwar                | 110     | 48.84 MB |
| Wasa'il al-Shi'a              | 30      | 12.53 MB |
| Mira'a al-'Uqul               | 26      | 12.27 MB |
| Mustadrak al-Wasa'il          | 18      | 11.26 MB |
| Jami' al-Ahadith (Manabi' Fiqh) | —     | 16.68 MB |

---

## Cross-Repo Relationships

### Data Flow: hadith-data → hadith-hub

1. `hadith-hub` fetches `books.json` from `hadith-data` GitHub raw URL
2. User selects books/volumes to download
3. ZIP files are fetched, extracted, and stored in IndexedDB:
   - ZIP `manifest.json` → `books` + `volumes` stores
   - `volumes/{vol}/{page}.txt` → `pages` store
4. All reading and search happens locally in the browser

### SS (Independent System)

- Shares no data or code with the other two repos
- Focused on a single scholarly work (*Abaqatul Anwar*)
- Uses server-side AI (Gemini) for semantic search and chat
- Maintains its own SQLite database and embedding vectors

### Key Differences

| Aspect          | SS                        | hadith-hub + hadith-data      |
|-----------------|---------------------------|-------------------------------|
| Scope           | 1 book, 21K entries       | 624 books, 1,421 volumes      |
| Content type    | Argumentative treatise    | Hadith collections (tradition-based) |
| Storage         | SQLite (server)           | IndexedDB (client)            |
| Search          | FTS5 + vector similarity  | Web Worker text search         |
| AI              | Gemini chat + embeddings  | None                           |
| Offline         | No (server-dependent)     | Yes (PWA)                      |
| Languages       | Farsi/Arabic              | Arabic, Persian                |
| Sect coverage   | Sunni sources cited       | Shia collections only          |

### The Genre Gap

The hadith-hub/hadith-data system is well-suited to its content: tradition-based books have a natural structure of `book → volume → page → text`, and the flat page-based schema captures this accurately.

The SS system applies this same page-based model to a fundamentally different genre. Abaqat al-Anwar's content is **argumentative** — its natural unit is the **objection-refutation thread**, not the individual page or hadith. The current schema works adequately for full-text search (finding passages that mention a topic), but loses the argumentative structure that gives those passages their scholarly meaning.
