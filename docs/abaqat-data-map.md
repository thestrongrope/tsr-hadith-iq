# Abaqat al-Anwar — Data Map

A structural map of the book's content dimensions, with real examples from the text.
For review by subject-matter experts before data model implementation.

---

## Overview: What This Book Is

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ABAQAT AL-ANWAR (عبقات الانوار)                  │
│                                                                     │
│  Author: Mir Hamid Husain Musavi (d. 1306 AH)                      │
│  Genre:  Polemical treatise (ردیه), NOT a hadith collection         │
│  Source: Point-by-point refutation of Tuhfat al-Ithna Ashariyya    │
│          by Shah Abdul Aziz al-Dihlawi (d. 1239 AH)               │
│  Scope:  23 volumes, Farsi commentary + Arabic quotations          │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CRITICAL: The entire 23-volume work responds to only ONE    │   │
│  │ chapter of the Tuhfat — Chapter 7 (الباب السابع في الإمامة),│   │
│  │ the chapter on Imamate. The Tuhfat itself has 12 chapters. │   │
│  │ Chapter 7 contains sub-sections called عقائد (doctrines),   │   │
│  │ e.g., "عقیده ششم از باب هفتم" (the 6th doctrine of Ch.7). │   │
│  │                                                            │   │
│  │ Furthermore, the 23 printed volumes are only the SECOND    │   │
│  │ of two Manaahij (approaches):                              │   │
│  │   المنهج الأول: Quranic proofs — STILL IN MANUSCRIPT       │   │
│  │   المنهج الثاني: Hadith proofs — the 23 printed volumes    │   │
│  │                                                            │   │
│  │ A single chapter of the Tuhfat required (at minimum)       │   │
│  │ 23 volumes of hadith-based refutation alone.               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Three unique contributions:                                        │
│    1. Argumentative: systematic refutation with discourse genealogy │
│    2. Biographical:  meta-rijal encyclopedia from Sunni sources     │
│    3. Bibliographical: cross-referencing 244+ books with precision  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: DEFENDED HADITHS (Volume-Level Organization)

Each volume or group of volumes defends one specific hadith.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 1: DEFENDED HADITHS                                          ║
║  (The 10 hadiths the entire book is organized around)               ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Ghadir (حدیث غدیر)                           │        ║
║  │ Volumes: 1-10                                           │        ║
║  │ "من کنت مولاه فعلی مولاه"                               │        ║
║  │ Vols 1-5: Sanad (chain of transmission)                 │        ║
║  │ Vol 6-10: Dalalat (meaning/implications)                │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Manzila (حدیث منزلت)          │ Vol 11       │        ║
║  │ "انت منی بمنزلة هارون من موسی"                          │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Wilayah (حدیث ولایت)          │ Vol 12       │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Tayr (حدیث طیر)               │ Vol 13       │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith Madinat al-Ilm (حدیث مدینة العلم) │ Vols 14-15  │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Tashbih (حدیث تشبیه)           │ Vol 16       │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Nur (حدیث نور)                 │ Vol 17       │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Thaqalayn (حدیث ثقلین)         │ Vols 18-22  │        ║
║  │ "انی تارک فیکم الثقلین کتاب الله و عترتی"              │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ Hadith al-Safinah (حدیث سفینه)           │ Vol 23       │        ║
║  │ "مثل اهل بیتی کمثل سفینة نوح"                          │        ║
║  └─────────────────────────────────────────────────────────┘        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Layer 2: MICRO-CLAIMS FROM THE TUHFAT (The Organizing Spine)

