#!/usr/bin/env python3
"""
Classify all books cited in Abaqat Volume 23 by schema type.

Reads the extracted citations from vol23-grok.json, deduplicates to unique
books, then uses Gemini 3.1 Pro to classify each book into our schema taxonomy
(A: ScholarEntry, B: HadithEntry, C: ReferenceEntry, D: Polemical,
E: HadithCommentary, F: NotIndexed).

Usage:
  uv run --with google-genai --with python-dotenv python scripts/classify_vol23_books.py
  uv run --with google-genai --with python-dotenv python scripts/classify_vol23_books.py --dry-run
  uv run --with google-genai --with python-dotenv python scripts/classify_vol23_books.py --batch-size 25

Closes #6
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

INPUT_FILE = REPO_ROOT / "docs" / "citation-extraction" / "vol23-grok.json"
OUTPUT_JSON = REPO_ROOT / "docs" / "citation-extraction" / "vol23-book-registry.json"
OUTPUT_MD = REPO_ROOT / "docs" / "citation-extraction" / "vol23-book-registry.md"
HAWRAMANI_CATS = REPO_ROOT / "data" / "indexes" / "hawramani-categories.json"

MODEL = "gemini-3.1-pro-preview"

SYSTEM_PROMPT = """You are an expert in classical Islamic bibliography (فهارس الكتب) with deep
knowledge of Arabic book genres across all Islamic disciplines: hadith, rijal,
tafsir, fiqh, kalam, adab, tarikh, and Sunni-Shia polemical literature.

You classify books into their scholarly genre based on the book title, author,
author's era, and how the book is used in scholarly discourse."""

CLASSIFICATION_PROMPT = """Classify each book below into one of these schemas:

SCHEMA A — ScholarEntry (books organized around individual scholars/narrators):
  - jarh_tadil: Narrator criticism — evaluates hadith transmitters (e.g., Tahdhib al-Tahdhib, Mizan al-I'tidal, al-Jarh wa al-Ta'dil)
  - biographical: General biographical dictionaries organized by person (e.g., Wafayat al-A'yan, Siyar A'lam al-Nubala, al-Wafi bi al-Wafayat)
  - tabaqat: Class/generation-based biographical works (e.g., Tabaqat Ibn Sa'd, Tabaqat al-Shafi'iyya, Tadhkirat al-Huffaz)
  - tarikh: City/regional histories organized by person with hadith narrations (e.g., Tarikh Baghdad, Tarikh Dimashq)
  - chronological: Year-by-year annals with death notices (e.g., al-'Ibar, Mir'at al-Janan)

SCHEMA B — HadithEntry (primary hadith collections):
  - sahih: Collections filtered for authenticity (Sahih al-Bukhari, Sahih Muslim)
  - sunan: Hadith organized by fiqh chapters with grading (Sunan al-Tirmidhi, Sunan Abi Dawud, etc.)
  - musnad: Hadith organized by companion (Musnad Ahmad, Musnad al-Bazzar, etc.)
  - mustadrak: Supplements to existing collections (al-Mustadrak of al-Hakim)
  - mujam: Hadith organized by teacher/companion name (al-Mu'jam al-Kabir/Awsat/Saghir)
  - musannaf: Early classified compilations including athar (Musannaf Ibn Abi Shayba, Musannaf Abd al-Razzaq)
  - juz: Single-topic hadith monographs (Juz of so-and-so, Fada'il compilations that are primarily hadith with chains)

SCHEMA C — ReferenceEntry (meta-reference works):
  - bibliography: Indexes of books and authors (Kashf al-Zunun, Kashf al-Hujub, al-Dhariah)
  - genealogical: Nisba/lineage dictionaries (al-Ansab)

SCHEMA D — Polemical:
  - sunni_polemical: Sunni works attacking Shia positions (Minhaj al-Sunnah, Tuhfat al-Ithna Ashariyya, etc.)
  - shia_polemical: Shia works defending or attacking (Abaqat al-Anwar itself, Minhaj al-Karama, etc.)

SCHEMA E — HadithCommentary (commentaries on hadith collections):
  - sharh: Full commentaries (Fath al-Bari, al-Minhaj Sharh Sahih Muslim, Irshad al-Sari)
  - hashiyah: Marginal glosses on another commentary
  - takhrij: Chain verification works (Takhrij Ahadith al-Kashshaf, etc.)
  - fiqhi: Legal derivation commentaries

SCHEMA F — NotIndexed (books outside our indexing scope):
  - tafsir: Quranic commentaries
  - kalam: Theological/creedal works
  - fiqh: Legal theory and rulings
  - adab: Literary/encyclopedic works
  - lughah: Lexicons, grammar, and language
  - tarikh_general: General history not organized by person
  - manaqib: Virtue compilations (fada'il books that are NOT pure hadith collections — thematic compilations without systematic isnad)
  - sirah: Prophetic biography
  - shia_doctrine: Shia doctrinal/theological works
  - unknown: Cannot be identified

CLASSIFICATION RULES:
1. The book's GENRE determines the schema, NOT how it is cited. A tafsir cited as HADITH_SOURCE is still a tafsir (Schema F/tafsir).
2. Manaqib/fada'il books: if primarily HADITH with chains (like Fada'il al-Sahaba of Ahmad), classify as B/musnad or B/juz. If thematic compilations without systematic isnad (like Yanabi' al-Mawaddah), classify as F/manaqib.
3. Sharh works ON hadith books → Schema E. Sharh works on fiqh/kalam/other → Schema F with appropriate sub-type.
4. If a book title is generic (e.g., "المسند", "الصحيح"), use the author to disambiguate.
5. Mark confidence "low" for books you are not certain about.

Return a JSON array. For each book, return:
{
  "book_arabic": "exact title from input",
  "schema": "A" | "B" | "C" | "D" | "E" | "F",
  "book_type": "sub-type from schema above",
  "confidence": "high" | "medium" | "low",
  "reasoning": "1 sentence why",
  "known_book": true | false,
  "standard_title_arabic": "canonical Arabic title if different from input",
  "standard_title_english": "standard English/transliterated title"
}

BOOKS TO CLASSIFY:
"""


