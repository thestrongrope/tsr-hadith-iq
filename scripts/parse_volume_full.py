#!/usr/bin/env python3
"""
Full structural parse of an Abaqat volume into the v2 data model.
Sends each section individually to Grok with section-type-specific prompts.
Results are cached per-section for resumability.

Usage:
  uv run --with openai --with python-dotenv python scripts/parse_volume_full.py --volume 23
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

VOLUMES_DIR = REPO_ROOT / "sources" / "abaqat" / "volumes-djvu"
OUTPUT_DIR = REPO_ROOT / "docs" / "volume-parsed"

HADITH_MAP = {
    1: ("Hadith al-Ghadir", "حديث الغدير", "Sanad"),
    2: ("Hadith al-Ghadir", "حديث الغدير", "Sanad"),
    3: ("Hadith al-Ghadir", "حديث الغدير", "Sanad"),
    4: ("Hadith of the Twelve Caliphs", "حديث الاثني عشر خليفة", "Dalalah"),
    5: ("Hadith al-Ghadir", "حديث الغدير", "Sanad"),
    6: ("Hadith al-Ghadir", "حديث الغدير", "Dalalah"),
    7: ("Hadith al-Ghadir", "حديث الغدير", "Dalalah"),
    8: ("Hadith al-Ghadir", "حديث الغدير", "Dalalah"),
    9: ("Hadith al-Ghadir", "حديث الغدير", "Dalalah"),
    10: ("Hadith al-Ghadir", "حديث الغدير", "Dalalah"),
    11: ("Hadith al-Manzila", "حديث المنزلة", "Sanad+Dalalah"),
    12: ("Hadith al-Wilayah", "حديث الولاية", "Sanad"),
    13: ("Hadith al-Tayr", "حديث الطير", "Sanad+Dalalah"),
    14: ("Hadith Madinat al-Ilm", "حديث مدينة العلم", "Sanad+Dalalah"),
    15: ("Hadith Madinat al-Ilm", "حديث مدينة العلم", "Sanad+Dalalah"),
    16: ("Hadith al-Tashbih", "حديث التشبيه", "Sanad+Dalalah"),
    17: ("Hadith al-Nur", "حديث النور", "Sanad"),
    18: ("Hadith al-Thaqalayn", "حديث الثقلين", "Sanad+Dalalah"),
    19: ("Hadith al-Thaqalayn", "حديث الثقلين", "Sanad+Dalalah"),
    20: ("Hadith al-Thaqalayn", "حديث الثقلين", "Sanad+Dalalah"),
    21: ("Hadith al-Thaqalayn", "حديث الثقلين", "Sanad+Dalalah"),
    22: ("Hadith al-Thaqalayn", "حديث الثقلين", "Sanad+Dalalah"),
    23: ("Hadith al-Safinah", "حديث السفينة", "Sanad+Dalalah"),
}

# ── Section detection (deterministic regex) ───────────────────────

def detect_sections(lines):
    """Detect structural sections from OCR text using regex patterns."""
    markers = []
    total = len(lines)

    for i, line in enumerate(lines):
        ln = i + 1
        s = line.strip()
        if not s or len(s) < 5:
            continue

        if 'فهرست مطالب' in s and ln < 100:
            markers.append({"line": ln, "type": "TABLE_OF_CONTENTS", "raw_heading": s[:80]})

        if ln < 230:
            continue

        # Author's preface
        if 'خاطب ما ميخواهد' in s and ln < 400:
            markers.append({"line": ln, "type": "TAMHID", "raw_heading": s[:100]})

        # Narrator citations
        if re.match(r'^اما\s', s):
            markers.append({"line": ln, "type": "NARRATOR_CITATION", "raw_heading": s[:120]})

        # Dalalah
        if 'وجه دلالت' in s or 'وجوه دلالت' in s or ('دلالت' in s and 'حديث' in s and 'امامت' in s):
            markers.append({"line": ln, "type": "DALALAH", "raw_heading": s[:100]})

        # Author responses
        if re.match(r'^اقول[:\s]', s):
            markers.append({"line": ln, "type": "AUTHOR_RESPONSE", "raw_heading": s[:80]})

        # Dehlavi claims/responses
        if 'كلام شاهصاحب' in s or 'كلام شاه صاحب' in s:
            markers.append({"line": ln, "type": "DEHLAVI_CLAIM", "raw_heading": s[:100]})
        if re.match(r'^جواب', s) and ('شاهصاحب' in s or 'شاه صاحب' in s):
            markers.append({"line": ln, "type": "DEHLAVI_RESPONSE", "raw_heading": s[:100]})

        # Biographical dossiers
        if re.match(r'.*درترجم[هة]', s) and ('كفته' in s or 'كفت' in s):
            markers.append({"line": ln, "type": "BIOGRAPHICAL_DOSSIER", "raw_heading": s[:100]})

        # Tanbih
        if 'تنبيه' in s and len(s) < 80:
            markers.append({"line": ln, "type": "TANBIH", "raw_heading": s[:80]})

        # Aqidah
        if 'عقيده اهل' in s:
            markers.append({"line": ln, "type": "AQIDAH", "raw_heading": s[:100]})

        # Ilzam
        if 'الزام' in s and 'افحام' in s:
            markers.append({"line": ln, "type": "ILZAM", "raw_heading": s[:80]})

        # Appendix
        if ln > 10000 and 'فهرست' in s:
            markers.append({"line": ln, "type": "APPENDIX", "raw_heading": s[:80]})

    # Sort and compute boundaries
    markers.sort(key=lambda m: m["line"])
    sections = []
    for i, m in enumerate(markers):
        sec = {
            "id": i + 1,
            "type": m["type"],
            "raw_heading": m["raw_heading"],
            "start_line": m["line"],
            "end_line": markers[i + 1]["line"] - 1 if i + 1 < len(markers) else total,
        }
        sec["line_count"] = sec["end_line"] - sec["start_line"] + 1
        sec["text"] = "".join(lines[sec["start_line"] - 1: sec["end_line"]])
        sec["char_count"] = len(sec["text"])
        sections.append(sec)

    return sections


# ── Section-specific prompts ──────────────────────────────────────

SYSTEM = """You are an expert Islamic studies scholar analyzing Abaqat al-Anwar by Mir Hamid Husain (d. 1306 AH).
The text is OCR'd Farsi with embedded Arabic. Expect OCR errors but content is recoverable.
You MUST correct OCR errors in book titles and scholar names using your knowledge of Islamic bibliography.
Always provide full scholar names, death dates (AH), and correct Arabic book titles.
Return valid JSON only."""

PROMPTS = {
    "NARRATOR_CITATION": """This section introduces a Sunni scholar who narrated Hadith al-Safinah.
