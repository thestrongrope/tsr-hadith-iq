#!/usr/bin/env python3
"""
Quality comparison: Extract book/author citations from Abaqat al-Anwar
across multiple models (Grok 4.1 Fast, Gemini Flash Lite, Gemini Flash).

Key insight: Models extract more carefully from smaller inputs. We chunk
each volume into ~2000-line segments and process each chunk separately,
then merge results.

Usage:
  uv run --with openai --with google-genai --with python-dotenv python scripts/compare_models_citations.py [--models grok,flash-lite,flash] [--volume 3] [--chunk-lines 2000]
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

VOLUMES_DIR = REPO_ROOT / "sources" / "abaqat" / "volumes-djvu"
OUTPUT_DIR = REPO_ROOT / "docs" / "citation-extraction"

# ── Model configs ──────────────────────────────────────────────────

MODEL_CONFIGS = {
    "grok": {
        "name": "Grok 4.1 Fast",
        "model_id": "grok-4-1-fast-non-reasoning",
        "backend": "openai",
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "GROK_API_KEY",
        "price_in": 0.20,
        "price_out": 0.50,
        "max_output": 131072,
    },
    "flash-lite": {
        "name": "Gemini 3.1 Flash Lite",
        "model_id": "gemini-3.1-flash-lite-preview",
        "backend": "gemini",
        "api_key_env": "GEMINI_API_KEY",
        "price_in": 0.25,
        "price_out": 1.50,
        "max_output": 65536,
    },
    "flash": {
        "name": "Gemini 3 Flash",
        "model_id": "gemini-3-flash-preview",
        "backend": "gemini",
        "api_key_env": "GEMINI_API_KEY",
        "price_in": 0.50,
        "price_out": 3.00,
        "max_output": 65536,
    },
}

# ── Citation context taxonomy ──────────────────────────────────────

CITATION_CONTEXTS = """
Citation context categories (assign exactly ONE per citation):

