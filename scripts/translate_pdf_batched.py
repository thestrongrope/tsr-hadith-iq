#!/usr/bin/env python3
"""
translate_pdf_batched.py — PDF OCR + Translation Pipeline

Translates PDF books page-by-page using Google Gemini models.
Splits the PDF into mini-PDFs (batches) and sends them directly to
Gemini 3 Flash — no image conversion needed.

Failed pages are automatically retried through a fallback model chain:
  1. gemini-3-flash-preview        (batched PDF, primary)
  2. gemini-3.1-flash-image-preview (per-page image, catches safety-filtered pages)
  3. gemini-2.5-flash               (per-page image, final fallback)

Output: per-page JSON files with original text + English translation.

Usage:
    uv run --with google-genai --with python-dotenv --with PyMuPDF \\
        python scripts/translate_pdf_batched.py \\
        --pdf path/to/book.pdf \\
        --jsondir path/to/output/json \\
        --guidelines path/to/guidelines.txt \\
        --start-page 7 --batch-size 10

The --guidelines file should contain the translation prompt (book context,
translation rules, honorifics, etc.). If omitted, a default set of
guidelines for Farsi/Arabic Islamic texts is used.

JSON output format per page:
    {
      "page": 42,
      "source": "gemini_pdf_batched:gemini-3-flash-preview",
      "paragraphs": [
        {"text": "<original Farsi/Arabic>", "translation": "<English>"},
        ...
      ]
    }
"""

import argparse
import io
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit(
        "Error: google-genai package not installed.\n"
        "  uv run --with google-genai --with python-dotenv --with PyMuPDF python translate_pdf_batched.py ..."
    )

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit(
        "Error: PyMuPDF not installed.\n"
        "  uv run --with google-genai --with python-dotenv --with PyMuPDF python translate_pdf_batched.py ..."
    )

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ---------------------------------------------------------------------------
# Fallback model chain — ordered by preference
# ---------------------------------------------------------------------------
FALLBACK_MODELS = [
    "models/gemini-3.1-flash-image-preview",  # best at catching safety-filtered pages
    "models/gemini-2.5-flash",                 # stable, proven
]

DEFAULT_GUIDELINES = """\
You are an expert translator specializing in Shia Islamic traditions, tasked \
with translating Farsi/Persian texts (with Arabic quotations) into English \
with precision and respect for Shia perspectives.

Translation rules:
1. Formatting: Only apply bold or italics if they appear in the original text.
2. Structure: Preserve section headings, footnote numbers, and reference details exactly as they appear.
3. Honorifics: Use "Messenger of Allah (peace be upon him and his holy progeny)" \
for the Prophet, "Ameerul Momineen, Imam Ali (peace be upon him)" for Imam Ali, \
and "Imam [Name] (peace be upon him)" for other Imams. For Sayyedah Zahra, write \
"Sayyedah Zahra (peace be upon her)." Translate الله عز و جل as \
"Allah, Mighty and Majestic be He." Do not add honorifics for Abu Bakr, Omar, \
Ayesha, Othman, or Abu Huraira.
4. Qur'anic verses: Put verse citations in parentheses such as (Surah Baqarah 2:210).
5. Shia perspective: Maintain a respectful Shia viewpoint throughout.
6. No extra commentary: Provide a direct translation only.
7. Farsi text: The primary language is Farsi/Persian. Arabic quotations are embedded within.
8. Footnotes: If footnotes appear at the bottom of the page, include them as \
separate paragraphs with type "footnote".\
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_json_text(raw: str) -> str:
    """Strip code fences and extraneous text around a JSON object."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z0-9]*", "", raw).replace("```", "").strip()
    if "{" in raw and "}" in raw:
        raw = raw[raw.find("{") : raw.rfind("}") + 1]
    return raw


def extract_pdf_pages(pdf_path: Path, page_nums: list[int]) -> bytes:
    """Extract specific pages (1-based) from a PDF and return as PDF bytes."""
    src = fitz.open(str(pdf_path))
    dst = fitz.open()
    for pn in page_nums:
        dst.insert_pdf(src, from_page=pn - 1, to_page=pn - 1)
    buf = io.BytesIO()
    dst.save(buf)
    dst.close()
    src.close()
    return buf.getvalue()


