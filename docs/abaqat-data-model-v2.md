---
title: "Abaqat al-Anwar — Data Model v2"
subtitle: "Refined schema incorporating structural analysis of Vol 23 (Hadith al-Safinah). Builds on v1 with new structural containers, narrator citation entity, and volume-level patterns."
date: "March 2026"
---

# Abaqat al-Anwar — Data Model v2

## What Changed from v1

The v1 model was built primarily from the Ghadir volumes (1–10), where the dominant pattern is **Claim → Response → Dossier**. Structural analysis of Vol 23 (Hadith al-Safinah) revealed that this flow is only one of several organizational patterns the author uses. The major additions:

1. **Volume Sections** — a structural container layer that captures how each volume is actually organized (Tamhid, Tawatur Defense, Dalalah, Dehlavi Response, Appendix)
2. **Narrator Citation** — a new entity for the "اما [Scholar] narrated this hadith in [Book]..." pattern, which is the backbone of sanad-focused volumes
3. **Tanbih** — authorial notices/digressions, a recurring structural element
4. **Dalalah Proof** — standalone numbered proofs of meaning, not always nested under a Response
5. **Recognition that volumes follow different organizational patterns** depending on whether they focus on Sanad (chain) or Dalalah (meaning)

---

## 1. The Two Volume Patterns

### Pattern A: Sanad-First (Chain Defense)

Used when Dehlavi or Ibn Taymiyyah attacks the hadith's **authenticity**.

```
Volume
├── Tamhid (introduction, opponent's denial)
├── Tawatur Defense (stacking 20–40 Sunni scholars who narrated it)
│     └── Narrator Citation × N ("اما [Scholar]...")
├── Dalalah (proving the hadith's meaning supports Imamate)
│     └── Numbered Proofs (وجه اول، وجه دوم...)
├── Dehlavi Section (claims + author's responses)
│     ├── Dehlavi Claim
│     ├── Author's Response (اقول)
│     └── Biographical Dossiers + Tanbih notices
└── Appendices (indexes)
```

**Observed in:** Vol 23 (Safinah), likely Vols 1–5 (Ghadir Sanad), 11 (Manzila), 12 (Wilayah), 13 (Tayr), 17 (Nur), 18–22 (Thaqalayn)

### Pattern B: Response-First (Claim-by-Claim Refutation)

Used when Dehlavi makes **specific textual or logical arguments** about the hadith's meaning.

```
Volume
├── Dehlavi Claim 1 (قال الفاضل المحدث التحرير)
│     ├── Author's Response (اقول)
│     ├── Numbered Arguments (اول، دوم، سوم)
│     ├── Biographical Dossiers (ترجمه × N)
│     ├── Argument Lineage (مقلدین chain)
│     └── Rebuttal Lineage (prior scholars who answered)
├── Dehlavi Claim 2
│     └── ...
└── Appendices
```

**Observed in:** Vols 6–10 (Ghadir Dalalah), likely Vols 14–15 (Madinat al-Ilm), 16 (Tashbih)

### Pattern C: Hybrid

Some volumes combine both — proving authenticity first, then responding to specific claims.

---

## 2. Entity Types (Revised)

### 2.0 Volume Section (مبحث) — NEW

The top-level structural container within a volume. Every piece of content belongs to exactly one section.

| Field | Description |
|-------|-------------|
| Volume | Which volume this section belongs to |
| Section type | TAMHID, TAWATUR_DEFENSE, DALALAH, DEHLAVI_SECTION, AUTHOR_RESPONSE, TANBIH, APPENDIX |
| Title (Farsi) | Section heading as it appears in text |
| Title (English) | Translation |
| Start/end position | Line numbers or page references in the source text |
| Parent section | For subsections (e.g., a Tanbih within a Dalalah section) |
| Description | Brief summary of what this section contains |

**Why this matters:** The v1 model assumed all content flows from Claim → Response. In reality, the Tawatur Defense section (which can be 60% of a volume) is not responding to a specific claim — it's preemptively establishing the hadith's authenticity before any specific debate begins.

