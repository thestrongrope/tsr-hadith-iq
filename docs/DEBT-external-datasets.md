# DEBT: Explore External Islamic Scholarly Datasets

## Context

For our Abaqat al-Anwar analysis, we need to verify book attributions, scholar death dates, and isnad chains against authoritative external data.

## Downloaded

- **Hadith Narrators (Kaggle)** — 24,326 scholars with names, grades, teachers, students, birth/death dates (Hijri+Gregorian), places. `reference/datasets/hadith-narrators/all_rawis.csv`

## To Explore

| Dataset | Source | Size | What it has | Use case |
|---------|--------|------|-------------|----------|
| **Sanadset 650K** | [Mendeley](https://data.mendeley.com/datasets/5xth87zwb5/4) | 650K records, 926 books | Narrators, chains, books | Chain verification |
| **Open Hadith Data** | [GitHub](https://github.com/mhashim6/Open-Hadith-Data) | 9 books (Six Books+3) | Full hadith texts, CSV | Verify hadith citations |
| **Hadith JSON** | [GitHub](https://github.com/AhmedBaset/hadith-json) | 50,884 hadiths, 17 books | JSON, Arabic+English | Search specific hadiths |
| **Hadith Data Sets** | [GitHub](https://github.com/abdelrahmaan/Hadith-Data-Sets) | 62,169 hadiths, 9 books | With/without tashkil | Text matching |
| **Hawramani Transmitters** | [hawramani.com](https://hadithtransmitters.hawramani.com/) | 135,068 entries, 62 books | Scholar bios, evaluations | Rijal verification |
| **HadithGraph** | [hawramani.com](https://hawramani.com/hadithgraph/) | Network tool | Isnad graphs + probabilities | Chain visualization |
| **Islamic Data (curated)** | [GitHub](https://github.com/khDev01/islamic-data/) | Meta-list | Links to datasets | Discovery |
| **Isnad Datasets** | [GitHub](https://github.com/muhaddithat/isnad-datasets) | Female narrators | CSV with bios | Specialized reference |
| **Muslim Scholars DB** | [muslimscholars.info](https://muslimscholars.info/) | 24K+ scholars | Interactive web | Source for Kaggle dataset |
| **Sunnah Dataset** | [HuggingFace](https://huggingface.co/datasets/meeAtif/hadith_datasets) | 14 books, bilingual | Arabic+English metadata | Hadith verification |

## Authoritative Web Sources (not downloadable)

1. **Sunnah.com** — 18 Sunni collections (primary verification)
2. **islamweb.net** — Broader Sunni library with fatwas (primary verification)
3. **hadithtransmitters.hawramani.com** — 135K entries from 62 rijal books (#2 for scholar data)
4. **kingoflinks.net** — Shia polemical (enrichment only, not authoritative)

## Tasks

- [ ] Explore Kaggle narrators dataset — match against Vol 23 scholars
- [ ] Download Sanadset 650K from Mendeley
- [ ] Download Open Hadith Data from GitHub
- [ ] Check if Hawramani has downloadable data or API
- [ ] Build cross-reference pipeline: Vol 23 scholar registry → external datasets