Within each hadith section, the Tuhfat raises dozens to hundreds of
specific micro-arguments. The author addresses EACH one.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 2: TUHFAT MICRO-CLAIMS (The Organizing Spine)               ║
║  (The specific objections the author is responding to)              ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  The Tuhfat al-Ithna Ashariyya is a multi-chapter work.            ║
║  Abaqat al-Anwar responds to only ONE chapter — the chapter        ║
║  on hadith-based proofs for Imamate (the chapter dealing with      ║
║  hadiths that establish the succession of Ali ibn Abi Talib).       ║
║                                                                     ║
║  Within that single chapter, the Tuhfat raises objections          ║
║  against each key hadith. These are the micro-claims that          ║
║  the author systematically dismantles across 23 volumes.           ║
║                                                                     ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ TUHFAT AL-ITHNA ASHARIYYA (التحفة الإثني عشرية)          │      ║
║  │ (Source: Arabic Wikipedia, confirmed by raw text refs)    │      ║
║  │                                                           │      ║
║  │  باب 1:  في تاريخ الشيعة وفرقها  (History & sects)       │      ║
║  │  باب 2:  في مكائدها  (Stratagems)                         │      ║
║  │  باب 3:  في أسلافها وكتبها  (Predecessors & books)       │      ║
║  │  باب 4:  في رواة الشيعة وأخبارها  (Narrators & reports)  │      ║
║  │  باب 5:  في الإلهيات  (Theology)                          │      ║
║  │  باب 6:  في النبوات  (Prophethood)                        │      ║
║  │  باب 7:  في الإمامة  (ON IMAMATE) ◄──────────────────── │      ║
║  │          ▲                                                │      ║
║  │          │  ALL 23 VOLUMES OF ABAQAT                      │      ║
║  │          │  RESPOND TO THIS ONE CHAPTER                   │      ║
║  │          │  (and only the hadith proofs —                  │      ║
║  │          │   Manhaj al-Thani)                              │      ║
║  │          │                                                │      ║
║  │          ├── عقیده 1 (Doctrine 1)                         │      ║
║  │          ├── عقیده 2 (Doctrine 2)                         │      ║
║  │          ├── ...                                          │      ║
║  │          ├── عقیده 6 (Doctrine 6) — ref'd in vol 5       │      ║
║  │          └── ...                                          │      ║
║  │  باب 8:  في المعاد  (Resurrection)                        │      ║
║  │  باب 9:  في المسائل الفقهية  (Jurisprudence)             │      ║
║  │  باب 10: في المطاعن  (Criticisms/Attacks)                │      ║
║  │  باب 11: في الخواص الثلاث  (Delusions, biases, errors)   │      ║
║  │  باب 12: في الولاء والبراء  (Allegiance & dissociation)  │      ║
║  └───────────────────────────────────────────────────────────┘      ║
║                                                                     ║
║  Under "Hadith al-Ghadir — Sanad" (Vols 1-5):                      ║
║                                                                     ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ CLAIM A: "This hadith is not mutawatir (mass-transmitted)"│      ║
║  │ Source: Tuhfat, p.33                                      │      ║
║  │ Original claimant: Fakhr al-Din al-Razi                   │      ║
║  └───────────────────────────────────────────────────────────┘      ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ CLAIM B: "al-Bukhari and Muslim didn't narrate it,        │      ║
║  │           so it cannot be sahih"                           │      ║
║  │ Source: Tuhfat                                            │      ║
║  │ Original claimant: Fakhr al-Din al-Razi                   │      ║
║  └───────────────────────────────────────────────────────────┘      ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ CLAIM C: "al-Waqidi didn't report it, which discredits    │      ║
║  │           the hadith"                                     │      ║
║  │ Source: Tuhfat / Razi's Nihayat al-'Uqul                 │      ║
║  └───────────────────────────────────────────────────────────┘      ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ CLAIM D: "Abu Dawud and Abu Hatim al-Razi criticized      │      ║
║  │           this hadith's authenticity"                      │      ║
║  │ Source: Tuhfat / Razi → Isfahani → Iji → Taftazani       │      ║
║  └───────────────────────────────────────────────────────────┘      ║
║                                                                     ║
║  Under "Hadith al-Ghadir — Dalalat" (Vols 6-10):                   ║
║                                                                     ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ CLAIM E: "The word 'mawla' means friend/helper,           │      ║
║  │           not leader/authority"                            │      ║
║  │ Source: Tuhfat / Razi / Taftazani                         │      ║
║  └───────────────────────────────────────────────────────────┘      ║
║  ┌───────────────────────────────────────────────────────────┐      ║
║  │ CLAIM F: ...                                              │      ║
║  │ (tens to hundreds more per hadith)                        │      ║
║  └───────────────────────────────────────────────────────────┘      ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Layer 3: ARGUMENT LINEAGE (Who Said It, Who Copied It)