- PRIMARY_REBUTTAL: Citing a book/author as part of directly countering one of Dehlavi's main claims about a hadith
- SUB_CLAIM_REBUTTAL: Citing a book/author to counter a subsidiary point within a larger argument
- AUTHOR_TAWTHIQ: Citing a rijal source to ESTABLISH the authority/reliability of a scholar (positive evaluation — ta'dil)
- AUTHOR_TAJRIH: Citing a rijal source to DESTROY the authority/reliability of a scholar (negative evaluation — jarh)
- TAWATUR_PROOF: Citing sources to prove mass-transmission (tawatur) of a hadith — stacking multiple transmitters
- CONTRADICTION: Citing a source to show the opponent contradicts himself or relies on the same source elsewhere
- ARGUMENT_LINEAGE: Citing to trace who originated a claim and who copied it (مقلدین / بتقلید chain)
- REBUTTAL_LINEAGE: Citing prior scholars who already refuted the same claim (سلسلة الجواب)
- LINGUISTIC: Citing lexicons, grammar books, or dictionaries for word meaning analysis
- HADITH_SOURCE: Citing the actual hadith text from a primary collection (not for rijal evaluation)
- CROSS_REF: Internal cross-reference to another part of Abaqat or another volume
"""

# ── Prompts ────────────────────────────────────────────────────────

SYSTEM_INSTRUCTION = """You are an expert Islamic studies scholar with deep knowledge of:
- Sunni-Shia polemical literature
- Classical Farsi (the author's language) and Arabic (quotation language)
- Rijal (narrator criticism), hadith sciences, and biographical dictionaries
- The specific structure of Abaqat al-Anwar by Mir Hamid Husain (d. 1306 AH)

The text you will analyze is OCR'd Farsi with embedded Arabic. Expect OCR errors but the content is recoverable.

The book's pattern: Farsi matrix embedding Arabic data blocks. Every Arabic quotation from a Sunni source is followed by a Farsi exegesis. Book titles appear in parentheses () or guillemets «». Biographical dossiers are headed by «ترجمة [Name] از [Book]».

CRITICAL RULES:
1. Be EXHAUSTIVE. List EVERY book and author citation. If the same book appears 20 times, list all 20 with individual contexts.
2. OCR CORRECTION: The text has OCR errors in Arabic/Farsi book titles. You MUST output the CORRECT standard Arabic title, not the OCR-mangled version. Use your knowledge of classical Islamic bibliography to recognize book titles even when OCR has corrupted individual characters.
3. AUTHOR IDENTIFICATION: Always fill in the full author name even if the text only gives a short form like "ذهبی کفته" or "ابن حجر" or just mentions the book title. Use your knowledge of Islamic bibliography to identify the author, their full name, and their death date in AH. Never leave author fields blank or null.
4. SECTION HEADINGS are NOT book citations. Lines like "جواب شیخ مفید از هفوات نظام" are section headings — do not list them as books.
5. FOOTNOTES: Lines like "(١) القصول ص ٥٠" are footnote references to a book already cited in the main text — you may list them but mark them as the same citation.
6. When "قال الخطیب" appears INSIDE a quote from another book (like Lisan al-Mizan quoting al-Khatib), note this as a nested citation — the primary source is Lisan al-Mizan, the nested source is Tarikh Baghdad."""

CHUNK_PROMPT = """You are analyzing a SECTION of Volume {vol_num} of Abaqat al-Anwar (عبقات الانوار).
This is chunk {chunk_num} of {total_chunks} (lines {line_start}–{line_end}).
The volume defends: {hadith_name}

Extract EVERY citation of a book or author in this section. For each citation:
1. The book cited — give the CORRECTED Arabic name (fix OCR errors) + transliteration
2. The author — ALWAYS fill in the full name, Arabic + transliteration + death date. Use your knowledge of Islamic bibliography to identify authors even when the text only gives a short reference like "ذهبی کفته"
3. WHY this book/author is cited here (context category from list below)
4. If inside a biographical dossier (ترجمه): who is the SUBJECT being evaluated
5. Any volume/page reference (look for ج / ص markers)

{citation_contexts}

Return a JSON object:
{{
  "chunk_info": {{
    "volume": {vol_num},
    "chunk": {chunk_num},
    "lines": "{line_start}-{line_end}"
  }},
  "citations": [
    {{
      "book_arabic": "CORRECTED Arabic book title (fix OCR errors)",
      "book_transliterated": "romanized book name",
      "author_arabic": "FULL author name in Arabic (REQUIRED — never leave blank)",
      "author_transliterated": "romanized author name (REQUIRED — never leave blank)",
      "author_death_ah": 748,
      "citation_context": "ONE category from above",
      "context_detail": "1-2 sentence explanation of why this is cited here",
      "subject_scholar": "who is being evaluated in a dossier, or null if not in a dossier",
      "vol_page_cited": "volume/page if mentioned (e.g. 'j.3 p.214'), or null"
    }}
  ]
}}

IMPORTANT:
- Be EXHAUSTIVE. List every book title and author name. Do not skip or group citations.
- ALWAYS fill in author_arabic and author_transliterated — never leave them as null or empty.
- Correct OCR errors in book titles (e.g. القصول → الفصول).
- Do NOT list section headings as book citations.

HERE IS THE TEXT SECTION:

"""

# Volume-to-hadith mapping
HADITH_MAP = {
    1: "Hadith al-Ghadir (Sanad)", 2: "Hadith al-Ghadir (Sanad)",
    3: "Hadith al-Ghadir (Sanad)", 4: "Hadith of the Twelve Caliphs",
    5: "Hadith al-Ghadir (Sanad)", 6: "Hadith al-Ghadir (Dalalat)",
    7: "Hadith al-Ghadir (Dalalat)", 8: "Hadith al-Ghadir (Dalalat)",
    9: "Hadith al-Ghadir (Dalalat)", 10: "Hadith al-Ghadir (Dalalat)",
    11: "Hadith al-Manzila", 12: "Hadith al-Wilayah",
    13: "Hadith al-Tayr", 14: "Hadith Madinat al-Ilm",
    15: "Hadith Madinat al-Ilm", 16: "Hadith al-Tashbih",
    17: "Hadith al-Nur", 18: "Hadith al-Thaqalayn",
    19: "Hadith al-Thaqalayn", 20: "Hadith al-Thaqalayn",
    21: "Hadith al-Thaqalayn", 22: "Hadith al-Thaqalayn",
    23: "Hadith al-Safinah",
}


def load_volume(vol_num):
    path = VOLUMES_DIR / f"abaghaat al'anwaar {vol_num}_djvu.txt"
    if not path.exists():
        return None, path
    with open(path, "r", encoding="utf-8") as f:
        return f.read(), path


def chunk_text(text, chunk_lines=2000):
    """Split text into chunks at line boundaries."""
    lines = text.split("\n")
    chunks = []
    for i in range(0, len(lines), chunk_lines):
        chunk = "\n".join(lines[i:i + chunk_lines])
        chunks.append({
            "text": chunk,
            "line_start": i + 1,
            "line_end": min(i + chunk_lines, len(lines)),
        })
    return chunks


# ── API backends ──────────────────────────────────────────────────

def call_grok(config, system_prompt, user_prompt):
    from openai import OpenAI

    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        return None, f"Missing {config['api_key_env']}"

    client = OpenAI(api_key=api_key, base_url=config["base_url"])

    t0 = time.time()
    response = client.chat.completions.create(
        model=config["model_id"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=config["max_output"],
        response_format={"type": "json_object"},
    )
    elapsed = time.time() - t0

    text = response.choices[0].message.content
    usage = response.usage
    return text, {
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "elapsed_seconds": round(elapsed, 1),
        "finish_reason": response.choices[0].finish_reason,
    }


def call_gemini(config, system_prompt, user_prompt):
    from google import genai
    from google.genai import types

    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        return None, f"Missing {config['api_key_env']}"

    client = genai.Client(api_key=api_key)

    t0 = time.time()
    response = client.models.generate_content(
        model=config["model_id"],
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            max_output_tokens=config["max_output"],
            response_mime_type="application/json",
        ),
    )
    elapsed = time.time() - t0

    text = response.text
    meta = response.usage_metadata
    return text, {
        "input_tokens": meta.prompt_token_count if meta else 0,
        "output_tokens": meta.candidates_token_count if meta else 0,
        "elapsed_seconds": round(elapsed, 1),
        "finish_reason": "stop",
    }


def call_model(config, system_prompt, user_prompt):
    """Dispatch to the right backend."""
    if config["backend"] == "openai":
        return call_grok(config, system_prompt, user_prompt)
    else:
        return call_gemini(config, system_prompt, user_prompt)


def parse_json_response(raw_text):
    """Parse JSON response, handling common model quirks."""
    try:
        data = json.loads(raw_text)
        # If model returns a list instead of object, wrap it
        if isinstance(data, list):
            data = {"citations": data}
        return data, None
    except json.JSONDecodeError as e:
        return None, str(e)


# ── Main processing ───────────────────────────────────────────────

def process_volume_chunked(model_key, vol_num, vol_text, chunk_lines, single_chunk=None):
    """Process a volume in chunks, merge results."""
    config = MODEL_CONFIGS[model_key]
    hadith = HADITH_MAP.get(vol_num, "Unknown")
    all_chunks = chunk_text(vol_text, chunk_lines)

    # Filter to single chunk if requested
    if single_chunk is not None:
        if single_chunk < 1 or single_chunk > len(all_chunks):
            print(f"  ERROR: chunk {single_chunk} out of range (1-{len(all_chunks)})")
            return None
        chunks = [all_chunks[single_chunk - 1]]
        # Preserve original chunk numbering
        chunks[0]["_orig_idx"] = single_chunk
    else:
        chunks = all_chunks
        for i, c in enumerate(chunks, 1):
            c["_orig_idx"] = i

    print(f"\n{'='*60}")
    print(f"  {config['name']} ({config['model_id']})")
    print(f"  Volume {vol_num}: {hadith}")
    total_chunks_count = len(all_chunks)
    print(f"  Processing {len(chunks)} of {total_chunks_count} chunks (~{chunk_lines} lines each)")
    print(f"  Pricing: ${config['price_in']}/M in, ${config['price_out']}/M out")
    print(f"{'='*60}")

    all_citations = []
    total_stats = {"input_tokens": 0, "output_tokens": 0, "elapsed_seconds": 0}
    errors = []

    # Per-chunk cache directory for resumability
    chunk_cache_dir = OUTPUT_DIR / f"vol{vol_num:02d}-{model_key}-chunks"
    chunk_cache_dir.mkdir(parents=True, exist_ok=True)

    MAX_RETRIES = 2

    for chunk in chunks:
        i = chunk["_orig_idx"]

        # Check if this chunk is already cached (resumability)
        cache_file = chunk_cache_dir / f"chunk-{i:02d}.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
            citations = cached.get("citations", [])
            all_citations.extend(citations)
            cached_stats = cached.get("stats", {})
            total_stats["input_tokens"] += cached_stats.get("input_tokens", 0)
            total_stats["output_tokens"] += cached_stats.get("output_tokens", 0)
            total_stats["elapsed_seconds"] += cached_stats.get("elapsed_seconds", 0)
            print(f"  Chunk {i}/{total_chunks_count} (lines {chunk['line_start']}-{chunk['line_end']})... CACHED ({len(citations)} citations)")
            continue

        prompt = CHUNK_PROMPT.format(
            vol_num=vol_num,
            chunk_num=i,
            total_chunks=total_chunks_count,
            line_start=chunk["line_start"],
            line_end=chunk["line_end"],
            hadith_name=hadith,
            citation_contexts=CITATION_CONTEXTS,
        ) + chunk["text"]

        # Retry loop
        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            attempt_label = f" (attempt {attempt}/{MAX_RETRIES})" if attempt > 1 else ""
            print(f"  Chunk {i}/{total_chunks_count} (lines {chunk['line_start']}-{chunk['line_end']}){attempt_label}...", end=" ", flush=True)

            try:
                raw_text, stats = call_model(config, SYSTEM_INSTRUCTION, prompt)

                if raw_text is None:
                    print(f"FAILED: {stats}")
                    if attempt < MAX_RETRIES:
                        print(f"    Retrying...", end=" ")
                        time.sleep(2)
                    continue

                total_stats["input_tokens"] += stats["input_tokens"]
                total_stats["output_tokens"] += stats["output_tokens"]
                total_stats["elapsed_seconds"] += stats["elapsed_seconds"]

                data, parse_err = parse_json_response(raw_text)
                if parse_err:
                    print(f"JSON error: {parse_err} ({stats['output_tokens']} tokens)")
                    if attempt < MAX_RETRIES:
                        print(f"    Retrying...", end=" ")
                        time.sleep(2)
                    continue

                citations = data.get("citations", [])
                for c in citations:
                    c["_chunk"] = i
                    c["_lines"] = f"{chunk['line_start']}-{chunk['line_end']}"

                all_citations.extend(citations)
                print(f"{len(citations)} citations ({stats['output_tokens']} tokens, {stats['elapsed_seconds']}s)")

                # Cache successful result
                cache_data = {"chunk": i, "citations": citations, "stats": stats}
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)

                success = True
                break

            except Exception as e:
                print(f"ERROR: {e}")
                if attempt < MAX_RETRIES:
                    print(f"    Retrying...", end=" ")
                    time.sleep(2)

        if not success:
            # Auto-reduce: split into smaller sub-chunks and retry
            # If sub-chunks also fail on Grok, fall back to Flash Lite
            lines_list = chunk["text"].split("\n")
            half_size = len(lines_list) // 2
            sub_chunks = [
                {"text": "\n".join(lines_list[:half_size]),
                 "line_start": chunk["line_start"], "line_end": chunk["line_start"] + half_size - 1},
                {"text": "\n".join(lines_list[half_size:]),
                 "line_start": chunk["line_start"] + half_size, "line_end": chunk["line_end"]},
            ]
            print(f"    Splitting chunk {i} into 2 halves...")

            for si, sub in enumerate(sub_chunks, 1):
                sub_cache = chunk_cache_dir / f"chunk-{i:02d}-sub{si}.json"
                if sub_cache.exists():
                    with open(sub_cache, "r", encoding="utf-8") as f:
                        cached = json.load(f)
                    sub_citations = cached.get("citations", [])
                    all_citations.extend(sub_citations)
                    print(f"    Sub-chunk {i}.{si} CACHED ({len(sub_citations)} citations)")
                    continue

                sub_prompt = CHUNK_PROMPT.format(
                    vol_num=vol_num, chunk_num=f"{i}.{si}",
                    total_chunks=total_chunks_count,
                    line_start=sub["line_start"], line_end=sub["line_end"],
                    hadith_name=hadith, citation_contexts=CITATION_CONTEXTS,
                ) + sub["text"]

                # Try primary model first
                sub_success = False
                for attempt in range(1, MAX_RETRIES + 1):
                    label = f" (attempt {attempt})" if attempt > 1 else ""
                    print(f"    Sub-chunk {i}.{si} (lines {sub['line_start']}-{sub['line_end']}){label}...", end=" ", flush=True)
                    try:
                        raw_text, stats = call_model(config, SYSTEM_INSTRUCTION, sub_prompt)
                        total_stats["input_tokens"] += stats["input_tokens"]
                        total_stats["output_tokens"] += stats["output_tokens"]
                        total_stats["elapsed_seconds"] += stats["elapsed_seconds"]

                        data, parse_err = parse_json_response(raw_text)
                        if parse_err:
                            print(f"JSON error: {parse_err}")
                            if attempt < MAX_RETRIES:
                                time.sleep(2)
                            continue

                        sub_citations = data.get("citations", [])
                        for c in sub_citations:
                            c["_chunk"] = i
                            c["_lines"] = f"{sub['line_start']}-{sub['line_end']}"
                        all_citations.extend(sub_citations)
                        print(f"{len(sub_citations)} citations ({stats['output_tokens']} tokens, {stats['elapsed_seconds']}s)")

                        with open(sub_cache, "w", encoding="utf-8") as f:
                            json.dump({"chunk": f"{i}.{si}", "citations": sub_citations, "stats": stats}, f, ensure_ascii=False, indent=2)
                        sub_success = True
                        break
                    except Exception as e:
                        print(f"ERROR: {e}")
                        if attempt < MAX_RETRIES:
                            time.sleep(2)

                # Fall back to Flash Lite if primary model failed
                if not sub_success and config["model_id"] != MODEL_CONFIGS.get("flash-lite", {}).get("model_id"):
                    fallback = MODEL_CONFIGS.get("flash-lite")
                    if fallback and os.getenv(fallback["api_key_env"]):
                        print(f"    Falling back to {fallback['name']} for sub-chunk {i}.{si}...", end=" ", flush=True)
                        try:
                            raw_text, stats = call_model(fallback, SYSTEM_INSTRUCTION, sub_prompt)
                            total_stats["input_tokens"] += stats["input_tokens"]
                            total_stats["output_tokens"] += stats["output_tokens"]
                            total_stats["elapsed_seconds"] += stats["elapsed_seconds"]

                            data, parse_err = parse_json_response(raw_text)
                            if parse_err:
                                print(f"Flash Lite also failed: {parse_err}")
                                errors.append({"chunk": f"{i}.{si}", "error": f"both models failed: {parse_err}"})
                                continue

                            sub_citations = data.get("citations", [])
                            for c in sub_citations:
                                c["_chunk"] = i
                                c["_lines"] = f"{sub['line_start']}-{sub['line_end']}"
                                c["_fallback"] = fallback["name"]
                            all_citations.extend(sub_citations)
                            print(f"{len(sub_citations)} citations (fallback, {stats['output_tokens']} tokens, {stats['elapsed_seconds']}s)")

                            with open(sub_cache, "w", encoding="utf-8") as f:
                                json.dump({"chunk": f"{i}.{si}", "citations": sub_citations, "stats": stats, "fallback": fallback["name"]}, f, ensure_ascii=False, indent=2)
                            sub_success = True
                        except Exception as e:
                            print(f"Fallback ERROR: {e}")
                            errors.append({"chunk": f"{i}.{si}", "error": str(e)})

                if not sub_success:
                    errors.append({"chunk": f"{i}.{si}", "error": "all attempts + fallback failed"})

    # Compute cost
    in_cost = (total_stats["input_tokens"] / 1_000_000) * config["price_in"]
    out_cost = (total_stats["output_tokens"] / 1_000_000) * config["price_out"]
    total_cost = in_cost + out_cost

    # Summary
    print(f"\n  --- {config['name']} Summary ---")
    print(f"  Total citations: {len(all_citations)}")
    print(f"  Tokens: {total_stats['input_tokens']:,} in + {total_stats['output_tokens']:,} out")
    print(f"  Time: {total_stats['elapsed_seconds']:.0f}s")
    print(f"  Cost: ${in_cost:.4f} + ${out_cost:.4f} = ${total_cost:.4f}")
    if errors:
        print(f"  Errors: {len(errors)} chunks failed")

    # Context breakdown
    ctx_counts = {}
    for c in all_citations:
        ctx = c.get("citation_context", "UNKNOWN")
        ctx_counts[ctx] = ctx_counts.get(ctx, 0) + 1
    if ctx_counts:
        print(f"  By context:")
        for ctx, count in sorted(ctx_counts.items(), key=lambda x: -x[1]):
            print(f"    {ctx}: {count}")

    # Unique books/authors
    books = set()
    authors = set()
    for c in all_citations:
        bt = c.get("book_transliterated", "")
        at = c.get("author_transliterated", "")
        if bt:
            books.add(bt)
        if at:
            authors.add(at)
    print(f"  Unique books: {len(books)} | Unique authors: {len(authors)}")

    # Build result
    result = {
        "model": config["name"],
        "model_id": config["model_id"],
        "volume": vol_num,
        "hadith_defended": hadith,
        "chunk_lines": chunk_lines,
        "num_chunks": len(chunks),
        "stats": total_stats,
        "cost": {"input": round(in_cost, 4), "output": round(out_cost, 4), "total": round(total_cost, 4)},
        "total_citations": len(all_citations),
        "unique_books": len(books),
        "unique_authors": len(authors),
        "citations_by_context": ctx_counts,
        "citations": all_citations,
        "errors": errors,
    }

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"vol{vol_num:02d}-{model_key}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {out_path.relative_to(REPO_ROOT)}")

    return result


def print_comparison(results):
    print(f"\n{'='*70}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'='*70}")

    print(f"\n{'Metric':<25}", end="")
    for r in results:
        name = r["model"][:18]
        print(f"  {name:>18}", end="")
    print()
    print("-" * (25 + 20 * len(results)))

    rows = [
        ("Total citations", lambda r: r["total_citations"]),
        ("Unique books", lambda r: r["unique_books"]),
        ("Unique authors", lambda r: r["unique_authors"]),
        ("Input tokens", lambda r: f"{r['stats']['input_tokens']:,}"),
        ("Output tokens", lambda r: f"{r['stats']['output_tokens']:,}"),
        ("Time (seconds)", lambda r: f"{r['stats']['elapsed_seconds']:.0f}"),
        ("Cost ($)", lambda r: f"${r['cost']['total']:.4f}"),
        ("Errors", lambda r: len(r.get("errors", []))),
    ]

    for label, fn in rows:
        print(f"{label:<25}", end="")
        for r in results:
            print(f"  {str(fn(r)):>18}", end="")
        print()

    # Context comparison
    all_contexts = set()
    for r in results:
        all_contexts.update(r.get("citations_by_context", {}).keys())

    if all_contexts:
        print(f"\n{'Context':<25}", end="")
        for r in results:
            name = r["model"][:18]
            print(f"  {name:>18}", end="")
        print()
        print("-" * (25 + 20 * len(results)))

        for ctx in sorted(all_contexts):
            print(f"{ctx:<25}", end="")
            for r in results:
                val = r.get("citations_by_context", {}).get(ctx, 0)
                print(f"  {val:>18}", end="")
            print()


def main():
    parser = argparse.ArgumentParser(description="Compare citation extraction across models")
    parser.add_argument("--models", default="grok,flash-lite,flash",
                        help="Comma-separated model keys")
    parser.add_argument("--volume", type=int, default=3,
                        help="Volume number (default: 3)")
    parser.add_argument("--chunk-lines", type=int, default=2000,
                        help="Lines per chunk (default: 2000)")
    parser.add_argument("--single-chunk", type=int, default=None,
                        help="Only process this chunk number (1-indexed)")
    args = parser.parse_args()

    model_keys = [m.strip() for m in args.models.split(",")]
    vol_num = args.volume

    print(f"Citation Extraction — Model Quality Comparison (Chunked)")
    print(f"Volume: {vol_num} | Chunk size: {args.chunk_lines} lines")
    print(f"Models: {', '.join(model_keys)}")

    # Load volume
    vol_text, vol_path = load_volume(vol_num)
    if vol_text is None:
        print(f"ERROR: Volume {vol_num} not found at {vol_path}")
        sys.exit(1)

    lines = vol_text.count("\n")
    n_chunks = (lines + args.chunk_lines - 1) // args.chunk_lines
    print(f"Volume {vol_num}: {len(vol_text):,} chars, {lines:,} lines → {n_chunks} chunks")

    # Estimate cost
    est_input_m = (len(vol_text) / 3) / 1_000_000
    est_output_per_chunk = 5000  # tokens
    est_output_m = (est_output_per_chunk * n_chunks) / 1_000_000
    print(f"\nEstimated cost per model:")
    for key in model_keys:
        if key in MODEL_CONFIGS:
            c = MODEL_CONFIGS[key]
            cost = est_input_m * c["price_in"] + est_output_m * c["price_out"]
            print(f"  {c['name']}: ~${cost:.3f}")

    # Run each model
    results = []
    for key in model_keys:
        if key not in MODEL_CONFIGS:
            print(f"\nWARNING: Unknown model '{key}', skipping")
            continue
        result = process_volume_chunked(key, vol_num, vol_text, args.chunk_lines, args.single_chunk)
        results.append(result)

    # Comparison
    if len(results) > 1:
        print_comparison(results)

    print(f"\nResults saved to: docs/citation-extraction/")


if __name__ == "__main__":
    main()
