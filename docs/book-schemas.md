# Book Indexing Schemas — Consolidated JSON Models

Each Islamic scholarly book type has a distinct internal structure. However, most books are ultimately *about people* — the schema reflects this by consolidating person-centric books into a single `ScholarEntry` type with source-specific fields populated sparsely. This keeps cross-referencing simple: one scholar, one ID, many source books pointing to it.

Closes #4

---

## Principles

1. **One Scholar, One ID** — a person is a person regardless of which book discusses them. `scholar_id` is the stable identifier across all books.
2. **Sparse population** — not every field is filled for every source. `null` means the source book does not provide that field. For array fields: `null` means the source book has no such section; `[]` means the section exists but contains zero items. Never use `[]` for a section the book type does not have.
3. **PDF → JSON once** — every entry captures the verbatim Arabic so the PDF is never read again.
4. **Abaqat-first** — every schema exposes Abaqat cross-references via an `abaqat_citations` field. Its exact path differs by schema: under `cross_refs.abaqat_citations` for ScholarEntry, top-level for HadithEntry and ReferenceEntry. See each schema for the precise path.

---

## Schema A: ScholarEntry

Covers: Jarh/Ta'dil books, Biographical dictionaries, Tabaqat, Tarikh, and Chronological annals.

**Books using this schema:**
- Tahdhib al-Tahdhib (Jarh/Ta'dil)
- Tahdhib al-Kamal (Jarh/Ta'dil)
- Mizan al-I'tidal (Jarh/Ta'dil, weak narrators only)
- Taqrib al-Tahdhib (Jarh/Ta'dil, condensed)
- Lisan al-Mizan (Jarh/Ta'dil supplement)
- al-Jarh wa al-Ta'dil (Jarh/Ta'dil)
- Wafayat al-A'yan (Biographical)
- Siyar A'lam al-Nubala (Biographical + evaluations)
- al-Wafi bi al-Wafayat (Biographical)
- al-Durar al-Kaminah (Biographical)
- Fawat al-Wafayat (Biographical)
- al-Daw' al-Lami' (Biographical)
- Bughyat al-Wu'at (Biographical)
- Husn al-Muhadara (Biographical)
- Tadhkirat al-Huffaz (Tabaqat)
- Tabaqat al-Huffaz (Tabaqat)
- Tabaqat al-Shafi'iyya al-Kubra (Tabaqat)
- al-Tabaqat al-Kubra — Ibn Sa'd (Tabaqat)
- Tabaqat al-Hanabilah (Tabaqat)
- al-Jawahir al-Mudiyyah (Tabaqat)
- Khulasat al-Athar (Biographical)
- Tarikh Baghdad (City history — person + hadiths they narrated)
- al-'Ibar fi Khabar man Ghabar (Chronological — death notices)
- Mir'at al-Janan (Chronological — death notices)

```json
{
  "entry_id": "tahdhib-2-156",
  "scholar_id": "jafar-ibn-muhammad-al-sadiq",
  "source_book": "Tahdhib al-Tahdhib",
  "source_book_arabic": "تهذيب التهذيب",
  "book_type": "jarh_tadil",
  "volume": 2,
  "page": 103,
  "entry_number": 156,

  "subject": {
    "name_arabic": "جعفر بن محمد بن علي بن الحسين بن علي بن أبي طالب",
    "name_english": "Ja'far ibn Muhammad ibn Ali ibn al-Husayn",
    "kunya": "أبو عبدالله",
    "laqab": "الصادق",
    "nisba": "الهاشمي المدني",
    "birth_ah": null,
    "death_ah": 148,
    "death_place": "المدينة",
    "profession": null,
    "madhab": null,
    "sect": "شيعي",
    "lineage": ["جعفر", "محمد", "علي", "الحسين", "علي بن أبي طالب"]
  },

  "generation": null,

  "teachers": [
    {"name_arabic": "أبوه محمد بن علي الباقر", "name_english": "his father Muhammad al-Baqir", "scholar_id": "muhammad-ibn-ali-al-baqir"}
  ],

  "students": [
    {"name_arabic": "مالك بن أنس", "name_english": "Malik ibn Anas", "scholar_id": "malik-ibn-anas"},
    {"name_arabic": "سفيان الثوري", "name_english": "Sufyan al-Thawri", "scholar_id": "sufyan-al-thawri"},
    {"name_arabic": "شعبة بن الحجاج", "name_english": "Shu'bah ibn al-Hajjaj", "scholar_id": "shubah-ibn-al-hajjaj"}
  ],

  "evaluations": [
    {
      "evaluator_arabic": "يحيى بن سعيد القطان",
      "evaluator_english": "Yahya ibn Sa'id al-Qattan",
      "evaluator_id": "yahya-ibn-said-al-qattan",
      "term_arabic": "في نفسي منه شيء",
      "grade": "jarh_1",
      "verbatim_quote": "سئل يحيى بن سعيد عنه فقال في نفسي منه شيء ومجالد أحب إليّ منه",
      "nested_source": null,
      "domain": null
    },
    {
      "evaluator_arabic": "ابن حجر",
      "evaluator_english": "Ibn Hajar",
      "evaluator_id": "ibn-hajar-al-asqalani",
      "term_arabic": "صدوق",
      "grade": "tadil_4",
      "verbatim_quote": null,
      "nested_source": null,
      "domain": null
    }
  ],

  "hadith_collections_included_in": ["خ", "م", "د", "ت", "س", "ق"],

  "works_authored": [],

  "key_quotes": [],

  "anecdotes": null,

  "biography_text": null,

  "hadiths_narrated": null,

  "year_entry": null,

  "cross_refs": {
    "scholar_id": "jafar-ibn-muhammad-al-sadiq",
    "tahdhib_entry": "tahdhib-2-156",
    "mizan_entry": null,
    "siyar_entry": null,
    "wafayat_entry": null,
    "tarikh_baghdad_entry": null,
    "abaqat_citations": [
      {"volume": 3, "line": 4107, "context": "dossier_subject"}
    ]
  },

  "verbatim_full_arabic": "جعفر بن محمد بن علي بن الحسين بن علي بن أبي طالب أبو عبد الله الهاشمي المدني الصادق...",

  "notes": null
}
```

### Evaluation field notes

**Multiple evaluations from the same evaluator:** One evaluator can appear multiple times in `evaluations[]`. For example, Abu Hatim says both `متروك` (jarh_4) and `يضع الحديث` (jarh_5) for al-Waqidi — these are stored as separate objects in the array.

**The `domain` field:** Some evaluators qualify their tawthiq to a specific domain. For example, Ibrahim al-Harbi says al-Waqidi is `أمين على الإسلام` (trusted on Islamic history) but `فأما الجاهلية فلم يعلم فيها شيئاً` (knows nothing about pre-Islamic matters). When a tawthiq or tajrih is domain-limited, `domain` captures the scope:

```json
{
  "evaluator_arabic": "إبراهيم الحربي",
  "term_arabic": "أمين",
  "grade": "tadil_4",
  "verbatim_quote": "الواقدي أمين على الإسلام وكان أعلم الناس بأمر الإسلام فأما الجاهلية فلم يعلم فيها شيئاً",
  "domain": "أمور الإسلام فقط — لا الجاهلية"
}
```

When `domain` is `null`, the evaluation applies universally. This is the common case.

**The `nested_source` field:** When an evaluator's statement is quoted not from their own book but through an intermediary (e.g., "al-Khatib said in Tarikh Baghdad that Ahmad said..."), `nested_source` captures the intermediary book. This is critical because Mir Hamid Husain often cites evaluations through secondary sources.

### book_type values

| Value | Books |
|-------|-------|
| `jarh_tadil` | Tahdhib, Mizan, Taqrib, Lisan, al-Jarh wa al-Ta'dil, Tahdhib al-Kamal |
| `biographical` | Wafayat, Siyar, Wafi, Durar, Fawat, Daw', Bughyat, Husn al-Muhadara, Khulasat |
| `tabaqat` | Tadhkirat, Tabaqat al-Huffaz, Tabaqat al-Shafi'iyya, Tabaqat al-Kubra, Tabaqat al-Hanabilah, Jawahir |
| `tarikh` | Tarikh Baghdad |
| `chronological` | al-'Ibar, Mir'at al-Janan |

### Field population by book_type

| Field | jarh_tadil | biographical | tabaqat | tarikh | chronological |
|-------|-----------|-------------|---------|--------|---------------|
| `evaluations` | ✅ primary | sometimes | sometimes | rarely | rarely |
| `teachers` / `students` | ✅ | ✅ | sometimes | sometimes | ❌ |
| `works_authored` | sometimes | ✅ | sometimes | sometimes | ❌ |
| `biography_text` | ❌ | ✅ | sometimes | sometimes | ❌ |
| `generation` | ❌ | sometimes (Siyar) | ✅ | ❌ | ❌ |
| `hadiths_narrated` | ❌ | ❌ | ❌ | ✅ primary | ❌ |
| `year_entry.year_ah` / `year_entry.year_ce` | ❌ | ❌ | ❌ | ❌ | ✅ primary |
| `anecdotes` | ❌ | ✅ | sometimes | sometimes | ❌ |

### Chronological entry (al-'Ibar, Mir'at)

For chronological annals, the top-level entry is the year, with `deaths` as an array of embedded ScholarEntries (condensed):

A `DeathNotice` is a condensed ScholarEntry: it captures the fields the source book actually provides for a death notice (name, brief bio, death details) without the full teacher/student/evaluation apparatus. Full biographical data lives in the ScholarEntry records for that `scholar_id` in other books.

```json
{
  "entry_id": "ibar-year-413",
  "source_book": "al-Ibar fi Khabar man Ghabar",
  "book_type": "chronological",
  "year_entry": {
    "year_ah": 413,
    "year_ce": 1022
  },

  "events": [
    {"description_arabic": "..."}
  ],

  "deaths": [
    {
      "scholar_id": "shaykh-al-mufid",
      "name_arabic": "الشيخ المفيد أبو عبدالله محمد بن محمد بن النعمان البغدادي الكرخي",
      "kunya": "أبو عبدالله",
      "laqab": "المفيد، ابن المعلم",
      "nisba": "البغدادي الكرخي",
      "death_ah": 413,
      "death_month_arabic": "رمضان",
      "age_at_death": 76,
      "madhab": null,
      "sect": "شيعي",
      "brief_bio_arabic": "عالم الشيعة وإمام الرافضة وصاحب التصانيف الكثيرة وكان رئيس الكلام والفقه والجدل",
      "works_count": 200,
      "evaluations": null,
      "verbatim_full_arabic": "والشيخ المفيد أبو عبدالله محمد بن محمد بن النعمان البغدادي الكرخي...",
      "cross_refs": {
        "scholar_id": "shaykh-al-mufid",
        "abaqat_citations": [{"volume": 3, "line": 4107, "context": "dossier_subject"}]
      }
    }
  ]
}
```

### Tarikh Baghdad entry

For city history books, `hadiths_narrated` carries the hadiths the subject transmitted through that city:

```json
{
  "entry_id": "tarikh-baghdad-123-456",
  "scholar_id": "some-scholar-id",
  "source_book": "Tarikh Baghdad",
  "book_type": "tarikh",
  "volume": 5,
  "page": 312,

  "subject": { "...": "same as ScholarEntry.subject" },

  "evaluations": [
    { "...": "same structure as ScholarEntry.evaluations items — evaluator_arabic, grade, verbatim_quote, etc." }
  ],

  "hadiths_narrated": [
    {
      "hadith_id": "tarikh-baghdad-hadith-5-312-1",
      "chain_summary_arabic": "حدثنا ... عن ... عن النبي ﷺ",
      "matn_arabic": "...",
      "topic_tags": ["ghadir", "wilayah"],
      "narrator_refs": ["scholar-id-1", "scholar-id-2"]
    }
  ],

  "cross_refs": { "...": "..." }
}
```

---

## Schema B: HadithEntry

Covers all hadith collections. The core structure is universal; sub-type fields are populated based on the collection.

**Books using this schema:**
- Sahih al-Bukhari
- Sahih Muslim
- Sunan al-Tirmidhi, Sunan Abi Dawud, Sunan al-Nasa'i, Sunan Ibn Majah
- Musnad Ahmad ibn Hanbal
- al-Mustadrak (al-Hakim)
- al-Mu'jam al-Kabir / al-Awsat / al-Saghir (al-Tabarani)
- al-Musannaf (Ibn Abi Shayba, Abd al-Razzaq)

```json
{
  "entry_id": "muslim-44-2408a",
  "source_book": "Sahih Muslim",
  "source_book_arabic": "صحيح مسلم",
  "collection_type": "sahih",

  "location": {
    "book_number": 44,
    "book_name_arabic": "كتاب فضائل الصحابة",
    "book_name_english": "Book of the Companions' Virtues",
    "chapter_arabic": "باب فضائل علي بن أبي طالب رضي الله عنه",
    "chapter_english": "Chapter on the virtues of Ali ibn Abi Talib",
    "hadith_number": 2408,
    "variant": "a"
  },

  "isnad": {
    "full_chain_arabic": "حدثنا زهير بن حرب وشجاع بن مخلد كلاهما عن ابن علية... عن زيد بن أرقم",
    "transmission_type": "marfu",
    "companion": {
      "name_arabic": "زيد بن أرقم",
      "name_english": "Zayd ibn Arqam",
      "scholar_id": "zayd-ibn-arqam"
    },
    "chain_links": [
      {
        "name_arabic": "زهير بن حرب",
        "name_english": "Zuhayr ibn Harb",
        "scholar_id": "zuhayr-ibn-harb",
        "role": "حدثنا",
        "jarh_grade": "tadil_3"
      },
      {
        "name_arabic": "إسماعيل بن إبراهيم ابن علية",
        "name_english": "Ismail ibn Ibrahim Ibn Ulayyah",
        "scholar_id": "ismail-ibn-ibrahim-ibn-ulayyah",
        "role": "عن",
        "jarh_grade": "tadil_3"
      }
    ]
  },

  "matn": {
    "arabic": "إني تارك فيكم الثقلين أولهما كتاب الله فيه الهدى والنور فخذوا بكتاب الله... وأهل بيتي أذكركم الله في أهل بيتي",
    "english_translation": null,
    "key_phrase_arabic": "كتاب الله وعترتي أهل بيتي"
  },

  "grading": {
    "compiler_grade": null,
    "compiler_condition": null,
    "external_grades": []
  },

  "topic_tags": ["thaqalayn", "ahl_al_bayt", "kitab_allah"],

  "sunnah_com_ref": "muslim:2408a",

  "abaqat_citations": [
    {"volume": 1, "line": 711, "context": "main_hadith_cited"}
  ],

  "notes": null
}
```

### collection_type values

| Value | Books | Notes |
|-------|-------|-------|
| `sahih` | Bukhari, Muslim | `grading` is always present for schema consistency; `compiler_grade` is `null` (the collection's inclusion is itself the grade), `external_grades` carries any later scholar comments |
| `sunan` | Tirmidhi, Abi Dawud, Nasa'i, Ibn Majah | Per-hadith grading required |
| `musnad` | Musnad Ahmad | Organized by companion, not topic |
| `mustadrak` | al-Mustadrak | al-Hakim's grade + al-Dhahabi's talkhis comment — critical for Abaqat |
| `mujam` | al-Mu'jam al-Kabir/Awsat/Saghir | Organized by teacher or companion |
| `musannaf` | Ibn Abi Shayba, Abd al-Razzaq | Fiqh chapters, includes athar (non-hadith reports) |

### Sub-type: Mustadrak

The Hakim/Dhahabi dialectic is the single most important grading dispute in Abaqat — Mir Hamid Husain frequently cites al-Hakim's sahih declaration against Dehlawi's dismissals. Both voices must be captured:

```json
{
  "grading": {
    "compiler_grade": "صحيح",
    "compiler_condition": "على شرط الشيخين",
    "external_grades": [
      {
        "grader": "al-Dhahabi",
        "grader_arabic": "الذهبي",
        "grade": "ضعيف",
        "verbatim_comment": "بل هو منكر",
        "source": "Talkhis al-Mustadrak",
        "agrees_with_compiler": false
      }
    ]
  }
}
```

### Sub-type: Musnad Ahmad

Organized by companion rather than topic. Add `companion_section` at the top level:

```json
{
  "companion_section": {
    "companion_arabic": "زيد بن أرقم",
    "companion_english": "Zayd ibn Arqam",
    "scholar_id": "zayd-ibn-arqam"
  }
}
```

### Sub-type: Sunan

Per-hadith grading is required. `compiler_grade` carries the compiler's own verdict (e.g. Tirmidhi's حسن صحيح), and `external_grades` carries later scholars:

```json
{
  "grading": {
    "compiler_grade": "حسن صحيح",
    "compiler_condition": null,
    "external_grades": [
      {
        "grader": "al-Albani",
        "grader_arabic": "الألباني",
        "grade": "صحيح",
        "verbatim_comment": null,
        "source": "Sahih al-Tirmidhi",
        "agrees_with_compiler": true
      }
    ]
  }
}
```

### topic_tags vocabulary

Topic tags are drawn from Abaqat's actual argument structure — the hadiths Mir Hamid Husain defends:

| Tag | Arabic | Description |
|-----|--------|-------------|
| `thaqalayn` | حديث الثقلين | "I leave among you two weighty things" |
| `ghadir` | حديث الغدير | "Whoever's master I am, Ali is his master" |
| `manzilah` | حديث المنزلة | "You are to me as Harun was to Musa" |
| `tayr` | حديث الطائر | "O Allah, bring the one you love most" |
| `dar` | حديث الدار | Ali named as successor at the house of Abu Talib |
| `wilayah` | حديث الولاية | Direct wilayah declarations |
| `mawaddah` | حديث المودة | Love of Ahl al-Bayt as Quranic obligation |
| `safinah` | حديث السفينة | "My Ahl al-Bayt are like Noah's ark" |
| `aman` | حديث الأمان | "My companions are security for my nation" |
| `nur` | حديث النور | Nur/light hadith |
| `hitta` | حديث حطة | Ahl al-Bayt as gate of forgiveness |
| `ahl_al_bayt` | أهل البيت | General Ahl al-Bayt virtue |
| `fadail_ali` | فضائل علي | Ali-specific virtues |
| `imamate` | الإمامة | General imamate argument |

---

## Schema C: ReferenceEntry

Covers bibliography and genealogical dictionaries — books that index *other works* or *lineages* rather than individuals.

### C1: Bibliography (Kashf al-Zunun)

```json
{
  "entry_id": "kashf-2-1234",
  "source_book": "Kashf al-Zunun",
  "source_book_arabic": "كشف الظنون عن أسامي الكتب والفنون",
  "volume": 2,
  "page": 456,

  "book_title_arabic": "تهذيب التهذيب",
  "book_title_english": "Tahdhib al-Tahdhib",
  "book_title_variants": ["تهذيب تهذيب الكمال"],

  "author": {
    "name_arabic": "ابن حجر العسقلاني",
    "name_english": "Ibn Hajar al-Asqalani",
    "scholar_id": "ibn-hajar-al-asqalani",
    "death_ah": 852
  },

  "subject_category": "رجال الحديث",
  "volumes": 12,
  "description_arabic": "اختصره من تهذيب الكمال للمزي وزاد عليه فوائد",
  "based_on": ["tahdhib-al-kamal"],
  "abridged_by": ["taqrib-al-tahdhib"],

  "abaqat_citations": [],
  "notes": null
}
```

### C2: Genealogical (al-Ansab)

al-Sam'ani's al-Ansab organizes by nisba. The entry is the nisba itself, with scholars who carry it listed as scholar refs — not full biographies.

```json
{
  "entry_id": "ansab-nisba-naysaburi",
  "source_book": "al-Ansab",
  "source_book_arabic": "الأنساب",
  "volume": 5,
  "page": 478,

  "nisba_arabic": "النيسابوري",
  "nisba_english": "al-Naysaburi",
  "nisba_origin": "نيسابور — مدينة في خراسان",

  "scholars": [
    {
      "name_arabic": "مسلم بن الحجاج النيسابوري",
      "name_english": "Muslim ibn al-Hajjaj al-Naysaburi",
      "scholar_id": "muslim-ibn-al-hajjaj",
      "death_ah": 261,
      "brief_note_arabic": "صاحب الصحيح"
    }
  ],

  "abaqat_citations": [],
  "notes": null
}
```

---

## Schema D: Polemical Works

Already modelled in `docs/abaqat-data-model-v2.md`. Key entities:
- `VolumeSection`, `OpponentClaim`, `NarratorCitation`, `AuthorResponse`
- `DalalahProof`, `BiographicalDossier`, `RijalEvaluation`, `Tanbih`
- `Scholar`, `SourceBook`, `Citation`, `ArgumentRebuttalLineage`

No duplication here — `Scholar` entities in Abaqat's model use the same `scholar_id` as ScholarEntry across all other schemas.

---

## JarhGrade System

Based on the standard **6+6 system** (al-Suyuti in Tadrib al-Rawi, expanded from al-Iraqi and Ibn Abi Hatim). This is the most widely used classification in hadith sciences.

Each evaluation in the schema stores:
- `term_arabic` — the exact verbatim term the evaluator used (never normalized)
- `grade` — the mapped rank from the system below (`tadil_1` through `tadil_6`, `jarh_1` through `jarh_6`)

**Important caveat:** The same term can mean different things depending on the evaluator. For example, when Yahya ibn Ma'in says "لا بأس به" he means "ثقة" (Grade tadil_3), but for most other scholars it means Grade tadil_4. The `grade` mapping must account for evaluator-specific conventions. When ambiguous, store the term verbatim and leave `grade` as `null` for the scholar to resolve.

### Maratib al-Ta'dil (6 ranks, highest to lowest)

| Grade value | Rank | Example terms (ألفاظ) | Ruling |
|-------------|------|----------------------|--------|
| `tadil_1` | Superlative praise | أوثق الناس، أثبت الناس، إليه المنتهى في التثبت | يحتج به |
| `tadil_2` | Reinforced (repetition or two attributes) | ثقة ثقة، ثقة ثبت، ثقة متقن، ثقة حافظ، ثقة حجة، ثبت حجة | يحتج به |
| `tadil_3` | Single attribute | ثقة، متقن، ثبت، حجة، حافظ ضابط | يحتج به |
| `tadil_4` | Uprightness without full dabt | صدوق، لا بأس به، ليس به بأس، مأمون | يحتج به |
| `tadil_5` | Below saduq, close to criticism | محلّه الصدق، شيخ وسط، صالح الحديث، حسن الحديث، صدوق يهم، صدوق سيء الحفظ، روى عنه الناس | حسن لغيره (مع متابعة) |
| `tadil_6` | Borderline, needs corroboration | مقبول، يروى حديثه، يعتبر به، مقارب الحديث | مقبول عند المتابعة، وإلا فليّن |

### Maratib al-Jarh (6 ranks, mildest to harshest)

| Grade value | Rank | Example terms (ألفاظ) | Ruling |
|-------------|------|----------------------|--------|
| `jarh_1` | Mild softening (تليين) | ليّن الحديث، فيه مقال، فيه ضعف، ليس بذاك، ليس بالقوي، تعرف وتنكر | يكتب حديثه وينظر |
| `jarh_2` | Explicit weakness | ضعيف، لا يحتج به، منكر الحديث، مضطرب الحديث، سيء الحفظ | لا يحتج به |
| `jarh_3` | Very weak, not to be written | ضعيف جداً، واهٍ، واهي الحديث، ليس بشيء، مردود، ضعّفوه | لا يكتب حديثه |
| `jarh_4` | Abandoned, accused | متروك، ساقط، هالك، ذاهب الحديث، متروك الحديث، ليس بثقة | يترك حديثه |
| `jarh_5` | Explicit lying | كذّاب، وضّاع، يضع الحديث، يكذب، دجّال | موضوع |
| `jarh_6` | Superlative in lying | أكذب الناس، ركن الكذب، إليه المنتهى في الكذب | موضوع |

### Also track: Unknown status

Not part of the jarh/ta'dil scale but critical for narrator evaluation:

| Grade value | Term | Meaning |
|-------------|------|---------|
| `majhul_hal` | مستور، مجهول الحال | Narrated from by more than one, but not authenticated |
| `majhul_ayn` | مجهول العين | Only one person narrated from him |

### Mapping to Ibn Hajar's 12-Grade (Taqrib al-Tahdhib)

Since Taqrib is one of our key source books, here is how his grades map:

| Ibn Hajar Grade | Our grade | His description |
|----------------|-----------|-----------------|
| 1 | — | صحابي (Companion, not graded) |
| 2 | `tadil_1` or `tadil_2` | أكد المدح — superlative or reinforced |
| 3 | `tadil_3` | أفرد بصفة — single attribute (ثقة) |
| 4 | `tadil_4` | قصر عن الثالثة قليلاً — (صدوق، لا بأس به) |
| 5 | `tadil_5` | قصر عن الرابعة — (صدوق يهم، صدوق سيء الحفظ) |
| 6 | `tadil_6` | مقبول — accepted only with corroboration |
| 7 | `majhul_hal` | مستور — unknown condition |
| 8 | `jarh_2` | ضعيف |
| 9 | `majhul_ayn` | مجهول — unknown identity |
| 10 | `jarh_4` | متروك / واهي الحديث / ساقط |
| 11 | `jarh_5` | متّهم بالكذب أو الوضع |
| 12 | `jarh_5` or `jarh_6` | كاذب / وضّاع |

### Sources

- Ibn Abi Hatim, Muqaddimat al-Jarh wa al-Ta'dil (original 4+4 system)
- al-Suyuti, Tadrib al-Rawi (expanded 6+6 system)
- al-Iraqi, al-Taqyid wa al-Idah (basis for al-Suyuti's expansion)
- al-Sakhawi, Fath al-Mughith (detailed commentary)
- Ibn Hajar, Muqaddimat Taqrib al-Tahdhib (12-grade system)
- https://hadithtransmitters.hawramani.com (cross-reference for narrator data)

---

## Cross-Referencing

The `scholar_id` field links the same person across all schemas. Given a scholar cited in Abaqat, the lookup is:

1. Find `scholar_id` from Abaqat's dossier
2. Query all ScholarEntry records with that `scholar_id`
3. Get evaluations from Tahdhib, Mizan, Siyar etc. in one call
4. Get all HadithEntry records where any `isnad.chain_links[].scholar_id` matches
5. See exactly which hadiths pass through a contested narrator

```json
{
  "cross_refs": {
    "scholar_id": "jafar-ibn-muhammad-al-sadiq",
    "tahdhib_entry": "tahdhib-2-156",
    "tahdhib_kamal_entry": "tahdhib-kamal-5-234",
    "mizan_entry": null,
    "siyar_entry": "siyar-6-255",
    "wafayat_entry": null,
    "tarikh_baghdad_entry": null,
    "abaqat_citations": [
      {"volume": 3, "line": 4107, "context": "dossier_subject"}
    ]
  }
}
```

---

## Edition References

Mir Hamid Husain provides precise edition information in footnotes. Different editions of the same book have different pagination, so edition data is critical for verification. Every citation in Abaqat's dossiers should track which edition was used.

```json
{
  "edition": {
    "editor": "علي محمد البجاوي",
    "publisher": null,
    "city": "مصر",
    "edition_number": "الطبعة الأولى",
    "manuscript_note": null
  }
}
```

For manuscripts (common in Mir Hamid Husain's time — many books were not yet printed):

```json
{
  "edition": {
    "editor": null,
    "publisher": null,
    "city": null,
    "edition_number": null,
    "manuscript_note": "مخطوط في مكتبة لكهنو"
  }
}
```

This field is optional on ScholarEntry (used when we know which edition was indexed) and required on Schema D citations (since Abaqat always specifies editions in footnotes).

**Real examples from the al-Waqidi dossier (Vol 3):**
- Mizan al-I'tidal: `ج٣ ص٥١٧ ط الأولى بتحقيق علي محمد البجاوي بمصر`
- Tahdhib al-Tahdhib: `ج٣ ص٤٩ مخطوط في مكتبة لكهنو`
- Wafayat al-A'yan: `ج٤ ط بيروت... الدكتور إحسان عباس`
- Mir'at al-Janan: `ج١ ص٧٥ ط دار المعارف النظامية بحيدرآباد الدكن`

---

## Additional Source Books (discovered from al-Waqidi dossier)

Testing schemas against actual Abaqat dossiers revealed books cited by Mir Hamid Husain that are NOT in our Tier 1 or Tier 2 lists:

| Book | Arabic | Author | Type | Schema |
|------|--------|--------|------|--------|
| al-Mughni fi al-Du'afa' | المغني في الضعفاء | al-Dhahabi | Jarh/Ta'dil (weak narrators) | A |
| al-Kashif | الكاشف | al-Dhahabi | Jarh/Ta'dil (condensed) | A |
| al-Tarikh al-Saghir | التاريخ الصغير | al-Bukhari | Chronological | A |
| 'Umdat al-Qari | عمدة القاري | al-'Ayni | Hadith commentary (not rijal) | — |
| Taqrib al-Tahdhib | تقريب التهذيب | Ibn Hajar | Jarh/Ta'dil (condensed) | A |

'Umdat al-Qari (Bukhari commentary) doesn't fit any of our 4 schemas cleanly — it's a **hadith commentary** (شرح حديث), not a rijal book or hadith collection. If more of these appear in other dossiers, we may need a Schema E for commentary works.

---

## Indexing Priority

| Priority | Book | Schema | Est. entries | Why first |
|----------|------|--------|-------------|-----------|
| 1 | Tahdhib al-Tahdhib | A (jarh_tadil) | ~8,000 | Most cited in Abaqat (12 vols), already verified |
| 2 | Mizan al-I'tidal | A (jarh_tadil) | ~11,000 | Primary tajrih source, verified |
| 3 | Wafayat al-A'yan | A (biographical) | ~855 | Small, high value, verified |
| 4 | Tadhkirat al-Huffaz | A (tabaqat) | ~1,100 | Verified, single volume |
| 5 | al-'Ibar | A (chronological) | ~600 | Concise, verified |
| 6 | Tarikh Baghdad | A (tarikh) | ~7,800 | 17 vols, high Abaqat citation count |
| 7 | Tahdhib al-Kamal | A (jarh_tadil) | ~8,000 | 35 vols, most detailed — index after Tahdhib |
| 8 | Siyar A'lam al-Nubala | A (biographical) | ~600 | Already split into chunks |
| 9 | Tabaqat al-Shafi'iyya | A (tabaqat) | ~500 | 10 vols, useful for Shafi'i scholars |