For each micro-claim, the author traces the chain of scholars who
made or echoed the same argument across centuries.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 3: ARGUMENT LINEAGE                                         ║
║  (Tracking how a claim propagated through imitation)                ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  Example: CLAIM D — "Abu Dawud and Abu Hatim criticized Ghadir"     ║
║  (from Vol 6, pp. 4-7)                                             ║
║                                                                     ║
║     ┌──────────────────────────────────────┐                        ║
║     │ ORIGINATOR                           │                        ║
║     │ Fakhr al-Razi (فخر رازی)             │                        ║
║     │ d. 606 AH                            │                        ║
║     │ in: Nihayat al-'Uqul (نهایة العقول)  │                        ║
║     └──────────────┬───────────────────────┘                        ║
║                    │ copied by                                      ║
║     ┌──────────────▼───────────────────────┐                        ║
║     │ Isfahani (اصفهانی)                   │                        ║
║     │ d. 749 AH                            │                        ║
║     │ in: Tashyid al-Qawa'id               │                        ║
║     │     (تشیید القواعد شرح تجرید العقائد) │                        ║
║     │ Quote: "هذا الحدیث من باب الآحاد      │                        ║
║     │  فلا یکون حجة فی هذا الباب"           │                        ║
║     └──────────────┬───────────────────────┘                        ║
║                    │ copied by                                      ║
║     ┌──────────────▼───────────────────────┐                        ║
║     │ Iji (ایجی) — d. 756 AH              │                        ║
║     │ in: al-Mawaqif (المواقف) vol.3 p.272 │                        ║
║     │ Quote: "الجواب منع صحة الحدیث        │                        ║
║     │  و دعوی الضرورة مکابرة"              │                        ║
║     └──────────────┬───────────────────────┘                        ║
║                    │ copied by                                      ║
║     ┌──────────────▼───────────────────────┐                        ║
║     │ Taftazani (تفتازانی) — d. 793 AH     │                        ║
║     │ in: Sharh al-Maqasid (شرح مقاصد)     │                        ║
║     │     p. 290                            │                        ║
║     │ Quote: "الجواب منع تواتر الخبر       │                        ║
║     │  فان ذلک من مکابرات الشیعة"          │                        ║
║     └──────────────┬───────────────────────┘                        ║
║                    │ copied by                                      ║
║     ┌──────────────▼───────────────────────┐                        ║
║     │ Jurjani (جرجانی) — d. 816 AH         │                        ║
║     │ in: Sharh al-Mawaqif (شرح مواقف)     │                        ║
║     └──────────────┬───────────────────────┘                        ║
║                    │ copied by                                      ║
║     ┌──────────────▼───────────────────────┐                        ║
║     │ Qushji (قوشجی) — d. 879 AH           │                        ║
║     │ in: Sharh al-Tajrid (شرح تجرید)      │                        ║
║     └──────────────┬───────────────────────┘                        ║
║                    │ incorporated into                              ║
║     ┌──────────────▼───────────────────────┐                        ║
║     │ Shah Sahib / al-Dihlawi (شاه صاحب)   │                        ║
║     │ d. 1239 AH                           │                        ║
║     │ in: Tuhfat al-Ithna Ashariyya        │                        ║
║     │     (التحفة الاثنی عشریة)             │                        ║
║     └──────────────────────────────────────┘                        ║
║                                                                     ║
║  Author's observation (Vol 6, p.4):                                 ║
║  "مقلدین رازی تقلیدا در حدیث غدیر و تواتر آن قدح کرده اند"        ║
║  "The imitators of al-Razi have criticized Hadith al-Ghadir's       ║
║   tawatur by imitation [not independent analysis]"                  ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Layer 4: REBUTTAL LINEAGE (Who Already Answered This)