The pattern is: "اما [Scholar], he narrated this hadith in [Book]..." followed by the chain and hadith text.

Extract:
{{
  "narrator": {{
    "name_arabic": "full Arabic name",
    "name_transliterated": "romanized",
    "death_ah": null,
    "school": "Shafi'i/Hanafi/Hanbali/etc or null"
  }},
  "source_book": {{
    "name_arabic": "corrected Arabic title",
    "name_transliterated": "romanized",
    "book_type": "hadith/rijal/tarikh/tafsir/etc"
  }},
  "companion_narrator": "which Sahabi the chain goes through (e.g. Abu Dharr, Ibn Abbas)",
  "isnad_summary": "brief description of the chain",
  "hadith_text": "the Arabic hadith text as quoted in this section",
  "author_commentary": "brief summary of the author's Farsi commentary (if any)",
  "additional_books_cited": [
    {{"name_arabic": "...", "name_transliterated": "...", "author": "..."}}
  ]
}}""",

    "DALALAH": """This section contains numbered proofs (وجوه) showing how Hadith al-Safinah proves Imamate.

Extract each proof:
{{
  "proofs": [
    {{
      "number": 1,
      "number_farsi": "وجه اول",
      "argument_summary": "English summary of the argument",
      "argument_text_excerpt": "key Farsi/Arabic phrase (first 200 chars)",
      "evidence_type": "logical/textual/linguistic/historical",
      "sources_cited": [{{"name": "...", "author": "..."}}]
    }}
  ],
  "total_proofs": 11
}}""",

    "BIOGRAPHICAL_DOSSIER": """This section evaluates a scholar using quotes from rijal books.