def render_page_to_png(pdf_path: Path, page_num: int, dpi: int = 150) -> bytes:
    """Render a single PDF page (1-based) to PNG bytes."""
    doc = fitz.open(str(pdf_path))
    page = doc.load_page(page_num - 1)
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    png_bytes = pix.tobytes("png")
    doc.close()
    return png_bytes


def _extract_paragraphs(page_data: dict) -> list[dict]:
    """Extract paragraph list from a page data dict."""
    paras = []
    if isinstance(page_data, dict) and isinstance(page_data.get("paragraphs"), list):
        for p in page_data["paragraphs"]:
            if isinstance(p, dict):
                text = str(p.get("text") or "").strip()
                trans = str(p.get("translation") or "").strip()
                if text:
                    paras.append({"text": text, "translation": trans})
    return paras


def parse_pages_result(data: dict, requested_pages: list[int]) -> dict[int, list[dict]]:
    """Parse the Gemini response JSON into {page_num: [paragraphs]}.

    Handles flexible key formats and falls back to positional mapping
    when Gemini uses printed page numbers instead of our requested ones.
    """
    pages_raw = data.get("pages", {})
    if not isinstance(pages_raw, dict):
        return {}

    returned: list[tuple[int, list[dict]]] = []
    for key in pages_raw:
        nums = re.findall(r"\d+", str(key))
        if not nums:
            continue
        page_int = int(nums[-1])
        paras = _extract_paragraphs(pages_raw[key])
        if paras:
            returned.append((page_int, paras))

    if not returned:
        return {}

    returned.sort(key=lambda x: x[0])

    # Direct matching
    requested_set = set(requested_pages)
    matched = {k: v for k, v in returned if k in requested_set}
    if len(matched) == len(returned):
        return matched

    # Positional fallback — Gemini sometimes uses printed page numbers
    if len(returned) <= len(requested_pages):
        positional = {}
        for i, (_, paras) in enumerate(returned):
            if i < len(requested_pages):
                positional[requested_pages[i]] = paras
        if len(positional) > len(matched):
            return positional

    return matched


def collect_response_text(resp) -> str:
    """Extract text from a Gemini response."""
    parts = []
    try:
        for cand in resp.candidates or []:
            if not cand or not cand.content:
                continue
            for part in cand.content.parts or []:
                t = getattr(part, "text", None)
                if t:
                    parts.append(t)
    except Exception:
        pass
    return "\n".join(parts).strip()


def extract_usage(resp) -> dict:
    """Extract token usage from a Gemini response."""
    if hasattr(resp, "usage_metadata") and resp.usage_metadata:
        um = resp.usage_metadata
        return {
            "prompt_tokens": getattr(um, "prompt_token_count", 0) or 0,
            "completion_tokens": getattr(um, "candidates_token_count", 0) or 0,
            "total_tokens": getattr(um, "total_token_count", 0) or 0,
        }
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def add_usage(total: dict, usage: dict) -> None:
    """Accumulate usage into total dict."""
    for k in total:
        total[k] += usage.get(k, 0) or 0