Before giving his own refutation, the author cites prior scholars
who already responded to the same or similar claims.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 4: REBUTTAL LINEAGE                                         ║
║  (Prior scholars who already refuted this claim)                    ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  Example: Responding to al-Jahiz's attacks on Imam Ali (a.s.)       ║
║  (from Vol 3, pp. 89-131)                                          ║
║                                                                     ║
║  The author notes (Vol 3, p.89):                                    ║
║  "Most of these criticisms are the same ones that Shah Sahib        ║
║   cited in the Tuhfat, quoting from the Nawasib"                   ║
║                                                                     ║
║     ┌──────────────────────────────────────────┐                    ║
║     │ PRIOR REBUTTAL 1                         │                    ║
║     │ Shaykh al-Mufid (شیخ مفید)               │                    ║
║     │ d. 413 AH                                │                    ║
║     │ in: al-Majalis (المجالس)                  │                    ║
║     │     al-'Uyun wa al-Mahasin               │                    ║
║     │     (العیون و المحاسن)                     │                    ║
║     │ "جواب آن بابلغ وجوه و احسن طرق نوشته"    │                    ║
║     │ "Wrote the response in the most eloquent  │                    ║
║     │  manner and finest methods"               │                    ║
║     └──────────────┬───────────────────────────┘                    ║
║                    │ summarized by                                   ║
║     ┌──────────────▼───────────────────────────┐                    ║
║     │ PRIOR REBUTTAL 2                         │                    ║
║     │ Sayyid al-Murtada (سید مرتضی)            │                    ║
║     │ d. 436 AH                                │                    ║
║     │ in: Fusul (فصول)                          │                    ║
║     │ "که آن را از کتاب المجالس جناب شیخ مفید  │                    ║
║     │  و از کتاب العیون و المحاسن آن جناب       │                    ║
║     │  تلخیص کرده"                              │                    ║
║     │ "Which he condensed from Shaykh           │                    ║
║     │  al-Mufid's al-Majalis and al-'Uyun"     │                    ║
║     └──────────────────────────────────────────┘                    ║
║     ┌──────────────────────────────────────────┐                    ║
║     │ PRIOR REBUTTAL 3                         │                    ║
║     │ al-Iskafi (اسکافی)                        │                    ║
║     │ "پاسخ شافی اسکافی از هذیانات جاحظ"       │                    ║
║     │ "al-Iskafi's comprehensive response       │                    ║
║     │  to al-Jahiz's ravings"                   │                    ║
║     └──────────────────────────────────────────┘                    ║
║     ┌──────────────────────────────────────────┐                    ║
║     │ PRIOR REBUTTAL 4                         │                    ║
║     │ Allamah al-Hilli (علامه حلی)              │                    ║
║     │ d. 726 AH                                │                    ║
║     │ in: Nahj al-Haqq (نهج الحق و کشف الصدق)  │                    ║
║     └──────────────────────────────────────────┘                    ║
║                    │                                                ║
║                    ▼                                                ║
║     ┌──────────────────────────────────────────┐                    ║
║     │ AUTHOR'S OWN REBUTTAL                    │                    ║
║     │ Mir Hamid Husain (مؤلف)                   │                    ║
║     │ Builds on all prior rebuttals + adds:    │                    ║
║     │  • New Sunni source evidence             │                    ║
║     │  • Biographical dossiers                 │                    ║
║     │  • Contradiction analysis                │                    ║
║     │  • Linguistic analysis                   │                    ║
║     └──────────────────────────────────────────┘                    ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Layer 5: THE AUTHOR'S REFUTATION (Multi-Pronged Response)

