---
title: "Abaqat al-Anwar — Data Model Strategy"
subtitle: "A proposed schema for digitally capturing the structural, biographical, and argumentative dimensions of the book. For review by subject-matter experts."
date: "March 2026"
---

# Abaqat al-Anwar — Data Model Strategy

## Purpose of This Document

This document proposes a data model for digitally representing the content of Abaqat al-Anwar. The goal is to move beyond the current flat-text storage (21,000 text chunks in a database) to a structured representation that captures:

- **What** the author is responding to (which specific claim from the Tuhfat)
- **How** he responds (which argumentative technique)
- **Who** he evaluates (which scholars, from which rijal sources)
- **What evidence** he cites (which books, with what directionality)

This is not a software specification — it is a scholarly structural analysis meant to be validated by experts in the book before implementation.

---

## 1. The Book's Context

### What Abaqat al-Anwar Is

A polemical scholarly treatise (ردیه) by Mir Hamid Husain Musavi (d. 1306 AH), written in Farsi with embedded Arabic quotations. It is a systematic, point-by-point refutation of one chapter of the Tuhfat al-Ithna Ashariyya by Shah Abdul Aziz al-Dihlawi (d. 1239 AH).

### What It Responds To

**Chapter 7 (باب هفتم في الإمامة)** of the Tuhfat — the chapter on Imamate. The Tuhfat has 12 chapters; Abaqat responds to this one chapter only.

Within Chapter 7, Dehlavi refutes three categories of Shia proof for the Imamate of Ali ibn Abi Talib:

| Category | Count | What Abaqat Responds With |
|----------|-------|---------------------------|
| Quranic verses (آیات) | 7 verses | المنهج الأول — Quranic proofs (still in manuscript, never printed) |
| Hadiths (احادیث) | 12 traditions | المنهج الثاني — Hadith proofs (the printed volumes) |
| Rational arguments (دلایل عقلیه) | 6 arguments | Addressed within the hadith volumes |

### What We Have