def save_page(jsondir: Path, page_num: int, paragraphs: list[dict], source: str) -> None:
    """Save a single page's translation to JSON."""
    json_path = jsondir / f"page_{page_num:03d}.json"
    page_data = {"page": page_num, "source": source, "paragraphs": paragraphs}
    json_path.write_text(json.dumps(page_data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Core API calls
# ---------------------------------------------------------------------------

def ocr_batch_pdf(client, pdf_bytes: bytes, page_nums: list[int],
                  guidelines: str, model: str) -> tuple[dict[int, list[dict]], dict]:
    """OCR+translate a batch of pages via PDF input. Returns ({page: paras}, usage)."""
    page_mapping = ", ".join(f"PDF page {i+1} = book page {pn}" for i, pn in enumerate(page_nums))

    instruction = (
        f"{guidelines}\n\n"
        f"This PDF contains {len(page_nums)} pages. "
        f"They correspond to the following book pages: {page_mapping}.\n"
        "Process ALL pages. For each page, perform high-quality OCR, "
        "segment into logical paragraphs, and translate each into English.\n"
        'Return ONLY a JSON object: {"pages":{"<book_page_number>":{"paragraphs":'
        '[{"text":"<original>","translation":"<English>"},...]},...]}\n'
        "Use BOOK page numbers as keys. No explanations, no code fences. "
        "Preserve numerals, punctuation, and diacritics exactly."
    )

    content = types.Content(role="user", parts=[
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
        types.Part.from_text(text=instruction),
    ])
    cfg = types.GenerateContentConfig(
        response_modalities=["TEXT"],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    resp = client.models.generate_content(model=model, contents=content, config=cfg)
    usage = extract_usage(resp)
    full = collect_response_text(resp)
    cleaned = clean_json_text(full)

    try:
        data = json.loads(cleaned)
    except Exception as e:
        print(f"  JSON parse error: {e}")
        return {}, usage

    return parse_pages_result(data, page_nums), usage


def ocr_single_image(client, png_bytes: bytes,
                     guidelines: str, model: str) -> tuple[list[dict], dict]:
    """OCR+translate a single page via PNG image. Returns (paragraphs, usage)."""
    instruction = (
        f"{guidelines}\n\n"
        "OCR this page image. The text is in Farsi/Persian with embedded Arabic. "
        "Segment into logical paragraphs. Translate each to English.\n"
        'Return ONLY JSON: {"paragraphs":[{"text":"<original>","translation":"<English>"},...]}\n'
        "No code fences, no extra keys. Preserve numerals and diacritics exactly."
    )

    content = types.Content(role="user", parts=[
        types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
        types.Part.from_text(text=instruction),
    ])
    cfg = types.GenerateContentConfig(
        response_modalities=["TEXT"],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    resp = client.models.generate_content(model=model, contents=content, config=cfg)
    usage = extract_usage(resp)
    full = collect_response_text(resp)
    cleaned = clean_json_text(full)

    try:
        data = json.loads(cleaned)
        return _extract_paragraphs(data), usage
    except Exception:
        return [], usage


# ---------------------------------------------------------------------------
# Fallback retry logic
# ---------------------------------------------------------------------------

def retry_with_fallbacks(client, pdf_path: Path, missing_pages: list[int],
                         guidelines: str, fallback_models: list[str]) -> tuple[dict[int, list[dict]], dict]:
    """Try each fallback model (image-based) on missing pages. Returns ({page: paras}, usage)."""
    all_results: dict[int, list[dict]] = {}
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    remaining = list(missing_pages)

    for model in fallback_models:
        if not remaining:
            break
        mname = model.split("/")[-1]
        still_missing = []

        for pn in remaining:
            print(f"    [{pn}] trying {mname}...")
            try:
                png_bytes = render_page_to_png(pdf_path, pn)
                paras, usage = ocr_single_image(client, png_bytes, guidelines, model)
                add_usage(total_usage, usage)
                if paras:
                    all_results[pn] = paras
                    print(f"    [{pn}] OK ({len(paras)} paragraphs)")
                else:
                    still_missing.append(pn)
                    print(f"    [{pn}] empty response")
            except Exception as e:
                still_missing.append(pn)
                print(f"    [{pn}] error: {e}")
            time.sleep(1)

        remaining = still_missing

    return all_results, total_usage


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="OCR and translate PDF books using Gemini with multi-model fallback"
    )
    parser.add_argument("--pdf", type=Path, required=True, help="Path to PDF file")
    parser.add_argument("--jsondir", type=Path, required=True, help="Output directory for per-page JSON files")
    parser.add_argument("--guidelines", type=Path, default=None,
                        help="Translation guidelines file (if omitted, uses defaults)")
    parser.add_argument("--start-page", type=int, default=1, help="First page (1-based, default: 1)")
    parser.add_argument("--end-page", type=int, default=None, help="Last page (default: last)")
    parser.add_argument("--batch-size", type=int, default=10, help="Pages per batch (default: 10)")
    parser.add_argument("--model", type=str, default="models/gemini-3-flash-preview",
                        help="Primary Gemini model (default: gemini-3-flash-preview)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between batches in seconds")
    parser.add_argument("--no-fallback", action="store_true", help="Disable fallback model chain")

    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Error: GEMINI_API_KEY not set in environment or .env file")

    if not args.pdf.exists():
        sys.exit(f"Error: PDF not found: {args.pdf}")

    # Load guidelines
    if args.guidelines:
        if not args.guidelines.exists():
            sys.exit(f"Error: Guidelines file not found: {args.guidelines}")
        guidelines = args.guidelines.read_text(encoding="utf-8").strip()
        print(f"Guidelines: {args.guidelines}")
    else:
        guidelines = DEFAULT_GUIDELINES
        print("Guidelines: defaults")

    args.jsondir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(args.pdf))
    total_pages = doc.page_count
    doc.close()

    end_page = min(args.end_page or total_pages, total_pages)
    start_page = max(args.start_page, 1)

    print(f"PDF: {args.pdf.name} ({total_pages} pages, {args.pdf.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"Range: {start_page}-{end_page} | Batch: {args.batch_size} | Model: {args.model}")
    if not args.no_fallback:
        print(f"Fallbacks: {' -> '.join(m.split('/')[-1] for m in FALLBACK_MODELS)}")
    print()

    # Pages still needed
    all_pages = list(range(start_page, end_page + 1))
    needed = [p for p in all_pages if not (args.jsondir / f"page_{p:03d}.json").exists()]
    skipped = len(all_pages) - len(needed)
    if skipped:
        print(f"Skipping {skipped} already-translated pages")
    if not needed:
        print("All pages already translated!")
        return

    batches = [needed[i : i + args.batch_size] for i in range(0, len(needed), args.batch_size)]
    print(f"Processing {len(needed)} pages in {len(batches)} batches\n")

    client = genai.Client(api_key=api_key)
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    total_saved = 0
    all_failed = []
    t_start = time.time()
    source_primary = f"gemini_pdf_batched:{args.model.split('/')[-1]}"

    for bi, batch in enumerate(batches):
        print(f"Batch {bi+1}/{len(batches)}: pages {batch[0]}-{batch[-1]} ({len(batch)} pages)")

        t0 = time.time()
        chunk_bytes = extract_pdf_pages(args.pdf, batch)
        print(f"  Mini-PDF: {len(chunk_bytes) / 1024:.0f} KB")

        try:
            pages_result, usage = ocr_batch_pdf(client, chunk_bytes, batch, guidelines, args.model)
        except Exception as e:
            print(f"  ERROR: {e}")
            pages_result, usage = {}, {}
            time.sleep(5)

        add_usage(total_usage, usage)

        # Save successful pages
        batch_saved = 0
        batch_missing = []
        for pn in batch:
            paras = pages_result.get(pn, [])
            if paras:
                save_page(args.jsondir, pn, paras, source_primary)
                batch_saved += 1
            else:
                batch_missing.append(pn)

        # Fallback chain for missing pages
        if batch_missing and not args.no_fallback:
            print(f"  {len(batch_missing)} pages missing, trying fallback models...")
            fb_result, fb_usage = retry_with_fallbacks(
                client, args.pdf, batch_missing, guidelines, FALLBACK_MODELS
            )
            add_usage(total_usage, fb_usage)
            for pn, paras in fb_result.items():
                source_fb = f"fallback:{FALLBACK_MODELS[0].split('/')[-1]}"
                save_page(args.jsondir, pn, paras, source_fb)
                batch_saved += 1
                batch_missing.remove(pn)

        all_failed.extend(batch_missing)
        total_saved += batch_saved
        elapsed = time.time() - t0
        per_page = elapsed / len(batch) if batch else 0
        print(f"  Saved {batch_saved}/{len(batch)} ({elapsed:.1f}s, {per_page:.1f}s/page, {usage.get('total_tokens', '?')} tokens)")

        if bi < len(batches) - 1:
            time.sleep(args.delay)

    total_elapsed = time.time() - t_start
    print()
    print("=" * 60)
    print(f"COMPLETE: {total_saved} pages saved, {len(all_failed)} failed")
    print(f"Time: {total_elapsed:.0f}s ({total_elapsed / 60:.1f} min)")
    if total_saved:
        print(f"Average: {total_elapsed / total_saved:.1f}s per page")
    print(f"Tokens: {total_usage}")
    if all_failed:
        print(f"Failed pages: {all_failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