The author's own response to each claim uses multiple tools.
"اشاره" (remark) markers divide the refutation into atomic logical points.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 5: AUTHOR'S REFUTATION STRUCTURE                            ║
║  (How each claim is systematically dismantled)                      ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  Example: Refuting CLAIM C — "al-Waqidi didn't report Ghadir"       ║
║  (from Vol 3, pp. 9-30)                                            ║
║                                                                     ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ اشاره (Remark 1): Expose the contradiction              │        ║
║  │                                                         │        ║
║  │ "عجب که شاه صاحب و ابن روزبهان و رازی                   │        ║
║  │  خود بروایت واقدی احتجاج می کنند"                       │        ║
║  │                                                         │        ║
║  │ The opponents THEMSELVES rely on al-Waqidi               │        ║
║  │ when it suits them (in Mataʿin of Uthman),              │        ║
║  │ but reject him here                                     │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ اشاره (Remark 2): Positive evaluations of al-Waqidi     │        ║
║  │                                                         │        ║
║  │ "مدایح واقدی در کتب اهل سنت"                            │        ║
║  │ "Praises of al-Waqidi in Sunni books"                   │        ║
║  │                                                         │        ║
║  │   → Triggers BIOGRAPHICAL DOSSIER (see Layer 6)         │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ اشاره (Remark 3): Negative evaluations acknowledged     │        ║
║  │                                                         │        ║
║  │ "معایب و مثالب واقدی در کتب اهل سنت"                    │        ║
║  │ "Faults of al-Waqidi in Sunni books"                    │        ║
║  │                                                         │        ║
║  │ Author presents BOTH sides, then shows the              │        ║
║  │ positive evaluations outweigh the negative              │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ اشاره (Remark 4): Logical conclusion                    │        ║
║  │                                                         │        ║
║  │ "عدم روایت واقدی حدیث غدیر را قادح آن نیست"             │        ║
║  │ "al-Waqidi's non-reporting of Ghadir does NOT           │        ║
║  │  discredit the hadith"                                  │        ║
║  │                                                         │        ║
║  │ Because: even the opponents don't consider              │        ║
║  │ al-Waqidi's silence a proof of weakness                 │        ║
║  │ in other contexts                                       │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║                                                                     ║
║  171 "اشاره" markers across 8 volumes (vols 2-10)                   ║
║  These are the ATOMIC UNITS of argumentation                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Layer 6: BIOGRAPHICAL DOSSIERS (The Rijal Dimension)

When the argument requires establishing a scholar's credibility or
lack thereof, the author builds a comprehensive dossier by cross-
referencing what MULTIPLE Sunni rijal authorities say about that person.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 6: BIOGRAPHICAL DOSSIERS (تراجم)                             ║
║  (Cross-referenced scholar evaluations — 195+ across all volumes)   ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  Example: DOSSIER ON AL-WAQIDI (واقدی)                              ║
║  (from Vol 3, pp. 10-24, serving Remark 2 above)                   ║
║                                                                     ║
║  Subject: Muhammad ibn Umar al-Waqidi (محمد بن عمر الواقدی)         ║
║  Born: 130 AH  │  Died: 207 AH  │  Role: Historian, Qadi of Baghdad║
║                                                                     ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │ SOURCE 1: Mizan al-I'tidal (میزان الاعتدال فی نقد الرجال)  │    ║
║  │ Authority: al-Dhahabi (ذهبی)                                │    ║
║  │ Heading: "ترجمه واقدی در کتاب میزان الاعتدال"               │    ║
║  │                                                             │    ║
║  │ Evaluations quoted within:                                  │    ║
║  │   Ahmad ibn Hanbal: "هو کذاب" (he is a liar)               │    ║
║  │   Ibn Ma'in: "لیس بثقة" (not trustworthy)                  │    ║
║  │   al-Bukhari: "متروک" (abandoned)                           │    ║
║  │   Abu Hatim: "یضع الحدیث" (fabricates hadith)               │    ║
║  │   al-Daraqutni: "فیه ضعیف" (there is weakness in him)      │    ║
║  │   BUT ALSO:                                                 │    ║
║  │   Mus'ab: "ثقة مأمون" (trustworthy, reliable)              │    ║
║  │   Yazid ibn Harun: "الواقدی ثقة" (al-Waqidi is trustworthy)│    ║
║  │   al-Darawardi: "أمیر المؤمنین فی الحدیث"                  │    ║
║  │                  (Commander of the Faithful in Hadith!)      │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │ SOURCE 2: Tahdhib al-Tahdhib (تذهیب التهذیب)                │    ║
║  │ Authority: al-Dhahabi (ذهبی)                                │    ║
║  │ Heading: "ترجمه واقدی در کتاب تذهیب التهذیب"                │    ║
║  │                                                             │    ║
║  │ Contains: full isnad chain (teachers & students)            │    ║
║  │   Teachers: Ibn 'Ajlan, Thawr ibn Yazid, Ibn Jurayh,      │    ║
║  │             Malik, Ibn Abi Dhi'b, and many others          │    ║
║  │   Students: al-Shafi'i, Abu 'Ubayd, Ibn Sa'd (his scribe) │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │ SOURCE 3: al-'Ibar (عبر فی خبر من غبر)                     │    ║
║  │ Authority: al-Dhahabi (ذهبی)                                │    ║
║  │ Heading: "ترجمه واقدی بگفتار ذهبی در عبر فی خبر من غبر"    │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │ SOURCE 4: al-Kashif (الکاشف)                                │    ║
║  │ Authority: al-Dhahabi (ذهبی)                                │    ║
║  │ Heading: "ترجمه واقدی بگفتار ذهبی در کاشف"                  │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │ SOURCE 5: al-Ansab (الانساب)                                │    ║
║  │ Authority: al-Sam'ani (سمعانی)                               │    ║
║  │ Heading: "ترجمه واقدی بگفتار سمعانی در انساب"               │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │ SOURCE 6: Wafayat al-A'yan (وفیات الأعیان)                  │    ║
║  │ Authority: Ibn Khallikan (ابن خلکان)                        │    ║
║  │ Heading: "ترجمه واقدی بگفتار ابن خلکان در وفیات الأعیان"   │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                                                                     ║
║  Author's conclusion: The same Sunni authorities who praise         ║
║  al-Waqidi as "امیر المؤمنین فی الحدیث" elsewhere cannot           ║
║  dismiss his testimony when it comes to Ghadir.                     ║
║                                                                     ║
║  ─────────────────────────────────────────────────────              ║
║  Scale across the book:                                             ║
║    195+ explicit biographical dossiers (ترجمه headings)             ║
║    ~70 unique scholars evaluated                                    ║
║    ~50 unique rijal books cross-referenced                          ║
║    ~35 unique evaluating authorities quoted                         ║
║    460+ individual jarh/ta'dil evaluation terms                     ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Layer 7: CITATIONS WITH DIRECTIONALITY

