#!/usr/bin/env python3
"""
Download rijal source books from archive.org (PDF + text).
Uses the archive.org metadata API to find all available files,
then downloads PDF and djvu.txt for each book.

Usage:
  uv run python scripts/download_rijal_books.py [--tier 1] [--book "Tahdhib al-Tahdhib"] [--dry-run]
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import time
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "docs" / "source-books-archive-org.json"
DOWNLOAD_DIR = REPO_ROOT / "reference" / "rijal-books"

# Tier 1: cited in 8+ volumes
TIER1 = [
    'Tahdhib al-Tahdhib', "Mizan al-I'tidal", 'Tadhkirat al-Huffaz',
    "Wafayat al-A'yan", "Mir'at al-Janan", "Al-'Ibar",
    'Tabaqat al-Huffaz', "Tabaqat al-Shafi'iyya al-Kubra",
    "Siyar A'lam al-Nubala", 'Tarikh Baghdad', 'Tahdhib al-Kamal',
]

# Tier 2: cited in 4-7 volumes
TIER2 = [
    'Taqrib al-Tahdhib', 'Sahih Muslim', 'Lisan al-Mizan',
    "Al-Wafi bi al-Wafayat", "Al-Ansab", "Al-Durar al-Kaminah",
    'Husn al-Muhadara', "Bughyat al-Wu'at", "Fawat al-Wafayat",
    "Al-Daw' al-Lami'", "Khulasat al-Athar",
]


def get_archive_files(identifier):
    """Get file listing from archive.org metadata API."""
    url = f"https://archive.org/metadata/{identifier}/files"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get('result', [])
    except Exception as e:
        print(f"    Error fetching file list: {e}")
        return []


def download_file(url, dest_path, desc=""):
    """Download a file with progress."""
    if dest_path.exists():
        size = dest_path.stat().st_size
        if size > 1000:  # Skip if already downloaded and non-trivial
            print(f"    SKIP (exists, {size/1024/1024:.1f} MB): {dest_path.name}")
            return True

    print(f"    Downloading {desc}: {dest_path.name}...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=300) as resp:
            total = int(resp.headers.get('Content-Length', 0))
            data = resp.read()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, 'wb') as f:
                f.write(data)
            size = len(data) / (1024 * 1024)
            print(f"{size:.1f} MB")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def download_book(book_name, book_data, book_dir, dry_run=False):
    """Download all files for a book from archive.org."""
    identifier = book_data.get('identifier')
    if not identifier:
        print(f"  No identifier for {book_name}")
        return False

    print(f"\n📚 {book_name}")
    print(f"   archive.org/{identifier}")

    # Get file listing
    files = get_archive_files(identifier)
    if not files:
        print(f"   No files found!")
        return False

    # Categorize files
    pdfs = sorted([f for f in files if f.get('name', '').lower().endswith('.pdf')],
                  key=lambda f: f.get('name', ''))
    texts = sorted([f for f in files if f.get('name', '').lower().endswith('_djvu.txt') or
                    (f.get('name', '').lower().endswith('.txt') and 'djvu' in f.get('name', '').lower())],
                   key=lambda f: f.get('name', ''))
    zips = sorted([f for f in files if f.get('name', '').lower().endswith('.zip')],
                  key=lambda f: f.get('name', ''))
    # Also look for plain text if no djvu text
    if not texts:
        texts = sorted([f for f in files if f.get('name', '').lower().endswith('.txt')
                        and not f.get('name', '').startswith('__')],
                       key=lambda f: f.get('name', ''))

    total_pdf_size = sum(int(f.get('size', 0)) for f in pdfs) / (1024 * 1024)
    total_txt_size = sum(int(f.get('size', 0)) for f in texts) / (1024 * 1024)
    total_zip_size = sum(int(f.get('size', 0)) for f in zips) / (1024 * 1024)

    # If no PDFs but has ZIPs, the book is bundled
    is_bundled = len(pdfs) == 0 and len(zips) > 0

    print(f"   PDFs: {len(pdfs)} files ({total_pdf_size:.0f} MB)")
    print(f"   Texts: {len(texts)} files ({total_txt_size:.0f} MB)")
    if zips:
        print(f"   ZIPs: {len(zips)} files ({total_zip_size:.0f} MB){' ← bundled (PDFs inside)' if is_bundled else ''}")

    if dry_run:
        if pdfs:
            for p in pdfs[:5]:
                sz = int(p.get('size', 0)) / (1024 * 1024)
                print(f"     PDF: {p['name'][:60]} ({sz:.1f} MB)")
            if len(pdfs) > 5:
                print(f"     ... +{len(pdfs)-5} more")
        for t in texts[:3]:
            sz = int(t.get('size', 0)) / (1024 * 1024)
            print(f"     TXT: {t['name'][:60]} ({sz:.1f} MB)")
        if is_bundled:
            for z in zips:
                sz = int(z.get('size', 0)) / (1024 * 1024)
                print(f"     ZIP: {z['name'][:60]} ({sz:.1f} MB)")
        return True

    # Download PDFs (individual files)
    if pdfs:
        dest = book_dir / "pdf"
        dest.mkdir(parents=True, exist_ok=True)
        for f in pdfs:
            fname = f['name']
            url = f"https://archive.org/download/{identifier}/{urllib.parse.quote(fname)}"
            download_file(url, dest / fname, "PDF")
            time.sleep(0.5)

    # Download ZIPs (bundled books)
    if zips:
        dest = book_dir / "bundles"
        dest.mkdir(parents=True, exist_ok=True)
        for f in zips:
            fname = f['name']
            url = f"https://archive.org/download/{identifier}/{urllib.parse.quote(fname)}"
            download_file(url, dest / fname, "ZIP")
            time.sleep(0.5)

    # Download text files
    if texts:
        dest = book_dir / "text"
        dest.mkdir(parents=True, exist_ok=True)
        for f in texts:
            fname = f['name']
            url = f"https://archive.org/download/{identifier}/{urllib.parse.quote(fname)}"
            download_file(url, dest / fname, "TXT")
            time.sleep(0.5)

    # Save metadata
    meta = {
        "book_name": book_name,
        "identifier": identifier,
        "url": f"https://archive.org/details/{identifier}",
        "pdfs": [f['name'] for f in pdfs],
        "texts": [f['name'] for f in texts],
        "zips": [f['name'] for f in zips],
        "bundled": is_bundled,
        "total_pdf_mb": round(total_pdf_size, 1),
        "total_txt_mb": round(total_txt_size, 1),
        "total_zip_mb": round(total_zip_size, 1),
    }
    with open(book_dir / "metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, ensure_ascii=False, indent=2)

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", type=int, choices=[1, 2], help="Download tier 1 or 2")
    parser.add_argument("--book", type=str, help="Download a specific book by name")
    parser.add_argument("--all", action="store_true", help="Download all books")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded")
    args = parser.parse_args()

    with open(CATALOG) as f:
        catalog = json.load(f)

    # Determine which books to download
    if args.book:
        books_to_download = [args.book]
    elif args.tier == 1:
        books_to_download = TIER1
    elif args.tier == 2:
        books_to_download = TIER2
    elif args.all:
        books_to_download = [k for k, v in catalog.items() if v.get('found') and v.get('identifier')]
    else:
        print("Specify --tier 1, --tier 2, --book 'Name', or --all")
        sys.exit(1)

    print(f"{'DRY RUN: ' if args.dry_run else ''}Downloading {len(books_to_download)} books")
    print(f"Destination: {DOWNLOAD_DIR}")

    success = 0
    failed = []
    for book_name in books_to_download:
        if book_name not in catalog:
            print(f"\n⚠️  {book_name} not in catalog")
            failed.append(book_name)
            continue

        data = catalog[book_name]
        if not data.get('found') or not data.get('identifier'):
            print(f"\n⚠️  {book_name} has no archive.org identifier")
            failed.append(book_name)
            continue

        # Clean book name for directory
        dir_name = book_name.replace("'", "").replace('"', '').replace('/', '-')
        book_dir = DOWNLOAD_DIR / dir_name

        if download_book(book_name, data, book_dir, args.dry_run):
            success += 1
        else:
            failed.append(book_name)

    print(f"\n{'='*60}")
    print(f"{'DRY RUN ' if args.dry_run else ''}Complete: {success}/{len(books_to_download)} books")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