- **10 printed volumes** (covering Hadith al-Ghadir only — Sanad in vols 1-5, Dalalat in vols 6-10)
- **23 volumes** as djvu-extracted OCR text (covering all hadiths)
- **The full text of the Tuhfat** (OCR'd Farsi)
- **Chapter 7 extracted separately** with Gemini-analyzed argument map

---

## 2. The Building Blocks (Entity Types)

Based on deep structural analysis of the text using Gemini 3.1 Pro, the book is composed of these recurring structural units:

### 2.1 The Opponent's Claim (نقل کلام الخصم)

The atomic target being refuted. Dehlavi's specific objection, quoted verbatim.

| Field | Description | Example |
|-------|-------------|---------|
| Claim text | The verbatim quotation | قال الفاضل المحدث التحرير: ... |
| Source | Where Dehlavi wrote this | Tuhfat, Chapter 7, p.XXX |
| Claim type | verse / hadith / rational | hadith |
| Specific target | Which verse or hadith | Hadith al-Ghadir |
| Dehlavi's attack strategy | linguistic / chain / fabrication | Linguistic: مولی ≠ اولی بتصرف |

### 2.2 The Author's Response (جواب / اقول)

The container unit for the refutation. Always introduced by **اقول** ("I say") with a pious invocation.

| Field | Description |
|-------|-------------|
| Opening formula | اقول مستعینا بلطف اللطیف الخبیر |
| Target claim | Which opponent's claim this responds to |
| Response approach | SANAD / DALALAH / BIOGRAPHICAL / CONTRADICTION / LINGUISTIC |
| Conclusion | Always explicit — the claim is مخدوش (flawed) or باطل (void) |

### 2.3 The Numbered Argument (وجه / دلیل)

Granular counter-points within a response, marked by ordinal numbers.

| Field | Description | Example |
|-------|-------------|---------|
| Number | Ordinal position | اول، دوم، سوم |
| Argument text | The specific counter-point | اول: غلط در این استدلال آن است که اهل عربیت قاطبة انکار کرده اند... |
| Evidence type | Linguistic / textual / logical / historical | Linguistic |
| Sources cited | Books and scholars referenced | — |

### 2.4 The Biographical Dossier (ترجمه)

The book's most distinctive structural feature. A compiled evaluation of a scholar from multiple Sunni rijal sources.

**Heading pattern:** « ترجمة [Scholar] از [Rijal Book] »

**Internal structure:**

**Example: Dossier on al-Waqidi (from Vol 3, pp. 10-24)**

*Identity:*

| Field | Value |
|-------|-------|
| Name | Muhammad ibn Umar ibn Waqid al-Aslami |
| Kunya | Abu Abdullah |
| Born | 130 AH |
| Died | 207 AH |
| Role | Historian, Qadi of Baghdad |
| Teachers | Ibn Jurayh, Ibn 'Ajlan, Ma'mar, Thawr ibn Yazid, Malik... |
| Students | al-Shafi'i, Abu 'Ubayd, Ibn Sa'd (his scribe)... |

*Negative evaluations (from Source 1: Mizan al-I'tidal):*

| Evaluator | Judgment | Arabic |
|-----------|---------|--------|
| Ahmad ibn Hanbal | He is a liar | هو کذاب |
| Ibn Ma'in | Not trustworthy | لیس بثقة |
| al-Bukhari | Abandoned | متروک |
| Abu Hatim | Fabricates hadith | یضع الحدیث |

*Positive evaluations (from the same source):*

| Evaluator | Judgment | Arabic |
|-----------|---------|--------|
| Mus'ab | Trustworthy, reliable | ثقة مأمون |
| Yazid ibn Harun | al-Waqidi is trustworthy | الواقدی ثقة |
| al-Darawardi | Commander of the Faithful in Hadith! | أمیر المؤمنین فی الحدیث |

*Additional sources consulted:* Tahdhib al-Tahdhib, al-'Ibar, al-Kashif, al-Ansab, Wafayat al-A'yan

*Author's conclusion (in Farsi):* "From this it is clear that the opponent contradicts his own authorities" — introduced by the formula: از این عبارت ظاهر است که...

**Dossier types observed:**

| Type | Description | When Used |
|------|------------|-----------|
| Full biographical | Name, dates, teachers, students, extensive evaluations | Major narrators under dispute |
| Brief evaluation | Just 1-2 quotes | Supplementary evidence |
| Comparative | Contrasts what different authorities say | When there's genuine disagreement |
| Polemical | Shows opponent's own authorities contradict the opponent | The signature move of Abaqat |

**Evaluation vocabulary (controlled terms):**

| Category | Terms |
|----------|-------|
| Positive (تعدیل) | ثقة، مأمون، صدوق، امام، علامة، حافظ، أمیر المؤمنین فی الحدیث، صالح الحدیث |
| Negative (جرح) | متروک، کذاب، یضع الحدیث، ضعیف، لیس بثقة، لا یکتب حدیثه، البلاء منه، دجال من الدجاجلة |
| Formulaic introductions | قال [Name]:... / وقال [Name]:... / سمعت [Name] یقول:... / سألت [Name] عن [Name] فقال:... |

### 2.5 The Argument Lineage (سلسلة الاستدلال)

Tracing who originated a claim and who copied it across centuries. This is **not our inference** — it is an explicit, named, recurring structural feature of the book. The author uses specific vocabulary to mark copying relationships.

**The author's vocabulary for argument lineage:**

| Farsi Term | Meaning | How It's Used |
|-----------|---------|---------------|
| مقلدین (muqallidin) | Imitators / blind followers | Labels the entire chain as a group |
| بتقلید (bi-taqlid) | By imitation of | Marks the specific copying relationship between two scholars |
| تقلیدا (taqlidan) | As imitation (adverb) | "They did this by imitation, not independent analysis" |
| اسلاف (aslaf) | Predecessors | "Following predecessors" — marks generational copying |

**Empirical evidence from the raw text (verbatim):**

**Evidence 1 — Section heading in Vol 6 (raw_text/vol_6.txt, line 37):**

> مقلدین رازی تقلیدا در حدیث غدیر و تواتر آن قدح کرده اند

"The **imitators of al-Razi** have criticized Hadith al-Ghadir and its tawatur **by imitation**"

This is an actual heading in the text — not a marginal note. The author names the phenomenon and makes it a structural unit of his argument.

**Evidence 2 — Explicit copying attribution in Vol 5 (raw_text/vol_5.txt, line 4040):**

> و قوشجی **بتقلید تفتازانی** در «شرح تجرید» در جواب این احتجاج می گوید

"And Qushji, **by imitation of Taftazani**, in Sharh al-Tajrid, says in response to this proof..."

The author explicitly marks that Qushji copied from Taftazani — this is not an inference, it is a factual attribution in the text.

**Evidence 3 — Tracing the chain to Shah Sahib in Vol 10 (raw_text/vol_10.txt, line 7087):**

> شاهصاحب **بتقلید اسلاف متعصبین** و اتباع وساوس جاحدین گرفتار شده، از تتبع آثار و تفحص اخبار و لحاظ قرائن و تأمل شواهد اعراض فرموده

"Shah Sahib, **by imitation of his bigoted predecessors** and following the whisperings of deniers, has been ensnared — he has abandoned the investigation of reports, the examination of traditions, the consideration of evidence, and the contemplation of proofs"

This is the author's most damning indictment: the Tuhfat author didn't do original research but simply copied.

**Evidence 4 — Tracking a secondary copying chain in Vol 10 (raw_text/vol_10.txt, line 7496):**

> ابن حجر در «صواعق» ذکر نموده، و برزنجی، و شیخ عبد الحق، و صاحب «مرافض» و امثالشان **بتقلید حجری** آن را پسندیدند

"Ibn Hajar mentioned it in al-Sawa'iq, and Barzanji, and Shaykh Abd al-Haqq, and the author of Marafi', and their like, **by imitation of Ibn Hajar**, adopted it"

Here the author traces a *second* copying chain — not from Razi but from Ibn Hajar. This shows he tracks multiple lineages.

**Evidence 5 — Labeling Razi's followers as a group in Vol 10 (raw_text/vol_10.txt, line 6957):**

> فخر رازی و **بعض مقلدین او** را چندان عصبیت و ناحق کوشی سراسیمه و بیخود ساخته

"Fakhr al-Razi and **some of his imitators** — their bigotry and pursuit of falsehood has made them frantic and senseless"

**Evidence 6 — The full chain from Vol 6 (raw_text/vol_6.txt, lines 54-79):**

In this passage the author **quotes six scholars sequentially**, each repeating the same objection to Hadith al-Ghadir, explicitly showing the chain of imitation:

1. Isfahani in Tashyid al-Qawa'id (line 55-57)
2. Iji in al-Mawaqif (line 65)
3. Taftazani in Sharh al-Maqasid (line 67)
4. Jurjani in Sharh al-Mawaqif (line 68-70)
5. Qushji in Sharh al-Tajrid (line 79)
6. Each quote is near-identical — proving the copying

The reconstructed chain from these passages:

```
Originator: Fakhr al-Razi (d. 606 AH) in Nihayat al-'Uqul
    ↓ copied by
Isfahani (d. 749 AH) in Tashyid al-Qawa'id
    "هذا الحدیث من باب الآحاد فلا یکون حجة فی هذا الباب"
    ↓ copied by
Iji (d. 756 AH) in al-Mawaqif, vol.3 p.272
    "الجواب منع صحة الحدیث و دعوی الضرورة مکابرة"
    ↓ copied by
Taftazani (d. 793 AH) in Sharh al-Maqasid, p.290
    "الجواب منع تواتر الخبر فان ذلک من مکابرات الشیعة"
    ↓ copied by
Jurjani (d. 816 AH) in Sharh al-Mawaqif
    "الجواب منع صحة الحدیث و دعوی الضرورة... مکابرة"
    ↓ copied by
Qushji (d. 879 AH) in Sharh al-Tajrid
    ↓ incorporated into
Shah Sahib (d. 1239 AH) in Tuhfat al-Ithna Ashariyya
```

Note how the Arabic quotations from each scholar are nearly identical — the same words repeated across 600 years. This is the author's point: the objection was never independently re-examined; it was mechanically transmitted.

**The argumentative purpose** of tracing lineage is to discredit the objection as unoriginal — showing it has no independent scholarly weight but is simply one person's mistake (Razi's) echoed by imitators across centuries. The author explicitly states this strategy.

### 2.6 The Rebuttal Lineage (سلسلة الجواب)

Citing prior Shia scholars who already answered the same claim. Like the argument lineage, this is explicit in the text — the author names his predecessors and shows how their work relates to his.

**Empirical evidence from Vol 3 (raw_text/vol_3.txt, lines 1048-1050):**

> و اکثر این مطاعن همان مطاعن است که جناب **شاهصاحب** آن را مع زیادة یسیرة بجواب دلیل ششم از دلائل عقلیه نقلا **عن النواصب** وارد فرموده اند

"Most of these criticisms are the same ones that **Shah Sahib** has cited, with minor additions, in response to the sixth rational proof, **quoting from the Nawasib**"

The author then traces who already answered, naming each predecessor:

**Evidence — Vol 3, line 1048-1050 (the rebuttal chain):**

> جناب **شیخ مفید** قدّس اللّه نفسه الزکیة... **جواب آن بابلغ وجوه و احسن طرق نوشته است**

"**Shaykh al-Mufid** — may God sanctify his pure soul — **wrote the response in the most eloquent manner and finest methods**"

> جناب **سید مرتضی** رضی الله عنه و ارضاه در کتاب «**فصول**» که آن را **از کتاب المجالس جناب شیخ مفید و از کتاب العیون و المحاسن آن جناب تلخیص کرده**

"**Sayyid al-Murtada** in his book **Fusul**, which he **condensed from Shaykh al-Mufid's al-Majalis and from his al-'Uyun wa al-Mahasin**"

The author explicitly states that Sayyid al-Murtada's work is a condensation of al-Mufid's — showing intellectual genealogy on the rebuttal side.

**Evidence — Vol 3, line 1416 (independent rebuttal):**

> **پاسخ شافی اسکافی از هذیانات جاحظ**

"**al-Iskafi's comprehensive response to al-Jahiz's ravings**"

This is an actual heading in the text — marking a separate prior rebuttal tradition.

**The reconstructed rebuttal chain:**

| Order | Scholar | Died | Work | Relationship |
|-------|---------|------|------|-------------|
| 1 | Shaykh al-Mufid | 413 AH | al-Majalis; al-'Uyun wa al-Mahasin | First to refute |
| 2 | Sayyid al-Murtada | 436 AH | Fusul | Condensed from al-Mufid |
| 3 | al-Iskafi | — | — | Independent response |
| 4 | Allamah al-Hilli | 726 AH | Nahj al-Haqq wa Kashf al-Sidq | Independent response |
| 5 | **Author (Mir Hamid Husain)** | 1306 AH | Abaqat al-Anwar | Builds on all + adds new Sunni evidence and biographical dossiers |

**The argumentative purpose** of the rebuttal lineage is the mirror image of the argument lineage: while the argument lineage discredits the opponents as mere imitators, the rebuttal lineage shows the Shia scholarly tradition has a deep, independent, multi-generational response — and the author's contribution is the latest and most comprehensive layer.

### 2.7 The Citation (استناد)

A reference to a source book with volume/page. Each citation has a **direction**:

| Direction | Meaning | Example |
|-----------|---------|---------|
| EVIDENCE_FOR | Author cites this source to support his position | Mizan al-I'tidal proving narrator is weak |
| EVIDENCE_AGAINST | The opponent relies on this source | Razi's Nihayat al-'Uqul |
| CROSS_REFERENCE | Neutral scholarly reference within a dossier | Wafayat al-A'yan for death date |
| SOURCE_REFUTED | The Tuhfat passage being refuted | Tuhfat p.XXX |

---

## 3. The Recurring Argument Flow

Every refutation in Abaqat follows a consistent six-step pattern:

| Step | Action | Marker in Text | Language |
|------|--------|---------------|----------|
| 1 | **State opponent's claim** — quote Dehlavi verbatim | قال الفاضل المحدث التحرير: | Farsi or Arabic |
| 2 | **Declare it false** — announce the response | اقول مستعینا بلطف اللطیف الخبیر | Arabic formula |
| 3 | **Cite Sunni primary sources** — hadith texts proving the point | Direct Arabic quotes with book/page | Arabic |
| 4 | **Build biographical dossiers** — stack 5-20 rijal sources proving chain reliability | « ترجمة [narrator] از [rijal book] » | Arabic quotes + Farsi synthesis |
| 5 | **Expose contradictions** — show the opponent relies on the same sources elsewhere | Farsi argumentation | Farsi |
| 6 | **Conclude** — extract the verdict | از این عبارت ظاهر است که... [مخدوش / باطل] | Farsi |

**Transition markers:**
- ونیز — "And also" (adding supplementary evidence)
- بالجمله — "In summary" (wrapping up a point)
- از این عبارت ظاهر است که — "From this statement it is clear that" (extracting the conclusion)
- کما سبق آنفاً — "As previously mentioned" (internal cross-reference)

**Language pattern:** The text is a **Farsi matrix embedding Arabic data blocks**. Every Arabic quotation is followed by a Farsi exegesis. The opponent's words are in Farsi (from Tuhfat) or Arabic (from Sawa'iq). Sunni source quotes are always Arabic. The author's voice is always Farsi.