### 2.1 Defended Hadith (حدیث مدافع‌عنه)

*Unchanged from v1.* The hadith being defended across one or more volumes.

| Field | Description | Example |
|-------|-------------|---------|
| Name (Arabic) | Standard name | حديث السفينة |
| Name (English) | Transliterated | Hadith al-Safinah |
| Hadith text | The full Arabic text of the tradition | مثل أهل بيتى كسفينة نوح من ركبها نجا ومن تخلف عنها هلك |
| Volumes | Which volumes cover this hadith | [23] |
| Section focus | SANAD, DALALAH, or BOTH | BOTH |

### 2.2 Opponent's Claim (نقل كلام الخصم)

*Expanded from v1.* Now tracks which opponent made the claim — not only Dehlavi but also Ibn Taymiyyah, Fakhr al-Razi, etc.

| Field | Description | Example |
|-------|-------------|---------|
| Claim text | Verbatim quotation | لا يعرف له إسناد أصلاً لا صحيح ولا ضعيف |
| Claimant | Who made this claim | Ibn Taymiyyah |
| Source | Where the claim appears | Minhaj al-Sunnah |
| Claim type | AUTHENTICITY_DENIAL, LINGUISTIC, CHAIN_ATTACK, FABRICATION, MEANING_ATTACK | AUTHENTICITY_DENIAL |
| Target hadith | Which hadith is being attacked | Hadith al-Safinah |
| Attack strategy | Specific technique used | Claims no isnad exists in any reliable book |

**Change from v1:** Dehlavi is not always the direct opponent. In Vol 23, the primary target is **Ibn Taymiyyah's** denial, and Dehlavi's claims come later. The Tuhfat Claim entity is now generalized to "Opponent's Claim."

### 2.3 Narrator Citation (إخراج / رواية) — NEW

The single most common structural unit in sanad-focused volumes. Each one proves that a specific Sunni authority transmitted the defended hadith.

| Field | Description | Example |
|-------|-------------|---------|
| Opening formula | Always begins with "اما" | اما شافعى؛ بس اين حديث شريف را... |
| Narrator scholar | Who narrated/transmitted | al-Shafi'i |
| Source book | Which book contains it | (his own musnad) |
| Chain (isnad) | The transmission chain given | Abu Dharr → ... → the Prophet |
| Hadith text variant | The specific wording in this source | مثل أهلبيتى كسفينة نوح... |
| Companion source | Which Sahabi the chain goes through | Abu Dharr al-Ghifari |
| Position in sequence | Order in the tawatur stack | 1 of 40 |
| Author's commentary | Farsi commentary after the citation | (if any) |

**Textual marker:** Always introduced by `اما [Scholar name]` at the start of a line.

**Argumentative purpose:** These are NOT evaluations of the narrator's reliability — they are *proof of transmission*. The author stacks 40 of them to prove tawatur (mass-transmission), making it impossible for the opponent to claim "this hadith has no isnad."

**Vol 23 evidence:** 40 narrator citations spanning lines 408–3373, from Imam al-Shafi'i (d. 204 AH) to contemporary scholars of the author's time.

### 2.4 Author's Response (جواب / اقول)

*Unchanged from v1.* The container for the author's rebuttal, introduced by "اقول".

| Field | Description |
|-------|-------------|
| Opening formula | اقول مستعینا بلطف اللطیف الخبیر |
| Target claim | Which opponent's claim this responds to |
| Response approach | SANAD / DALALAH / BIOGRAPHICAL / CONTRADICTION / LINGUISTIC |
| Conclusion | مخدوش (flawed) or باطل (void) |

### 2.5 Dalalah Proof (وجه دلالت) — REVISED

*Upgraded from "Numbered Argument" in v1.* Can be standalone (not nested under a Response) when proving the hadith's meaning independently.

