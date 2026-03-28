#!/usr/bin/env python3
"""
Restructure Vol 23 citations by Abaqat's actual argument flow:

  Layer 1: HADITH EVIDENCE — books that contain Hadith al-Safinah
  Layer 2: AUTHENTICATION — rijal/jarh books establishing narrator reliability
  Layer 3: REBUTTALS — counter-arguments to Dehlavi (textual + logical)

Reads from already-extracted data (no PDF reads, no API calls).

Usage:
  uv run python scripts/restructure_vol23_argument.py
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
CITATIONS_FILE = REPO_ROOT / "docs" / "citation-extraction" / "vol23-grok.json"
REGISTRY_FILE = REPO_ROOT / "docs" / "citation-extraction" / "vol23-book-registry.json"
STRUCTURE_FILE = REPO_ROOT / "docs" / "volume-structure" / "vol23-structure.json"
OUTPUT_JSON = REPO_ROOT / "docs" / "citation-extraction" / "vol23-argument-structure.json"
OUTPUT_MD = REPO_ROOT / "docs" / "citation-extraction" / "vol23-argument-structure.md"

# Map citation contexts to argument layers
LAYER_MAP = {
    "HADITH_SOURCE": "evidence",
    "TAWATUR_PROOF": "evidence",
    "AUTHOR_TAWTHIQ": "authentication",
    "AUTHOR_TAJRIH": "authentication",
    "PRIMARY_REBUTTAL": "rebuttal",
    "REBUTTAL_LINEAGE": "rebuttal",
    "ARGUMENT_LINEAGE": "rebuttal",
    "SUB_CLAIM_REBUTTAL": "rebuttal",
    "LINGUISTIC": "rebuttal",
    "CONTRADICTION": "rebuttal",
    "CROSS_REF": "other",
    "FOOTNOTE": "other",
}


def load_data():
    with open(CITATIONS_FILE) as f:
        citations = json.load(f)

    registry = {}
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as f:
            reg_data = json.load(f)
        for b in reg_data.get("books", []):
            registry[b["book_arabic"]] = b

    structure = None
    if STRUCTURE_FILE.exists():
        with open(STRUCTURE_FILE) as f:
            structure = json.load(f)

    return citations, registry, structure


def build_argument_layers(citations, registry):
    layers = {
        "evidence": {"books": {}, "citations": 0},
        "authentication": {"books": {}, "citations": 0},
        "rebuttal": {"books": {}, "citations": 0},
        "other": {"books": {}, "citations": 0},
    }

    for c in citations["citations"]:
        layer = LAYER_MAP.get(c["citation_context"], "other")
        layers[layer]["citations"] += 1

        key = c["book_arabic"]
        if key not in layers[layer]["books"]:
            reg = registry.get(key, {})
            layers[layer]["books"][key] = {
                "book_arabic": c["book_arabic"],
                "book_transliterated": c.get("book_transliterated", ""),
                "standard_title_english": reg.get("standard_title_english", ""),
                "author_arabic": c.get("author_arabic", ""),
                "author_death_ah": c.get("author_death_ah"),
                "schema": reg.get("schema", "?"),
                "book_type": reg.get("book_type", "?"),
                "citation_count": 0,
                "contexts": set(),
                "subject_scholars": set(),
            }
        layers[layer]["books"][key]["citation_count"] += 1
        layers[layer]["books"][key]["contexts"].add(c["citation_context"])
        if c.get("subject_scholar"):
            layers[layer]["books"][key]["subject_scholars"].add(c["subject_scholar"])

    # Convert sets to lists
    for layer in layers.values():
        for book in layer["books"].values():
            book["contexts"] = sorted(book["contexts"])
            book["subject_scholars"] = sorted(book["subject_scholars"])

    return layers


def compute_stats(layers):
    stats = {}
    all_evidence_books = set(layers["evidence"]["books"].keys())
    all_auth_books = set(layers["authentication"]["books"].keys())
    all_rebuttal_books = set(layers["rebuttal"]["books"].keys())
    all_books = all_evidence_books | all_auth_books | all_rebuttal_books

    # Evidence layer stats
    ev_books = list(layers["evidence"]["books"].values())
    death_years = [b["author_death_ah"] for b in ev_books if b["author_death_ah"]]

    stats["evidence"] = {
        "total_books": len(ev_books),
        "total_citations": layers["evidence"]["citations"],
        "earliest_author_ah": min(death_years) if death_years else None,
        "latest_author_ah": max(death_years) if death_years else None,
        "time_span_years": (max(death_years) - min(death_years)) if len(death_years) >= 2 else 0,
        "by_century": dict(Counter(
            f"{(d // 100) + 1}th century AH" for d in death_years
        )),
    }

    # Auth layer stats
    auth_books = list(layers["authentication"]["books"].values())
    auth_tawthiq = [b for b in auth_books if "AUTHOR_TAWTHIQ" in b["contexts"]]
    auth_tajrih = [b for b in auth_books if "AUTHOR_TAJRIH" in b["contexts"]]
    stats["authentication"] = {
        "total_books": len(auth_books),
        "total_citations": layers["authentication"]["citations"],
        "tawthiq_books": len(auth_tawthiq),
        "tajrih_books": len(auth_tajrih),
        "tawthiq_citations": sum(b["citation_count"] for b in auth_tawthiq),
        "tajrih_citations": sum(b["citation_count"] for b in auth_tajrih),
        "unique_scholars_evaluated": len(set(
            s for b in auth_books for s in b["subject_scholars"]
        )),
    }

    # Rebuttal layer stats
    reb_books = list(layers["rebuttal"]["books"].values())
    reb_types = Counter()
    for b in reb_books:
        for ctx in b["contexts"]:
            reb_types[ctx] += 1
    stats["rebuttal"] = {
        "total_books": len(reb_books),
        "total_citations": layers["rebuttal"]["citations"],
        "by_type": dict(reb_types),
    }

    stats["total_unique_books"] = len(all_books)
    stats["dual_role_evidence_auth"] = len(all_evidence_books & all_auth_books)
    stats["dual_role_evidence_rebuttal"] = len(all_evidence_books & all_rebuttal_books)

    return stats


def generate_markdown(layers, stats):
    lines = []

    lines.append("# Vol 23 — Hadith al-Safinah: Argument Structure")
    lines.append("")
    lines.append("> مَثَلُ أَهْلِ بَيْتِي كَمَثَلِ سَفِينَةِ نُوحٍ مَنْ رَكِبَهَا نَجَا وَمَنْ تَخَلَّفَ عَنْهَا هَلَكَ")
    lines.append("> ")
    lines.append('> "The likeness of my Ahl al-Bayt among you is like Noah\'s ark — whoever boards it is saved, and whoever stays behind is destroyed."')
    lines.append("")
    lines.append("---")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append("Mir Hamid Husain's argument in Volume 23 follows a three-layer structure:")
    lines.append("")
    lines.append(f"| Layer | Purpose | Books | Citations |")
    lines.append(f"|-------|---------|-------|-----------|")
    lines.append(f"| **1. Hadith Evidence** | Prove the hadith exists in Sunni sources | {stats['evidence']['total_books']} | {stats['evidence']['total_citations']} |")
    lines.append(f"| **2. Authentication** | Establish narrator reliability via rijal | {stats['authentication']['total_books']} | {stats['authentication']['total_citations']} |")
    lines.append(f"| **3. Rebuttals** | Refute Dehlavi's counter-arguments | {stats['rebuttal']['total_books']} | {stats['rebuttal']['total_citations']} |")
    lines.append(f"| **Total** | | **{stats['total_unique_books']}** | **518** |")
    lines.append("")

    if stats["evidence"].get("earliest_author_ah") and stats["evidence"].get("latest_author_ah"):
        lines.append(f"Evidence spans {stats['evidence']['time_span_years']} years of Sunni scholarship ")
        lines.append(f"(d. {stats['evidence']['earliest_author_ah']} AH — d. {stats['evidence']['latest_author_ah']} AH)")
        lines.append("")

    # Layer 1: Evidence
    lines.append("---")
    lines.append("")
    lines.append("## Layer 1: Hadith Evidence")
    lines.append("")
    lines.append(f"**{stats['evidence']['total_books']} Sunni books** containing Hadith al-Safinah, cited **{stats['evidence']['total_citations']} times**.")
    lines.append("")
    lines.append("These are the books Mir Hamid Husain points to and says: \"This hadith is recorded in YOUR sources.\"")
    lines.append("The sheer number establishes tawatur (mass-transmission), making denial impossible.")
    lines.append("")

    # By century
    if stats["evidence"].get("by_century"):
        lines.append("### Distribution by century")
        lines.append("")
        lines.append("| Century | Books |")
        lines.append("|---------|-------|")
        for century, count in sorted(stats["evidence"]["by_century"].items()):
            lines.append(f"| {century} | {count} |")
        lines.append("")

    # Evidence book list
    lines.append("### Complete list of Sunni sources containing Hadith al-Safinah")
    lines.append("")
    lines.append("| # | Arabic Title | English Title | Author | d. AH | Cited |")
    lines.append("|---|-------------|---------------|--------|-------|-------|")
    ev_sorted = sorted(layers["evidence"]["books"].values(),
                       key=lambda x: x["citation_count"], reverse=True)
    for i, b in enumerate(ev_sorted, 1):
        ar = b["book_arabic"]
        en = b.get("standard_title_english") or b.get("book_transliterated") or ""
        author = (b.get("author_arabic") or "")[:30]
        death = b.get("author_death_ah") or "?"
        lines.append(f"| {i} | {ar} | {en} | {author} | {death} | {b['citation_count']} |")
    lines.append("")

    # Layer 2: Authentication
    lines.append("---")
    lines.append("")
    lines.append("## Layer 2: Authentication")
    lines.append("")
    lines.append(f"**{stats['authentication']['total_books']} rijal/biographical books** cited **{stats['authentication']['total_citations']} times** to evaluate narrators.")
    lines.append("")
    lines.append(f"- Tawthiq (positive evaluations): {stats['authentication']['tawthiq_books']} books, {stats['authentication']['tawthiq_citations']} citations")
    lines.append(f"- Tajrih (negative evaluations): {stats['authentication']['tajrih_books']} books, {stats['authentication']['tajrih_citations']} citations")
    if stats['authentication']['unique_scholars_evaluated'] > 0:
        lines.append(f"- Unique scholars evaluated: {stats['authentication']['unique_scholars_evaluated']}")
    lines.append("")

    lines.append("### Rijal books used for authentication")
    lines.append("")
    lines.append("| # | Arabic Title | English Title | Author | d. AH | Role | Cited |")
    lines.append("|---|-------------|---------------|--------|-------|------|-------|")
    auth_sorted = sorted(layers["authentication"]["books"].values(),
                         key=lambda x: x["citation_count"], reverse=True)
    for i, b in enumerate(auth_sorted, 1):
        ar = b["book_arabic"]
        en = b.get("standard_title_english") or b.get("book_transliterated") or ""
        author = (b.get("author_arabic") or "")[:30]
        death = b.get("author_death_ah") or "?"
        role = " + ".join(c.replace("AUTHOR_", "") for c in b["contexts"])
        lines.append(f"| {i} | {ar} | {en} | {author} | {death} | {role} | {b['citation_count']} |")
    lines.append("")

    # Layer 3: Rebuttals
    lines.append("---")
    lines.append("")
    lines.append("## Layer 3: Rebuttals")
    lines.append("")
    lines.append(f"**{stats['rebuttal']['total_books']} books** cited **{stats['rebuttal']['total_citations']} times** to refute Dehlavi's counter-arguments.")
    lines.append("")
    lines.append("### Rebuttal types")
    lines.append("")
    lines.append("| Type | Citations |")
    lines.append("|------|-----------|")
    for rtype, count in sorted(stats["rebuttal"]["by_type"].items(), key=lambda x: -x[1]):
        lines.append(f"| {rtype} | {count} |")
    lines.append("")

    lines.append("### Books used in rebuttals")
    lines.append("")
    lines.append("| # | Arabic Title | Author | d. AH | Rebuttal Type | Cited |")
    lines.append("|---|-------------|--------|-------|---------------|-------|")
    reb_sorted = sorted(layers["rebuttal"]["books"].values(),
                        key=lambda x: x["citation_count"], reverse=True)
    for i, b in enumerate(reb_sorted[:50], 1):  # top 50
        ar = b["book_arabic"]
        author = (b.get("author_arabic") or "")[:30]
        death = b.get("author_death_ah") or "?"
        rtype = ", ".join(b["contexts"])
        lines.append(f"| {i} | {ar} | {author} | {death} | {rtype} | {b['citation_count']} |")

    if len(reb_sorted) > 50:
        lines.append(f"| ... | *{len(reb_sorted) - 50} more books* | | | | |")
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    print("Loading extracted data (no API calls)...")
    citations, registry, structure = load_data()
    print(f"  {len(citations['citations'])} citations, {len(registry)} books in registry")

    print("Building argument layers...")
    layers = build_argument_layers(citations, registry)

    print("Computing statistics...")
    stats = compute_stats(layers)

    # Save JSON
    output = {
        "volume": 23,
        "hadith": "Hadith al-Safinah",
        "hadith_arabic": "حديث السفينة",
        "hadith_text": "مَثَلُ أَهْلِ بَيْتِي كَمَثَلِ سَفِينَةِ نُوحٍ مَنْ رَكِبَهَا نَجَا وَمَنْ تَخَلَّفَ عَنْهَا هَلَكَ",
        "stats": stats,
        "layers": {
            "evidence": {
                "description": "Sunni books containing Hadith al-Safinah — proving tawatur",
                "total_books": stats["evidence"]["total_books"],
                "total_citations": stats["evidence"]["total_citations"],
                "books": sorted(layers["evidence"]["books"].values(),
                               key=lambda x: x["citation_count"], reverse=True),
            },
            "authentication": {
                "description": "Rijal/jarh books establishing narrator reliability",
                "total_books": stats["authentication"]["total_books"],
                "total_citations": stats["authentication"]["total_citations"],
                "books": sorted(layers["authentication"]["books"].values(),
                               key=lambda x: x["citation_count"], reverse=True),
            },
            "rebuttal": {
                "description": "Books and arguments refuting Dehlavi's counter-claims",
                "total_books": stats["rebuttal"]["total_books"],
                "total_citations": stats["rebuttal"]["total_citations"],
                "books": sorted(layers["rebuttal"]["books"].values(),
                               key=lambda x: x["citation_count"], reverse=True),
            },
        },
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved: {OUTPUT_JSON}")

    # Save markdown
    md = generate_markdown(layers, stats)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saved: {OUTPUT_MD}")

    # Summary
    print(f"\n{'='*60}")
    print(f"HADITH AL-SAFINAH — ARGUMENT STRUCTURE")
    print(f"{'='*60}")
    print(f"  Layer 1 — Evidence:        {stats['evidence']['total_books']:>3} books, {stats['evidence']['total_citations']:>3} citations")
    print(f"  Layer 2 — Authentication:  {stats['authentication']['total_books']:>3} books, {stats['authentication']['total_citations']:>3} citations")
    print(f"  Layer 3 — Rebuttals:       {stats['rebuttal']['total_books']:>3} books, {stats['rebuttal']['total_citations']:>3} citations")
    print(f"  Total unique books:        {stats['total_unique_books']:>3}")


if __name__ == "__main__":
    main()