---

## 4. How the Dimensions Connect

| Tuhfat (What Dehlavi Claims) | Abaqat (How the Author Responds) |
|------------------------------|----------------------------------|
| **Linguistic attack:** "Mawla doesn't mean authority" | **Numbered arguments** (اول، دوم، سوم) with counter-evidence from Arabic lexicons and Quran |
| **Chain attack:** "Bukhari didn't narrate it" | **Biographical dossiers** stacking 5-20 rijal sources proving the narrators are reliable by Sunni standards |
| **Argument lineage:** Razi's claim copied by Iji, Taftazani, Jurjani, Qushji, then Dehlavi | **Contradiction exposure:** "The opponents THEMSELVES rely on al-Waqidi elsewhere" |
| **No prior rebuttals cited** by Dehlavi | **Rebuttal lineage:** al-Mufid, Sayyid al-Murtada, al-Iskafi, al-Hilli all answered before the author |
| **Authenticity attack:** "This hadith is fabricated" | **Counter-citation:** Quoting the same hadith from the opponent's own most trusted books |

---

## 5. Scale of the Data (What We've Measured)

### From the Tuhfat (the opponent's side)

| Metric | Count | Source |
|--------|-------|--------|
| Quranic verses refuted | 7 | Gemini analysis of Chapter 7 |
| Hadiths refuted | 12 | Gemini analysis of Chapter 7 |
| Rational arguments | 6 | Gemini analysis of Chapter 7 |
| Scholars Dehlavi cites | 59 | Gemini extraction |
| Books Dehlavi references | 32 | Gemini extraction |