| Field | Description | Example |
|-------|-------------|---------|
| Number | Ordinal position | وجه اول، وجه دوم |
| Proof text | The argument | This hadith proves Imamate because... |
| Evidence type | Linguistic / textual / logical / historical | Logical |
| Parent | Either a Response or a standalone Dalalah section | Dalalah section |
| Sources cited | Books and scholars referenced | — |

**Vol 23 evidence:** 11 وجوه (aspects of proof) spanning lines 3374–3994, proving that "like Noah's ark" implies obligatory following of Ahl al-Bayt.

### 2.6 Biographical Dossier (ترجمه)

*Unchanged from v1.* Cross-referenced scholar evaluation from multiple rijal books.

| Field | Description |
|-------|-------------|
| Heading | « ترجمة [Scholar] از [Rijal Book] » |
| Subject scholar | Who is being evaluated |
| Dossier type | Full biographical, Brief evaluation, Comparative, Polemical |
| Argumentative purpose | Why the author evaluates this scholar here |
| Evaluations | List of Rijal Evaluations (see 2.7) |

### 2.7 Rijal Evaluation (جرح / تعدیل)

*Unchanged from v1.* Individual evaluation within a dossier.

| Field | Description |
|-------|-------------|
| Evaluator | Who made the judgment (e.g., Ahmad ibn Hanbal) |
| Term | The rijal term used (ثقة، كذاب، متروك...) |
| Category | Positive (تعدیل) or Negative (جرح) |
| Verbatim Arabic | The exact quote |
| Source reference | Which rijal book this comes from |

### 2.8 Tanbih (تنبيه وايقاظ) — NEW

Authorial notice, digression, or warning. A recurring structural element throughout the book.

| Field | Description | Example |
|-------|-------------|---------|
| Title | Heading text | « تنبيه وايقاظ » |
| Content summary | What the notice is about | Warning about Shah Sahib's misunderstanding of Hadith Safinah |
| Related section | Which section this tanbih relates to | Dalalah section |
| Length | Line count | 323 lines |

**Vol 23 evidence:** 10 tanbih notices, some very substantial (500–2000 lines). They function as extended authorial commentaries, digressions into related topics, or corrections of common misunderstandings.

### 2.9 Scholar (عالم / راوی)

*Unchanged from v1.*

| Field | Description |
|-------|-------------|
| Name (Arabic, Farsi, English) | Full name with kunya, nisba |
| Birth / Death | In AH |
| Role | Narrator, Evaluator, Opponent, Author cited |
| Teachers / Students | Scholarly lineage |
| School | Hanafi, Shafi'i, Hanbali, Maliki, Mu'tazili, Shi'i, etc. |

### 2.10 Source Book (کتاب)

*Unchanged from v1.*

| Field | Description |
|-------|-------------|
| Name (Arabic, English) | Standard title |
| Author | Link to Scholar entity |
| Type | rijal / hadith / tafsir / tarikh / kalam / fiqh / adab / lexicon |

### 2.11 Citation (استناد)

*Expanded from v1.* Now includes the citation context taxonomy developed during Vol 23 extraction.

| Field | Description |
|-------|-------------|
| Book | Link to Source Book |
| Volume / Page | Reference if given |
| Direction | EVIDENCE_FOR / EVIDENCE_AGAINST / CROSS_REFERENCE / SOURCE_REFUTED |
| Context | PRIMARY_REBUTTAL / AUTHOR_TAWTHIQ / AUTHOR_TAJRIH / HADITH_SOURCE / TAWATUR_PROOF / CONTRADICTION / ARGUMENT_LINEAGE / REBUTTAL_LINEAGE / LINGUISTIC / CROSS_REF |
| Context detail | Why this citation is made here |
| Subject scholar | If inside a dossier, who is being evaluated |
| Raw quote | Surrounding source text for locating the citation |

### 2.12 Argument Lineage (سلسلة الاستدلال)

*Unchanged from v1.* Traces who originated a claim and who copied it.

### 2.13 Rebuttal Lineage (سلسلة الجواب)

*Unchanged from v1.* Traces prior scholars who already answered the same claim.

---

## 3. How Entities Connect

### Level 0 — The Volume Structure

