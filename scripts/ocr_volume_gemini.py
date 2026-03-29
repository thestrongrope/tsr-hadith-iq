#!/usr/bin/env python3
"""
OCR Abaqat volumes using Gemini 3.1 Pro — one-time extraction.

Sends each page as an image to Gemini, gets clean Arabic/Farsi text back.
Saves per-page JSON (resumable) and a concatenated full text file.

Usage:
  uv run --with google-genai --with pymupdf --with python-dotenv python scripts/ocr_volume_gemini.py --volume 23
  uv run --with google-genai --with pymupdf --with python-dotenv python scripts/ocr_volume_gemini.py --volume 23 --start-page 50
  uv run --with google-genai --with pymupdf --with python-dotenv python scripts/ocr_volume_gemini.py --volume 23 --dry-run

Output:
  reference/books/abaqat/ocr/vol23-gemini-pages.json  — per-page text with metadata
  reference/books/abaqat/ocr/vol23-gemini-full.txt    — concatenated clean text
"""

import json
import os
import sys
import time
import base64
import argparse
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

BOOKS_DIR = REPO_ROOT / "reference" / "books"
# Default to abaqat; can be overridden for other books
PDF_DIR = BOOKS_DIR / "abaqat" / "pdf"
OUTPUT_DIR = BOOKS_DIR / "abaqat" / "ocr"

MODEL = "gemini-3.1-flash-lite-preview"

OCR_PROMPT = """Extract ALL text from this scanned page of an Arabic/Farsi Islamic scholarly book (Abaqat al-Anwar).

Rules:
- Extract every word exactly as printed — Arabic text, Farsi text, footnotes, page numbers, headers
- Preserve line breaks where they appear in the original
- For Arabic quotations embedded in Farsi text, extract both accurately
- Include diacritics (tashkil) if visible
- Include footnote numbers and footnote text at the bottom of the page
- If a word is unclear, give your best reading — do NOT skip it
- Output ONLY the extracted text, no commentary or formatting markup
- If the page is blank or contains only a page number, output just that"""


def extract_page_image(pdf_path: str, page_num: int) -> bytes:
    """Extract a page as PNG image bytes."""
    import fitz
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    # Render at 200 DPI for good OCR quality without excessive size
    pix = page.get_pixmap(dpi=200)
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


def ocr_page(client, img_bytes: bytes, page_num: int) -> str:
    """Send page image to Gemini and get text back."""
    from google.genai import types

    img_b64 = base64.b64encode(img_bytes).decode()

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                parts=[
                    types.Part(text=OCR_PROMPT),
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/png",
                            data=img_bytes,
                        )
                    ),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=4096,
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )

    return (response.text or "").strip()


def load_existing(output_file: Path) -> dict:
    """Load already-OCR'd pages for resume."""
    if not output_file.exists():
        return {"pages": {}, "metadata": {}}
    with open(output_file) as f:
        return json.load(f)


def save_progress(data: dict, output_file: Path):
    """Save current state."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_full_text(data: dict, output_file: Path):
    """Concatenate all pages into a single text file."""
    pages = data["pages"]
    with open(output_file, "w", encoding="utf-8") as f:
        for page_num in sorted(pages.keys(), key=int):
            page = pages[page_num]
            f.write(f"--- PAGE {page_num} ---\n")
            f.write(page["text"])
            f.write("\n\n")


def main():
    parser = argparse.ArgumentParser(description="OCR Abaqat volume with Gemini")
    parser.add_argument("--volume", type=int, required=True, help="Volume number (e.g., 23)")
    parser.add_argument("--start-page", type=int, default=0, help="Start from this page (0-indexed)")
    parser.add_argument("--end-page", type=int, default=None, help="End at this page (exclusive)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without calling API")
    parser.add_argument("--batch-delay", type=float, default=1.0, help="Seconds between pages")
    args = parser.parse_args()

    # Find PDF
    pdf_name = f"abaghaat al'anwaar {args.volume}.pdf"
    pdf_path = PDF_DIR / pdf_name
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    # Get page count
    import fitz
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pages_file = OUTPUT_DIR / f"vol{args.volume:02d}-pages.json"
    text_file = OUTPUT_DIR / f"vol{args.volume:02d}-full.txt"

    # Load existing progress
    data = load_existing(pages_file)
    already_done = set(data["pages"].keys())

    end_page = args.end_page or total_pages
    pages_to_do = [
        p for p in range(args.start_page, end_page)
        if str(p) not in already_done
    ]

    print(f"Volume {args.volume}: {total_pages} pages, {len(already_done)} already OCR'd, {len(pages_to_do)} remaining")

    if args.dry_run:
        print(f"\nDry run — would OCR pages {pages_to_do[:5]}... to {pages_to_do[-1:]}")
        print(f"Estimated cost: ~${len(pages_to_do) * 0.0007:.2f}")
        print(f"Estimated time: ~{len(pages_to_do) * 2:.0f}s ({len(pages_to_do) * 2 / 60:.1f} min)")
        return

    if not pages_to_do:
        print("All pages already OCR'd. Regenerating full text...")
        save_full_text(data, text_file)
        print(f"Saved: {text_file}")
        return

    # Initialize Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    # Update metadata
    data["metadata"] = {
        "volume": args.volume,
        "pdf": str(pdf_path),
        "total_pages": total_pages,
        "model": MODEL,
    }

    print(f"\nOCR'ing {len(pages_to_do)} pages with {MODEL}...")
    t0 = time.time()
    errors = []

    for i, page_num in enumerate(pages_to_do):
        try:
            img_bytes = extract_page_image(str(pdf_path), page_num)
            text = ocr_page(client, img_bytes, page_num)

            data["pages"][str(page_num)] = {
                "page": page_num,
                "text": text,
                "chars": len(text),
            }

            if (i + 1) % 10 == 0 or i == 0:
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed * 60
                remaining = (len(pages_to_do) - i - 1) / (rate / 60) if rate > 0 else 0
                print(f"  Page {page_num} ({i+1}/{len(pages_to_do)}) — {len(text)} chars — {rate:.0f} pages/min — ~{remaining:.0f}s remaining")

                # Save every 10 pages
                save_progress(data, pages_file)

        except Exception as e:
            print(f"  ERROR page {page_num}: {e}")
            errors.append({"page": page_num, "error": str(e)})

        time.sleep(args.batch_delay)

    # Final save
    save_progress(data, pages_file)
    save_full_text(data, text_file)

    elapsed = time.time() - t0
    total_chars = sum(p["chars"] for p in data["pages"].values())

    print(f"\n{'='*60}")
    print(f"OCR COMPLETE — Volume {args.volume}")
    print(f"{'='*60}")
    print(f"  Pages OCR'd: {len(data['pages'])}/{total_pages}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Errors: {len(errors)}")
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Saved: {pages_file}")
    print(f"  Saved: {text_file}")

    if errors:
        print(f"\n  Failed pages: {[e['page'] for e in errors]}")
        print("  Re-run the script to retry failed pages.")


if __name__ == "__main__":
    main()