### From the Abaqat (the author's side)

| Metric | Count | Source |
|--------|-------|--------|
| Volumes analyzed | 23 | Gemini analysis of all volumes |
| Total responses to Dehlavi | 67 | Mapped to specific claims |
| Biographical dossiers | 114 | Across all 23 volumes |
| Explicit ترجمه headings (vols 2-10) | 155 | Regex count on raw text |
| اشاره markers (vols 2-10) | 171 | Regex count on raw text |
| Unique scholars mentioned | 297 | Gemini extraction |
| Unique books cited | 289 | Gemini extraction |
| Jarh/ta'dil evaluation terms (vols 2-6) | 363 | Regex count on raw text |

### Hadith-to-Volume Mapping (verified)

| Hadith | Volumes | Section |
|--------|---------|---------|
| Ghadir | 1-3, 5-10 | Sanad + Dalalat |
| Twelve Caliphs | 4 | Dalalat |
| Manzila | 11 | Sanad + Dalalat |
| Wilayah | 12 | Sanad |
| Tayr (Bird) | 13 | Sanad + Dalalat |
| Madinat al-Ilm | 14-15 | Sanad + Dalalat |
| Tashbih (Resemblance) | 16 | Sanad + Dalalat |
| Nur (Light) | 17 | Sanad |
| Thaqalayn | 18-22 | Sanad + Dalalat |
| Safinah | 23 | Sanad + Dalalat |