```
Volume 23 (Hadith al-Safinah)
├── [TAMHID] Author's Preface (L259–407)
├── [TAWATUR] 40 Narrator Citations (L408–3373)
│     ├── Narrator Citation: al-Shafi'i → Abu Dharr
│     ├── Narrator Citation: Ahmad ibn Hanbal → ...
│     ├── ... (38 more)
│     └── Narrator Citation: Hasan al-Zaman (contemporary)
├── [DALALAH] 11 Proofs of Meaning (L3374–3994)
│     ├── Dalalah Proof 1 (وجه اول)
│     ├── ...
│     └── Dalalah Proof 11 (وجه يازدهم)
├── [RESPONSE] Author's Responses (L3995–7868)
│     ├── Author Response (اقول)
│     ├── Tanbih notices
│     ├── Biographical Dossiers
│     │     └── Rijal Evaluations
│     └── Aqidah sections (Sunni beliefs about each Imam)
├── [DEHLAVI] Dehlavi Claims + Responses (L7869–13212)
│     ├── Dehlavi Claim (جواب استدلالات فاسده...)
│     ├── Author Response (اقول)
│     ├── Tanbih notices
│     └── Dehlavi Claim 2
└── [APPENDIX] Indexes (L13213–17690)
```

### Level 1 — The Target

A *Defended Hadith* (e.g., Safinah) is attacked by one or more *Opponent's Claims* — from Dehlavi, Ibn Taymiyyah, or others. The author's defense unfolds across the volume sections.

### Level 2 — The Defense

**If sanad-focused:** The volume opens with *Narrator Citations* stacked to prove tawatur, then moves to *Dalalah Proofs* and finally *Responses* to specific claims.

**If dalalah-focused:** The volume opens directly with *Opponent's Claims* and *Author's Responses* containing *Numbered Arguments* and *Biographical Dossiers*.

### Level 3 — The Evidence

Each *Biographical Dossier* is about a *Scholar*, quotes from a *Source Book*, and contains *Rijal Evaluations*. Each *Narrator Citation* links a *Scholar* to a *Source Book* and provides a transmission chain.

### Level 4 — The Genealogy

*Argument Lineages* trace copied claims. *Rebuttal Lineages* trace prior refutations.

---

## 4. Entity Relationship Summary

| Entity | Arabic | Type | Links To |
|--------|--------|------|----------|
| **Volume Section** | مبحث | Container | Volume, child Sections |
| **Defended Hadith** | حدیث | Core | Volumes, Opponent's Claims |
| **Opponent's Claim** | نقل كلام الخصم | Core | Claimant Scholar, Target Hadith, Responses |
| **Narrator Citation** | إخراج / رواية | NEW | Narrator Scholar, Source Book, Hadith, Companion |
| **Author's Response** | جواب / اقول | Core | Target Claim, contains: Proofs + Dossiers + Citations |
| **Dalalah Proof** | وجه دلالت | Revised | Parent (Response or standalone section) |
| **Biographical Dossier** | ترجمه | Core | Subject Scholar, Source Book, Evaluations |
| **Rijal Evaluation** | جرح / تعدیل | Core | Evaluator Scholar, Term, Source Book |
| **Tanbih** | تنبيه | NEW | Related section, content summary |
| **Scholar** | عالم / راوی | Reference | Teachers, Students, School |
| **Source Book** | کتاب | Reference | Author Scholar, Book type |
| **Citation** | استناد | Link | Source Book, Context, Direction, Subject |
| **Argument Lineage** | سلسلة الاستدلال | Genealogy | Scholars chain, Target Claim |
| **Rebuttal Lineage** | سلسلة الجواب | Genealogy | Scholars chain, Target Response |

---

## 5. What We Measured (Updated)

### Vol 23 (Hadith al-Safinah) — Structural Parse