def load_and_deduplicate(input_file: Path) -> list[dict]:
    """Load citations and deduplicate to unique books."""
    with open(input_file) as f:
        data = json.load(f)

    books = {}
    for c in data["citations"]:
        # Composite key: title + death year (handles "المسند" by different authors)
        key = (c["book_arabic"], c.get("author_death_ah") or "unknown")
        if key not in books:
            books[key] = {
                "book_arabic": c["book_arabic"],
                "book_transliterated": c.get("book_transliterated", ""),
                "author_arabic": c.get("author_arabic", ""),
                "author_transliterated": c.get("author_transliterated", ""),
                "author_death_ah": c.get("author_death_ah"),
                "citation_contexts": set(),
                "citation_count": 0,
            }
        books[key]["citation_contexts"].add(c["citation_context"])
        books[key]["citation_count"] += 1

    # Convert sets to sorted lists
    result = []
    for b in books.values():
        b["citation_contexts"] = sorted(b["citation_contexts"])
        result.append(b)

    return sorted(result, key=lambda x: x["citation_count"], reverse=True)


def load_existing_results(output_file: Path) -> dict:
    """Load already-classified books for resume capability."""
    if not output_file.exists():
        return {}
    with open(output_file) as f:
        data = json.load(f)
    return {b["book_arabic"]: b for b in data.get("books", [])}


def classify_batch(client, books: list[dict], batch_num: int, total_batches: int) -> list[dict]:
    """Send a batch of books to Gemini for classification."""
    from google.genai import types

    # Build the book list for the prompt
    book_list = []
    for b in books:
        entry = {
            "book_arabic": b["book_arabic"],
            "book_transliterated": b["book_transliterated"],
            "author_arabic": b["author_arabic"],
            "author_death_ah": b["author_death_ah"],
            "citation_contexts": b["citation_contexts"],
        }
        book_list.append(entry)

    prompt = CLASSIFICATION_PROMPT + json.dumps(book_list, ensure_ascii=False, indent=2)

    print(f"  Batch {batch_num}/{total_batches}: {len(books)} books...")
    t0 = time.time()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=16384,
        ),
    )

    elapsed = time.time() - t0
    text = (response.text or "").strip()

    try:
        results = json.loads(text)
    except json.JSONDecodeError:
        print(f"  WARNING: Failed to parse JSON response for batch {batch_num}")
        print(f"  Raw response (first 500 chars): {text[:500]}")
        return []

    print(f"  Got {len(results)} classifications in {elapsed:.1f}s")
    return results