Extract:
{{
  "subject_scholar": {{
    "name_arabic": "full name",
    "name_transliterated": "romanized",
    "death_ah": null
  }},
  "argumentative_purpose": "why is this scholar being evaluated here",
  "evaluations": [
    {{
      "evaluator": "who made the judgment",
      "evaluator_death_ah": null,
      "source_book": "which rijal book",
      "term_arabic": "the jarh/ta'dil term (ثقة، كذاب، etc)",
      "category": "positive or negative",
      "verbatim_arabic": "exact Arabic quote (first 200 chars)"
    }}
  ]
}}""",

    "AUTHOR_RESPONSE": """This section is the author's response (اقول) to an opponent's claim.

Extract:
{{
  "target_claim": "what claim is being responded to",
  "approach": "SANAD/DALALAH/BIOGRAPHICAL/CONTRADICTION/LINGUISTIC",
  "key_arguments": ["list of main points made"],
  "conclusion": "the verdict — مخدوش/باطل/etc",
  "sources_cited": [{{"name": "...", "author": "...", "purpose": "..."}}]
}}""",

    "DEHLAVI_CLAIM": """This section quotes Dehlavi's (Shah Sahib's) claim.

Extract:
{{
  "claimant": "Shah Abdul Aziz al-Dihlawi or other",
  "claim_verbatim": "the verbatim Farsi/Arabic text of the claim (first 300 chars)",
  "claim_summary": "English summary",
  "attack_type": "AUTHENTICITY_DENIAL/LINGUISTIC/CHAIN_ATTACK/FABRICATION/MEANING_ATTACK",
  "source": "Tuhfat al-Ithna Ashariyya or other book"
}}""",

    "DEHLAVI_RESPONSE": """This section responds to Dehlavi's claim.

Extract:
{{
  "target_claim": "which Dehlavi claim is being answered",
  "response_summary": "English summary of the response",
  "key_arguments": ["main counter-points"],
  "sources_cited": [{{"name": "...", "author": "...", "purpose": "..."}}]
}}""",

    "TANBIH": """This is an authorial notice/digression (تنبيه).

Extract:
{{
  "title": "heading text if any",
  "topic_summary": "English summary of what this notice is about (2-3 sentences)",
  "related_to": "which preceding section or argument this relates to",
  "key_points": ["main points made"]
}}""",

    "TAMHID": """This is the author's introduction/preface to the volume.

Extract:
{{
  "summary": "English summary of the preface (3-5 sentences)",
  "hadith_text_quoted": "the Arabic hadith text as stated by the author",
  "opponent_quoted": "which opponent is cited and what they said",
  "opponent_claim_verbatim": "verbatim Arabic/Farsi of opponent's denial (first 300 chars)",
  "authors_stated_plan": "what the author says he will do in this volume"
}}""",

    "AQIDAH": """This section presents Sunni scholars' beliefs about a specific Imam.

Extract:
{{
  "imam_discussed": "which Imam this section is about",
  "scholars_quoted": [
    {{
      "scholar": "name",
      "death_ah": null,
      "book": "source book",
      "quote_summary": "what they said about this Imam"
    }}
  ],
  "argumentative_purpose": "why these Sunni beliefs are cited here"
}}""",

    "ILZAM": """This is a binding argument (الزام وافحام) — using the opponent's own logic against them.