---

## 6. Proposed Entity Relationship

### Entities and Their Relationships

| Entity | Arabic | Fields | Links To |
|--------|--------|--------|----------|
| **Defended Hadith** | حدیث | Name, Arabic text, volumes | Tuhfat Claims |
| **Tuhfat Claim** | ادعای تحفه | Verbatim text, page in Tuhfat, attack type (linguistic/chain/fabrication) | Defended Hadith, Author's Response |
| **Author's Response** | جواب | Opening formula, approach type, conclusion | Tuhfat Claim, contains: Numbered Args + Dossiers + Citations |
| **Numbered Argument** | وجه / دلیل | Ordinal number, argument text, evidence type | Parent Response |
| **Biographical Dossier** | ترجمه | Heading text, argumentative purpose | Subject Scholar, Authority Scholar, Source Book, Evaluations |
| **Rijal Evaluation** | جرح / تعدیل | Evaluator name, term, category (+/-), verbatim Arabic quote, source reference | Dossier, Evaluator Scholar, Source Book |
| **Scholar** | عالم / راوی | Name (Arabic, Farsi, English), kunya, nisba, birth, death, role | Teachers, Students, Argument Lineage, Rebuttal Lineage |
| **Source Book** | کتاب | Name (Arabic, English), author, type (rijal/hadith/tafsir/tarikh/kalam) | Author Scholar |
| **Citation** | استناد | Book, volume, page, direction (for/against/cross-ref/refuted) | Source Book, Response or Dossier |
| **Argument Lineage** | سلسلة الاستدلال | The claim being traced, ordered chain of scholars who made/copied it | Scholars, Tuhfat Claim |
| **Rebuttal Lineage** | سلسلة الجواب | The claim being answered, ordered chain of prior scholars who refuted it | Scholars, Author's Response |