def cross_reference_hawramani(books: list[dict], hawramani_file: Path) -> None:
    """Add hawramani category matches to classified books."""
    if not hawramani_file.exists():
        return

    with open(hawramani_file) as f:
        categories = json.load(f)

    cat_names = {c["id"]: c["name"] for c in categories}

    # Simple matching: check if any category name contains the book's Arabic title
    for book in books:
        book["hawramani_match"] = None
        title = book.get("standard_title_arabic") or book["book_arabic"]
        for cat in categories:
            # Check if the Arabic part of the category name matches
            cat_name = cat["name"]
            if title in cat_name or any(
                part.strip() in cat_name
                for part in title.split()
                if len(part.strip()) > 3
            ):
                book["hawramani_match"] = {
                    "category_id": cat["id"],
                    "category_name": cat_name,
                    "entry_count": cat["count"],
                }
                break


def generate_markdown(books: list[dict], metadata: dict) -> str:
    """Generate scholar-reviewable markdown tables."""
    lines = [
        "# Vol 23 Book Registry — Schema Classification",
        "",
        f"**Total books:** {metadata['total_unique_books']}",
        f"**Classified by:** {metadata['classified_by']}",
        f"**Date:** {metadata['classified_at'][:10]}",
        "",
        "## Schema Distribution",
        "",
        "| Schema | Count | Description |",
        "|--------|-------|-------------|",
    ]

    schema_labels = {
        "A": "ScholarEntry (person-centric)",
        "B": "HadithEntry (hadith collections)",
        "C": "ReferenceEntry (bibliographies)",
        "D": "Polemical",
        "E": "HadithCommentary",
        "F": "NotIndexed",
    }

    dist = metadata["schema_distribution"]
    for schema in ["A", "B", "C", "D", "E", "F"]:
        count = dist.get(schema, 0)
        lines.append(f"| {schema} | {count} | {schema_labels.get(schema, '')} |")

    # Group books by schema
    by_schema = {}
    for b in books:
        s = b.get("schema", "F")
        by_schema.setdefault(s, []).append(b)

    for schema in ["A", "B", "C", "D", "E", "F"]:
        if schema not in by_schema:
            continue
        schema_books = sorted(by_schema[schema], key=lambda x: x.get("book_type", ""))
        lines.extend([
            "",
            f"---",
            "",
            f"## Schema {schema}: {schema_labels.get(schema, '')}",
            "",
            "| Arabic Title | English Title | Author | d. AH | Sub-type | Conf. | Citations |",
            "|-------------|---------------|--------|-------|----------|-------|-----------|",
        ])
        for b in schema_books:
            std_ar = b.get("standard_title_arabic") or b["book_arabic"]
            std_en = b.get("standard_title_english") or b.get("book_transliterated") or ""
            author = (b.get("author_arabic") or "")[:30]
            death = b.get("author_death_ah") or "?"
            btype = b.get("book_type", "?")
            conf = b.get("confidence", "?")
            count = b.get("citation_count", 0)
            lines.append(f"| {std_ar} | {std_en} | {author} | {death} | {btype} | {conf} | {count} |")

    # Needs Review section
    needs_review = [b for b in books if b.get("confidence") == "low" or b.get("known_book") is False]
    if needs_review:
        lines.extend([
            "",
            "---",
            "",
            "## Needs Scholar Review",
            "",
            "These books have low confidence classification or are unrecognized:",
            "",
            "| Arabic Title | Author | d. AH | Assigned Schema | Reasoning |",
            "|-------------|--------|-------|-----------------|-----------|",
        ])
        for b in needs_review:
            lines.append(
                f"| {b['book_arabic']} | {(b.get('author_arabic') or '')[:30]} | "
                f"{b.get('author_death_ah') or '?'} | {b.get('schema', '?')}/{b.get('book_type', '?')} | "
                f"{b.get('reasoning') or ''} |"
            )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Classify Vol 23 cited books by schema type")
    parser.add_argument("--dry-run", action="store_true", help="Print first batch prompt without calling API")
    parser.add_argument("--batch-size", type=int, default=30, help="Books per Gemini batch (default: 30)")
    args = parser.parse_args()

    if not INPUT_FILE.exists():
        print(f"Error: Input file not found: {INPUT_FILE}")
        sys.exit(1)

    # Step 1: Deduplicate
    print("Loading and deduplicating citations...")
    books = load_and_deduplicate(INPUT_FILE)
    print(f"  {len(books)} unique books from Vol 23")

    # Step 2: Check for existing results (resume)
    existing = load_existing_results(OUTPUT_JSON)
    to_classify = [b for b in books if b["book_arabic"] not in existing]
    print(f"  {len(existing)} already classified, {len(to_classify)} remaining")

    if args.dry_run:
        # Show first batch prompt
        batch = to_classify[: args.batch_size]
        book_list = [
            {
                "book_arabic": b["book_arabic"],
                "book_transliterated": b["book_transliterated"],
                "author_arabic": b["author_arabic"],
                "author_death_ah": b["author_death_ah"],
                "citation_contexts": b["citation_contexts"],
            }
            for b in batch
        ]
        print("\n=== DRY RUN — First batch prompt ===\n")
        print(SYSTEM_PROMPT)
        print("\n---\n")
        print(CLASSIFICATION_PROMPT + json.dumps(book_list, ensure_ascii=False, indent=2))
        print(f"\n=== Would send {len(to_classify)} books in {(len(to_classify) + args.batch_size - 1) // args.batch_size} batches ===")
        return

    if not to_classify:
        print("All books already classified. Regenerating outputs...")
    else:
        # Step 3: Classify via Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not set")
            sys.exit(1)

        from google import genai

        client = genai.Client(api_key=api_key)

        batches = [to_classify[i : i + args.batch_size] for i in range(0, len(to_classify), args.batch_size)]
        print(f"\nClassifying {len(to_classify)} books in {len(batches)} batches...")

        for i, batch in enumerate(batches, 1):
            results = classify_batch(client, batch, i, len(batches))

            # Merge results with input data
            results_by_title = {r["book_arabic"]: r for r in results}
            for b in batch:
                classified = results_by_title.get(b["book_arabic"], {})
                merged = {**b, **classified}
                existing[b["book_arabic"]] = merged

            # Save after each batch (resume capability)
            _save_json(books, existing)
            print(f"  Saved progress ({len(existing)} total)")

            if i < len(batches):
                time.sleep(2)  # Rate limiting

    # Step 4: Build final output
    final_books = []
    for b in books:
        if b["book_arabic"] in existing:
            final_books.append(existing[b["book_arabic"]])
        else:
            final_books.append({**b, "schema": "F", "book_type": "unknown", "confidence": "low"})

    # Step 5: Hawramani cross-reference
    print("\nCross-referencing with hawramani categories...")
    cross_reference_hawramani(final_books, HAWRAMANI_CATS)

    # Step 6: Save outputs
    metadata = {
        "source": str(INPUT_FILE.relative_to(REPO_ROOT)),
        "total_unique_books": len(final_books),
        "classified_by": MODEL,
        "classified_at": datetime.now(timezone.utc).isoformat(),
        "schema_distribution": {},
    }
    for b in final_books:
        s = b.get("schema", "F")
        metadata["schema_distribution"][s] = metadata["schema_distribution"].get(s, 0) + 1

    output = {"metadata": metadata, "books": final_books}
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {OUTPUT_JSON} ({len(final_books)} books)")

    # Generate markdown
    md = generate_markdown(final_books, metadata)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saved: {OUTPUT_MD}")

    # Summary
    print(f"\n=== Classification Summary ===")
    for schema in sorted(metadata["schema_distribution"]):
        count = metadata["schema_distribution"][schema]
        print(f"  Schema {schema}: {count} books")

    low_conf = sum(1 for b in final_books if b.get("confidence") == "low")
    unknown = sum(1 for b in final_books if b.get("known_book") is False)
    print(f"\n  Needs review: {low_conf} low confidence, {unknown} unknown books")


def _save_json(all_books: list[dict], classified: dict) -> None:
    """Save intermediate results."""
    final = []
    for b in all_books:
        if b["book_arabic"] in classified:
            final.append(classified[b["book_arabic"]])
        else:
            final.append(b)

    output = {
        "metadata": {
            "source": str(INPUT_FILE.relative_to(REPO_ROOT)),
            "total_unique_books": len(all_books),
            "classified_by": MODEL,
            "classified_at": datetime.now(timezone.utc).isoformat(),
            "partial": True,
        },
        "books": final,
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