Extract:
{{
  "target": "who is being bound by their own argument",
  "opponents_position": "what the opponent claims",
  "binding_argument": "how the author turns it against them",
  "sources_cited": [{{"name": "...", "author": "..."}}]
}}""",
}

# Skip these — no LLM needed
SKIP_TYPES = {"TABLE_OF_CONTENTS", "APPENDIX"}


# ── API call ──────────────────────────────────────────────────────

def call_grok(system, prompt, max_tokens=8192):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")

    response = client.chat.completions.create(
        model="grok-4-1-fast-non-reasoning",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    text = response.choices[0].message.content
    usage = response.usage
    return text, {
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
    }


def call_gemini_flash_lite(system, prompt, max_tokens=8192):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.1,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
        ),
    )
    meta = response.usage_metadata
    return response.text, {
        "input_tokens": meta.prompt_token_count if meta else 0,
        "output_tokens": meta.candidates_token_count if meta else 0,
    }


def parse_section(sec, cache_dir, hadith_name):
    """Parse a single section. Returns parsed data or None."""
    sec_type = sec["type"]
    sec_id = sec["id"]

    # Skip types that don't need LLM
    if sec_type in SKIP_TYPES:
        return {"type": sec_type, "skipped": True, "reason": "no LLM needed"}

    # Check cache
    cache_file = cache_dir / f"section-{sec_id:03d}.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # Get prompt template
    prompt_template = PROMPTS.get(sec_type)
    if not prompt_template:
        # Unknown type — use a generic extraction
        prompt_template = """Extract the key content from this section:
{{
  "summary": "English summary (2-3 sentences)",
  "key_points": ["main points"],
  "sources_cited": [{{"name": "...", "author": "..."}}]
}}"""

    prompt = f"""Analyze this section from Volume 23 of Abaqat al-Anwar (defending {hadith_name}).
Section type: {sec_type}
Lines: {sec['start_line']}-{sec['end_line']}

{prompt_template}

HERE IS THE SECTION TEXT:

{sec['text']}"""

    # Try Grok first, fallback to Flash Lite
    MAX_RETRIES = 2
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw, stats = call_grok(SYSTEM, prompt)
            data = json.loads(raw)
            data["_meta"] = {"model": "grok", "tokens": stats}
            # Cache it
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        except (json.JSONDecodeError, Exception) as e:
            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue
            # Fallback to Flash Lite
            try:
                raw, stats = call_gemini_flash_lite(SYSTEM, prompt)
                data = json.loads(raw)
                data["_meta"] = {"model": "flash-lite", "tokens": stats}
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return data
            except Exception as e2:
                return {"_error": str(e2), "type": sec_type}


# ── Phase 2: Build registries ────────────────────────────────────

def build_registries(sections, parsed_data):
    """Build unified scholar and book registries from parsed sections."""
    scholars = {}  # keyed by transliterated name
    books = {}     # keyed by transliterated name

    def add_scholar(name_t, name_a=None, death=None, role=None):
        if not name_t or name_t in ('null', 'None', '?', ''):
            return
        key = name_t.strip()
        if key not in scholars:
            scholars[key] = {"name_transliterated": key, "name_arabic": name_a, "death_ah": death, "roles": set()}
        if name_a and not scholars[key]["name_arabic"]:
            scholars[key]["name_arabic"] = name_a
        if death and not scholars[key]["death_ah"]:
            scholars[key]["death_ah"] = death
        if role:
            scholars[key]["roles"].add(role)

    def add_book(name_t, name_a=None, author=None, btype=None):
        if not name_t or name_t in ('null', 'None', '?', ''):
            return
        key = name_t.strip()
        if key not in books:
            books[key] = {"name_transliterated": key, "name_arabic": name_a, "author": author, "type": btype}
        if name_a and not books[key]["name_arabic"]:
            books[key]["name_arabic"] = name_a
        if author and not books[key]["author"]:
            books[key]["author"] = author

    for sec, parsed in zip(sections, parsed_data):
        if not parsed or parsed.get("skipped") or parsed.get("_error"):
            continue

        sec_type = sec["type"]

        if sec_type == "NARRATOR_CITATION":
            n = parsed.get("narrator", {})
            add_scholar(n.get("name_transliterated"), n.get("name_arabic"), n.get("death_ah"), "narrator")
            b = parsed.get("source_book", {})
            add_book(b.get("name_transliterated"), b.get("name_arabic"), n.get("name_transliterated"), b.get("book_type"))
            for ab in parsed.get("additional_books_cited", []):
                add_book(ab.get("name_transliterated"), ab.get("name_arabic"), ab.get("author"))

        elif sec_type == "BIOGRAPHICAL_DOSSIER":
            subj = parsed.get("subject_scholar", {})
            add_scholar(subj.get("name_transliterated"), subj.get("name_arabic"), subj.get("death_ah"), "dossier_subject")
            for ev in parsed.get("evaluations", []):
                add_scholar(ev.get("evaluator"), None, ev.get("evaluator_death_ah"), "evaluator")
                add_book(ev.get("source_book"), None, ev.get("evaluator"))

        elif sec_type == "DALALAH":
            for proof in parsed.get("proofs", []):
                for src in proof.get("sources_cited", []):
                    add_book(src.get("name"), None, src.get("author"))

        elif sec_type in ("AUTHOR_RESPONSE", "DEHLAVI_RESPONSE", "ILZAM"):
            for src in parsed.get("sources_cited", []):
                add_book(src.get("name"), None, src.get("author"))

        elif sec_type == "AQIDAH":
            for sq in parsed.get("scholars_quoted", []):
                add_scholar(sq.get("scholar"), None, sq.get("death_ah"), "authority")
                add_book(sq.get("book"), None, sq.get("scholar"))

    # Convert sets to lists for JSON
    for s in scholars.values():
        s["roles"] = sorted(s["roles"])

    return scholars, books


# ── Phase 3: Map existing citations to sections ──────────────────

def map_citations_to_sections(sections, citations_file):
    """Map previously extracted citations to structural sections by line overlap."""
    if not citations_file.exists():
        return {}

    with open(citations_file, "r", encoding="utf-8") as f:
        cdata = json.load(f)

    citations = cdata.get("citations", [])
    section_citations = defaultdict(list)

    for c in citations:
        lines_str = c.get("_lines", "")
        if not lines_str or "-" not in lines_str:
            continue
        c_start, c_end = map(int, lines_str.split("-"))

        # Find which section this citation falls in
        for sec in sections:
            if c_start >= sec["start_line"] and c_start <= sec["end_line"]:
                section_citations[sec["id"]].append(c)
                break

    return dict(section_citations)


# ── Main ──────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", type=int, required=True)
    args = parser.parse_args()

    vol = args.volume
    hadith_en, hadith_ar, focus = HADITH_MAP.get(vol, ("Unknown", "", ""))

    print(f"Full parse of Volume {vol}: {hadith_en} ({focus})")

    # Load text
    path = VOLUMES_DIR / f"abaghaat al'anwaar {vol}_djvu.txt"
    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"  {len(lines):,} lines, {sum(len(l) for l in lines):,} chars")

    # Phase 1: Detect sections
    print(f"\nPhase 1: Detecting sections...")
    sections = detect_sections(lines)
    from collections import Counter
    type_counts = Counter(s["type"] for s in sections)
    print(f"  Found {len(sections)} sections:")
    for t, c in type_counts.most_common():
        print(f"    {t}: {c}")

    # Phase 1b: Parse each section with LLM
    print(f"\nPhase 1b: Parsing sections with LLM...")
    cache_dir = OUTPUT_DIR / f"vol{vol:02d}-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    total_stats = {"input_tokens": 0, "output_tokens": 0, "cached": 0, "parsed": 0, "errors": 0}
    parsed_data = []

    for sec in sections:
        label = f"  [{sec['id']:>3}/{len(sections)}] {sec['type']:<22} L{sec['start_line']:>5}-{sec['end_line']:>5}"

        if sec["type"] in SKIP_TYPES:
            print(f"{label} SKIP")
            parsed_data.append({"type": sec["type"], "skipped": True})
            continue

        cache_file = cache_dir / f"section-{sec['id']:03d}.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            parsed_data.append(data)
            total_stats["cached"] += 1
            print(f"{label} CACHED")
            continue

        print(f"{label}", end=" ", flush=True)
        result = parse_section(sec, cache_dir, hadith_en)
        parsed_data.append(result)

        if result and not result.get("_error"):
            meta = result.get("_meta", {})
            tokens = meta.get("tokens", {})
            total_stats["input_tokens"] += tokens.get("input_tokens", 0)
            total_stats["output_tokens"] += tokens.get("output_tokens", 0)
            total_stats["parsed"] += 1
            model = meta.get("model", "?")
            print(f"✓ ({model}, {tokens.get('output_tokens', 0)} out)")
        else:
            total_stats["errors"] += 1
            print(f"✗ {result.get('_error', 'unknown error')[:60]}")

    in_cost = (total_stats["input_tokens"] / 1_000_000) * 0.20
    out_cost = (total_stats["output_tokens"] / 1_000_000) * 0.50
    print(f"\n  Phase 1 complete: {total_stats['parsed']} parsed, {total_stats['cached']} cached, {total_stats['errors']} errors")
    print(f"  Tokens: {total_stats['input_tokens']:,} in + {total_stats['output_tokens']:,} out")
    print(f"  Cost: ${in_cost + out_cost:.4f}")

    # Phase 2: Build registries
    print(f"\nPhase 2: Building scholar and book registries...")
    scholars, books = build_registries(sections, parsed_data)
    print(f"  Scholars: {len(scholars)} | Books: {len(books)}")

    # Phase 2b: Map existing citations
    print(f"\nPhase 2b: Mapping citations to sections...")
    citations_file = REPO_ROOT / "docs" / "citation-extraction" / f"vol{vol:02d}-grok.json"
    section_citations = map_citations_to_sections(sections, citations_file)
    total_mapped = sum(len(v) for v in section_citations.values())
    print(f"  Mapped {total_mapped} citations to {len(section_citations)} sections")

    # Phase 3: Assemble final JSON
    print(f"\nPhase 3: Assembling final parsed volume...")
    output = {
        "volume": vol,
        "hadith": {
            "name_english": hadith_en,
            "name_arabic": hadith_ar,
            "focus": focus,
        },
        "total_lines": len(lines),
        "total_sections": len(sections),
        "sections": [],
        "scholars": scholars,
        "books": books,
        "stats": {
            "narrator_citations": type_counts.get("NARRATOR_CITATION", 0),
            "dalalah_proofs": 0,
            "biographical_dossiers": type_counts.get("BIOGRAPHICAL_DOSSIER", 0),
            "author_responses": type_counts.get("AUTHOR_RESPONSE", 0),
            "tanbih_notices": type_counts.get("TANBIH", 0),
            "dehlavi_sections": type_counts.get("DEHLAVI_CLAIM", 0) + type_counts.get("DEHLAVI_RESPONSE", 0),
            "total_citations_mapped": total_mapped,
            "unique_scholars": len(scholars),
            "unique_books": len(books),
        },
    }

    for sec, parsed in zip(sections, parsed_data):
        sec_out = {
            "id": sec["id"],
            "type": sec["type"],
            "raw_heading": sec["raw_heading"],
            "start_line": sec["start_line"],
            "end_line": sec["end_line"],
            "line_count": sec["line_count"],
            "char_count": sec["char_count"],
            "parsed": parsed if not parsed.get("skipped") else None,
            "citations": section_citations.get(sec["id"], []),
        }
        output["sections"].append(sec_out)

        # Count dalalah proofs
        if sec["type"] == "DALALAH" and parsed:
            output["stats"]["dalalah_proofs"] = parsed.get("total_proofs", len(parsed.get("proofs", [])))

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"vol{vol:02d}-parsed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path.relative_to(REPO_ROOT)}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"  VOLUME {vol} PARSE COMPLETE")
    print(f"{'='*60}")
    print(f"  Hadith: {hadith_en} ({hadith_ar})")
    print(f"  Sections: {len(sections)} ({type_counts.most_common()})")
    print(f"  Scholars: {len(scholars)} | Books: {len(books)}")
    print(f"  Citations mapped: {total_mapped}")
    s = output["stats"]
    print(f"  Narrator citations: {s['narrator_citations']}")
    print(f"  Dalalah proofs: {s['dalalah_proofs']}")
    print(f"  Biographical dossiers: {s['biographical_dossiers']}")
    print(f"  Author responses: {s['author_responses']}")
    print(f"  Tanbih notices: {s['tanbih_notices']}")
    print(f"  Output: {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