| Metric | Count | Source |
|--------|-------|--------|
| Volume sections | 74 | Deterministic regex parse |
| Narrator Citations (اما) | 40 | Regex on "^اما" |
| Dalalah Proofs | 11 (وجوه) | From TOC |
| Biographical Dossiers | 5 | Regex on "درترجمه" |
| Author's Responses (اقول) | 3 | Regex on "^اقول" |
| Tanbih notices | 10 | Regex on "تنبيه" |
| Dehlavi Claims + Responses | 3 | Regex on "شاهصاحب" |
| Appendix sections | 11 | Regex on "فهرست" |
| Total citations extracted | 518 | Grok 4.1 Fast + Flash Lite fallback |
| Unique books cited | 379 | From citation extraction |
| Unique authors cited | 354 | From citation extraction |

### Citation Context Distribution (Vol 23)

| Context | Count | % | Description |
|---------|-------|---|-------------|
| HADITH_SOURCE | 218 | 42% | Primary hadith texts from Sunni collections |
| PRIMARY_REBUTTAL | 117 | 23% | Direct counter-arguments |
| AUTHOR_TAWTHIQ | 77 | 15% | Establishing scholar reliability (positive) |
| AUTHOR_TAJRIH | 32 | 6% | Destroying scholar reliability (negative) |
| REBUTTAL_LINEAGE | 28 | 5% | Prior scholars who already refuted |
| CROSS_REF | 14 | 3% | Internal references |
| ARGUMENT_LINEAGE | 8 | 2% | Tracing who copied a claim |
| TAWATUR_PROOF | 7 | 1% | Mass-transmission stacking |
| SUB_CLAIM_REBUTTAL | 7 | 1% | Subsidiary counter-points |
| LINGUISTIC | 8 | 2% | Lexical/grammatical evidence |

**Key insight:** HADITH_SOURCE (42%) dominates over AUTHOR_TAWTHIQ (15%) in this volume — confirming that Vol 23 is primarily about **proving the hadith exists in Sunni books** rather than evaluating narrators. This is the opposite of the Ghadir Sanad volumes where dossier-building dominates.

---

## 6. Questions for the Scholar (Updated)

Original questions from v1 remain. Additional questions based on Vol 23 analysis:

1. **Narrator Citation pattern:** The "اما [Scholar]" structure appears 40 times in Vol 23. Is this the standard pattern across all sanad-focused volumes? Do the Ghadir volumes (1–5) follow the same stacking approach?

2. **Tanbih function:** We found 10 تنبيه notices in Vol 23, some spanning 500–2000 lines. Are these digressions or essential parts of the argument? Should they be modeled as independent sections or as subsections of whatever precedes them?

3. **Aqidah sections:** Vol 23 includes sections on "Sunni beliefs about Imam Ja'far al-Sadiq" etc. — proving that Sunnis respected each Imam. Is this unique to Safinah or does it appear in other volumes?

4. **Ibn Taymiyyah vs Dehlavi:** In Vol 23 the primary opponent is Ibn Taymiyyah (who denies any isnad exists), not Dehlavi. The Dehlavi section comes later. Is this pattern common — different opponents for different hadiths?

5. **Volume organization:** Does the author consciously organize volumes as "sanad-first" vs "claim-by-claim"? Or is this our analytical framework?

---

## 7. Source Files (Updated)

| File | Content |
|------|---------|
| `docs/abaqat-data-model-strategy.md` | v1 of this document (Ghadir-based model) |
| `docs/abaqat-data-model-v2.md` | This document (refined with Vol 23 analysis) |
| `docs/volume-structure/vol23-structure.json` | Structural parse of Vol 23 (74 sections with line boundaries) |
| `docs/volume-structure/vol23-sections/` | Each section as a separate text file |
| `docs/citation-extraction/vol23-grok.json` | 518 citations extracted with context taxonomy |
| `docs/citation-extraction/vol23-citation-map.html` | Interactive HTML visualization |
| `docs/source-books-catalog.md` | 61 rijal books catalog for cross-referencing |
| `scripts/compare_models_citations.py` | Citation extraction script (Grok + Flash Lite fallback) |
| `scripts/parse_volume_structure.py` | Structural parsing script |
