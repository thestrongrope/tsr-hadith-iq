#!/usr/bin/env python3
"""
Split oversized PDFs and extract index pages from downloaded rijal books.

Usage:
  uv run --with pymupdf python scripts/split_and_index_books.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = REPO_ROOT / "data" / "books"

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: pymupdf not installed. Run: uv run --with pymupdf python scripts/split_and_index_books.py")
    sys.exit(1)


def get_page_count(pdf_path):
    """Get page count of a PDF."""
    doc = fitz.open(str(pdf_path))
    count = len(doc)
    doc.close()
    return count


def split_pdf(pdf_path, splits, output_dir):
    """Split a PDF into chunks based on page ranges."""
    doc = fitz.open(str(pdf_path))
    total = len(doc)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, start, end in splits:
        end = min(end, total)
        if start >= total:
            print(f"    SKIP {name}: start page {start} > total {total}")
            continue
        out_doc = fitz.open()
        out_doc.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
        out_path = output_dir / f"{name}.pdf"
        out_doc.save(str(out_path))
        out_doc.close()
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"    ✅ {name}.pdf: pages {start}-{end} ({end - start + 1} pages, {size_mb:.1f} MB)")

    doc.close()


def validate_book(book_dir):
    """Validate a book's PDFs and report page counts."""
    meta_path = book_dir / "metadata.json"
    if not meta_path.exists():
        return None

    with open(meta_path) as f:
        meta = json.load(f)

    pdf_dir = book_dir / "pdf"
    if not pdf_dir.exists():
        return meta

    pdfs = sorted(pdf_dir.glob("*.pdf"))
    total_pages = 0
    pdf_info = []

    for pdf in pdfs:
        try:
            pages = get_page_count(pdf)
            size_mb = pdf.stat().st_size / (1024 * 1024)
            total_pages += pages
            pdf_info.append({
                "file": pdf.name,
                "pages": pages,
                "size_mb": round(size_mb, 1),
                "readable": size_mb < 100,
            })
        except Exception as e:
            pdf_info.append({"file": pdf.name, "error": str(e)})

    meta["validation"] = {
        "total_pdfs": len(pdfs),
        "total_pages": total_pages,
        "pdf_details": pdf_info,
        "all_readable": all(p.get("readable", False) for p in pdf_info),
    }

    with open(meta_path, "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return meta


def main():
    print("=" * 60)
    print("Validating and indexing rijal books")
    print("=" * 60)

    # Step 1: Validate all books
    print("\n--- Step 1: Validate all books ---\n")
    for book_dir in sorted(BOOKS_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        name = book_dir.name
        meta = validate_book(book_dir)
        if not meta:
            print(f"  ⚠️  {name}: no metadata.json")
            continue

        v = meta.get("validation", {})
        total_pages = v.get("total_pages", 0)
        all_readable = v.get("all_readable", True)
        status = "✅" if all_readable else "⚠️ HAS OVERSIZED FILES"
        print(f"  {status} {name}: {v.get('total_pdfs', 0)} PDFs, {total_pages} pages")

        for pdf in v.get("pdf_details", []):
            if not pdf.get("readable", True):
                print(f"      ⚠️  {pdf['file']}: {pdf['pages']} pages, {pdf['size_mb']} MB — NEEDS SPLITTING")

    # Step 2: Split oversized Siyar A'lam al-Nubala
    print("\n--- Step 2: Split Siyar A'lam al-Nubala ---\n")
    siyar_dir = BOOKS_DIR / "siyar-alam-al-nubala"
    siyar_pdf = siyar_dir / "pdf" / "105924.pdf"

    if siyar_pdf.exists():
        splits_dir = siyar_dir / "pdf" / "split"

        if (splits_dir / "vol_01_generation_01-05.pdf").exists():
            print("  Already split — skipping")
        else:
            # Based on the 28-volume structure of Siyar
            # Each volume is roughly 160-170 pages
            # Total: 4683 pages, content ends ~4303 (indexes start)
            splits = [
                ("vol_01_generation_01-05", 1, 500),
                ("vol_02_generation_06-10", 501, 1000),
                ("vol_03_generation_11-15", 1001, 1500),
                ("vol_04_generation_16-20", 1501, 2000),
                ("vol_05_generation_21-25", 2001, 2500),
                ("vol_06_generation_26-30", 2501, 3000),
                ("vol_07_generation_31-35", 3001, 3500),
                ("vol_08_generation_36-40", 3501, 4000),
                ("vol_09_remaining_content", 4001, 4302),
                ("index_quranic_verses", 4303, 4322),
                ("index_prophetic_hadiths", 4323, 4388),
                ("index_table_of_contents", 4389, 4422),
                ("index_alphabetical_names", 4423, 4683),
            ]

            print(f"  Splitting {siyar_pdf.name} ({get_page_count(siyar_pdf)} pages)...")
            split_pdf(siyar_pdf, splits, splits_dir)

            # Update metadata
            with open(siyar_dir / "metadata.json") as f:
                meta = json.load(f)
            meta["split_files"] = {s[0]: {"pages": f"{s[1]}-{s[2]}"} for s in splits}
            meta["note"] = "Original 132MB PDF split into manageable chunks. Use split/ directory for verification."
            with open(siyar_dir / "metadata.json", "w") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
    else:
        print("  Siyar PDF not found — skipping")

    # Step 3: Summary
    print("\n--- Summary ---\n")
    total_books = 0
    total_pages = 0
    total_verified = 0
    for book_dir in sorted(BOOKS_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        meta_path = book_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            total_books += 1
            total_pages += meta.get("validation", {}).get("total_pages", 0)
            if meta.get("verified_citations"):
                total_verified += 1

    print(f"  Books downloaded: {total_books}")
    print(f"  Total pages: {total_pages:,}")
    print(f"  Books with verified citations: {total_verified}")
    print(f"  All files readable: check validation in each metadata.json")


if __name__ == "__main__":
    main()