### How Entities Connect (Reading Top to Bottom)

**Level 1 — The Target:**
A *Defended Hadith* (e.g., Ghadir) is attacked by one or more *Tuhfat Claims*.

**Level 2 — The Response:**
Each *Tuhfat Claim* receives an *Author's Response*, which contains *Numbered Arguments*, *Biographical Dossiers*, and *Citations*.

**Level 3 — The Evidence:**
Each *Biographical Dossier* is about a *Scholar* (the subject), quotes from a *Source Book* via an *Authority Scholar*, and contains multiple *Rijal Evaluations* — each with a named evaluator, a jarh/ta'dil term, and a verbatim Arabic quote.

**Level 4 — The Genealogy:**
*Argument Lineages* trace which *Scholar* originated a claim and who copied it. *Rebuttal Lineages* trace which prior *Scholars* already answered the same claim, culminating in the author's own response.

---

## 7. Questions for the Scholar

Before finalizing this data model, we need expert input on:

1. **Completeness of the claim inventory**: We identified 7 Quranic verses, 12 hadiths, and 6 rational arguments from Dehlavi's Chapter 7. Is this complete? Are there claims we missed?

2. **Volume-to-hadith mapping accuracy**: Volume 4 was identified as covering the Hadith of the Twelve Caliphs rather than Ghadir — is this correct? Are there other mapping corrections needed?

3. **Dossier classification**: We identified 4 types of biographical dossiers (full, brief, comparative, polemical). Are there other types? Is this classification meaningful from a scholarly perspective?

4. **The "fulan" question**: Dehlavi claims Sharif al-Radi removed Abu Bakr's name from Nahj al-Balagha and replaced it with "fulan." He cites no specific Shia commentator and misidentifies the compiler as Sharif al-Murtada. How does the Abaqat address this specific claim? Is it a significant argument or a marginal one?

5. **The المنهج الأول**: The unpublished first Manhaj on Quranic proofs — does any manuscript exist? Has any scholar worked on it? Should our data model account for it as a future possibility?

6. **Evaluation terminology**: We extracted 8 positive and 9 negative rijal terms. Is this vocabulary complete for what appears in the Abaqat? Are there grading systems (like Ibn Abi Hatim's 4-tier scale) that the author follows?

7. **Cross-volume references**: Does the author of Abaqat cross-reference between volumes (e.g., "as I proved in the Ghadir volume")? If so, how systematically?

8. **The 12-hadith structure**: The author's own catalog (from Volume 11's introduction) lists 12 hadiths. But Gemini also found Safinah and Nujum in later volumes. Are these part of the original plan or later additions?

---

## 8. Source Files

| File | Content |
|------|---------|
| `docs/tuhfat-chapter7-imamate.txt` | Extracted raw text of Tuhfat Chapter 7 (3,826 lines) |
| `docs/tuhfat-chapter7-argument-map.json` | Gemini analysis of Dehlavi's claims (structured) |
| `docs/tuhfat-chapter7-argument-map.md` | Readable report of Dehlavi's argument structure |
| `docs/tuhfat-chapter7-analysis.md` | Manual + Gemini analysis with critical assessment |
| `docs/abaqat-methodology-analysis.json` | Gemini deep analysis of Abaqat's structural patterns |
| `docs/abaqat-dossier-patterns.json` | Gemini deep analysis of biographical dossier patterns |
| `docs/abaqat-responses/` | Per-volume response catalogs (23 JSON + 23 MD files) |
| `docs/abaqat-data-map.md` | 7-layer data map with examples |
| `docs/abaqat-data-map.pdf` | Print-ready PDF of the data map |
| `docs/data-models.md` | Full technical data model documentation |
| `AbaghaatAlanwaarfarsi/` | All 23 volumes as djvu-extracted text |
| `Full text of "تحفهء اثنى عشريه".html` | Complete Tuhfat text |