The same Sunni book can be cited in opposite directions depending
on the argumentative context.

```
╔═══════════════════════════════════════════════════════════════════════╗
║  LAYER 7: CITATION DIRECTIONALITY                                   ║
║  (The same source used FOR and AGAINST the author's position)       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  Example: Sahih al-Bukhari (صحیح البخاری)                           ║
║                                                                     ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ DIRECTION: OPPONENT RELIES ON IT                        │        ║
║  │                                                         │        ║
║  │ Claim: "al-Bukhari didn't narrate Hadith al-Ghadir,     │        ║
║  │        therefore it is not sahih"                        │        ║
║  │                                                         │        ║
║  │ The opponent uses Bukhari's SILENCE as evidence          │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║                                                                     ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ DIRECTION: AUTHOR USES IT AS EVIDENCE                   │        ║
║  │                                                         │        ║
║  │ The author shows that Bukhari HIMSELF has narrated       │        ║
║  │ other hadiths with the same chains, proving the          │        ║
║  │ narrators are reliable by Bukhari's own standards        │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║                                                                     ║
║  ┌─────────────────────────────────────────────────────────┐        ║
║  │ DIRECTION: AUTHOR CRITIQUES ITS METHODOLOGY             │        ║
║  │                                                         │        ║
║  │ The author shows internal contradictions in Bukhari      │        ║
║  │ (متناقض اخبار در صحیحین — contradictory reports in      │        ║
║  │ the two Sahihs), undermining the claim that              │        ║
║  │ Bukhari's non-inclusion equals inauthenticity            │        ║
║  └─────────────────────────────────────────────────────────┘        ║
║                                                                     ║
║  244 unique books cited across the entire work                      ║
║  14,907 individual citations with volume/page references            ║
║  Each citation has a DIRECTION that the current schema loses        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## How All Layers Connect (Complete Example)

One complete flow through all layers for a single micro-claim:

```
╔═══════════════════════════════════════════════════════════════════════╗
║  COMPLETE EXAMPLE: "al-Waqidi's non-narration discredits Ghadir"   ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  L1  DEFENDED HADITH: Hadith al-Ghadir (Vols 1-10, Sanad section) ║
║   │                                                                 ║
║   ▼                                                                 ║
║  L2  TUHFAT MICRO-CLAIM: "al-Waqidi didn't report Ghadir"          ║
║   │  Source: Razi's Nihayat al-'Uqul, adopted by Tuhfat            ║
║   │                                                                 ║
║   ▼                                                                 ║
║  L3  ARGUMENT LINEAGE (who made this claim):                       ║
║   │  Razi (d.606) → Taftazani (d.793) → Qushji (d.879)            ║
║   │  → Shah Sahib (d.1239)                                         ║
║   │  Plus: Ibn Ruzbehan (who attacked Tabari for                   ║
║   │  reporting the house-burning incident, using                    ║
║   │  al-Waqidi's non-narration as a weapon)                        ║
║   │                                                                 ║
║   ▼                                                                 ║
║  L4  REBUTTAL LINEAGE (who already answered):                      ║
║   │  Allamah al-Hilli in Nahj al-Haqq (first raised               ║
║   │  the counter-examples of Tuhfat relying on Waqidi)             ║
║   │                                                                 ║
║   ▼                                                                 ║
║  L5  AUTHOR'S REFUTATION (Vol 3, pp. 9-30):                       ║
║   │  اشاره 1: Shows opponents themselves rely on al-Waqidi         ║
║   │            in other contexts (Mataʿin of Uthman)               ║
║   │  اشاره 2: "مدایح واقدی" — compiles positive evaluations        ║
║   │            → triggers biographical dossier                      ║
║   │  اشاره 3: "معایب واقدی" — presents negative evaluations        ║
║   │            (showing intellectual honesty)                       ║
║   │  اشاره 4: Concludes non-reporting ≠ discrediting               ║
║   │                                                                 ║
║   ▼                                                                 ║
║  L6  BIOGRAPHICAL DOSSIER: al-Waqidi                               ║
║   │  Cross-references from 6 rijal books:                          ║
║   │  Mizan al-I'tidal, Tahdhib al-Tahdhib, al-'Ibar,             ║
║   │  al-Kashif, al-Ansab, Wafayat al-A'yan                       ║
║   │  Contains jarh/ta'dil from 12+ named evaluators                ║
║   │                                                                 ║
║   ▼                                                                 ║
║  L7  CITATIONS WITH DIRECTIONALITY:                                ║
║      • Razi's Nihayat al-'Uqul → OPPONENT RELIES ON               ║
║      • Mizan al-I'tidal → EVIDENCE (rijal data)                   ║
║      • Tarikh Baghdad → EVIDENCE (positive evaluation)             ║
║      • Tabaqat al-Huffaz → EVIDENCE (al-Waqidi's stature)         ║
║      • Tuhfat p.33 → SOURCE BEING REFUTED                         ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## What the Current Schema Captures vs. What Exists

```
╔════════════════════════════╦══════════════════╦════════════════════╗
║ Dimension                  ║ In the Book      ║ In Current Schema  ║
╠════════════════════════════╬══════════════════╬════════════════════╣
║ Defended hadiths           ║ 10 hadiths       ║ Implicit only      ║
║ Tuhfat micro-claims        ║ 100s per hadith  ║ NOT CAPTURED       ║
║ Argument lineage           ║ 2-8 per claim    ║ NOT CAPTURED       ║
║ Rebuttal lineage           ║ 1-4 per claim    ║ NOT CAPTURED       ║
║ Author's refutation        ║ Multi-pronged    ║ ~800-char chunks   ║
║ اشاره atomic markers       ║ 171 total        ║ NOT CAPTURED       ║
║ Biographical dossiers      ║ 195+ dossiers    ║ NOT CAPTURED       ║
║ Rijal evaluations          ║ 460+ terms       ║ NOT CAPTURED       ║
║ Scholar entities           ║ ~70 evaluated     ║ NOT CAPTURED       ║
║ Rijal books cross-ref'd    ║ ~50 books        ║ NOT CAPTURED       ║
║ Citation directionality    ║ for/against/meta  ║ NOT CAPTURED       ║
║ Raw page/volume refs       ║ All pages        ║ Captured           ║
║ Full text content          ║ 23 MB            ║ Captured (chunks)  ║
║ Full-text search           ║ —                ║ FTS5 index         ║
║ Semantic search            ║ —                ║ 6,800 embeddings   ║
╚════════════════════════════╩══════════════════╩════════════════════╝
```
