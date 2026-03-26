#!/usr/bin/env python3
"""
Parse a volume of Abaqat al-Anwar into its actual structural sections.
Uses Grok to interpret the TOC and section markers, then splits the
raw text into a structured JSON that can be consumed without further LLM calls.

Usage:
  uv run --with openai --with python-dotenv python scripts/parse_volume_structure.py --volume 23
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

VOLUMES_DIR = REPO_ROOT / "sources" / "abaqat" / "volumes-djvu"
OUTPUT_DIR = REPO_ROOT / "docs" / "volume-structure"

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

SYSTEM = """You are an expert in the structure of Abaqat al-Anwar by Mir Hamid Husain.
You will be given the FULL TEXT of a volume with LINE NUMBERS prepended to each line.
The text is OCR'd Farsi/Arabic with errors — expect garbled characters but content is recoverable.

Your task: identify every major section of this volume and report the EXACT LINE NUMBER
where each section begins. Look for:
- The table of contents (فهرست مطالب) near the start
- Section headings (often standalone lines, sometimes in guillemets «»)
- "اما" markers introducing new source citations
- "ترجمه" markers for biographical dossiers
- "اقول" for author's responses
- "كلام شاهصاحب" for Dehlavi's claims
- "جواب" for responses to claims
- Major topic transitions"""

PROMPT = """Analyze the FULL TEXT of Volume {vol_num} of Abaqat al-Anwar.
This volume covers: {hadith_name}

The text has LINE NUMBERS at the start of each line. Use these to report exact boundaries.

Identify every major section and subsection. For each section provide:
1. The EXACT line number where it starts
2. The section title in original Farsi/Arabic (cleaned from OCR errors)
3. An English translation
4. The section type (TAMHID, REFUTATION, NARRATOR_CHAIN, DALALAH, BIOGRAPHICAL_DOSSIER, DEHLAVI_CLAIM, AUTHOR_RESPONSE, HADITH_CITATION, SUPPLEMENTARY, APPENDIX, TABLE_OF_CONTENTS)
5. Parent section ID if it's a subsection (null for top-level)
6. A brief description of what this section contains

Return JSON:
{{
  "volume": {vol_num},
  "hadith": "{hadith_name}",
  "sections": [
    {{
      "id": "1",
      "start_line": 88,
      "title_original": "فهرست مطالب",
      "title_english": "Table of Contents",
      "section_type": "TABLE_OF_CONTENTS",
      "parent_id": null,
      "description": "Lists all sections of this volume"
    }}
  ]
}}

HERE IS THE FULL TEXT WITH LINE NUMBERS:

"""


def load_volume(vol_num):
    path = VOLUMES_DIR / f"abaghaat al'anwaar {vol_num}_djvu.txt"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_section_structure(vol_num, text_head):
    """Call Grok to parse the TOC into structured sections."""
    from openai import OpenAI

    api_key = os.getenv("GROK_API_KEY")
    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    hadith = HADITH_MAP.get(vol_num, "Unknown")
    prompt = PROMPT.format(vol_num=vol_num, hadith_name=hadith) + text_head

    for attempt in range(1, 4):
        label = f" (attempt {attempt})" if attempt > 1 else ""
        print(f"  Sending to Grok{label}...")
        t0 = time.time()
        response = client.chat.completions.create(
            model="grok-4-1-fast-non-reasoning",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=16384,
            response_format={"type": "json_object"},
        )
        elapsed = time.time() - t0
        usage = response.usage
        text = response.choices[0].message.content
        print(f"  Done in {elapsed:.1f}s ({usage.prompt_tokens:,} in, {usage.completion_tokens:,} out)")

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"  JSON error: {e}")
            if attempt < 3:
                print(f"  Retrying...")
                time.sleep(2)
            else:
                # Try to salvage partial JSON
                print(f"  Attempting partial JSON salvage...")
                # Find last complete object in the sections array
                idx = text.rfind('}')
                if idx > 0:
                    # Try to close the array and object
                    for suffix in ['}]}', '}]}\n', '}\n]}']:
                        try:
                            return json.loads(text[:idx+1] + ']}')
                        except json.JSONDecodeError:
                            continue
                raise


def normalize_arabic(text):
    """Strip diacritics, normalize whitespace and common OCR variants for fuzzy matching."""
    import re
    # Remove Arabic diacritics (tashkeel)
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]', '', text)
    # Normalize alef variants
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ٱ', 'ا')
    # Normalize teh marbuta / heh
    text = text.replace('ة', 'ه')
    # Normalize yaa variants
    text = text.replace('ي', 'ى').replace('ئ', 'ى')
    # Collapse all whitespace (spaces, tabs, ZWNJ, etc.)
    text = re.sub(r'[\s\u200c\u200d\u00a0]+', '', text)
    return text


def locate_sections(sections, full_text):
    """Find the line number where each section starts using fuzzy matching."""
    lines = full_text.split("\n")
    # Pre-compute normalized version of each line and multi-line windows
    norm_lines = [normalize_arabic(l) for l in lines]
    # Also build 3-line windows for matching across line breaks
    norm_windows = []
    for i in range(len(lines)):
        window = ''.join(norm_lines[i:i+3])
        norm_windows.append(window)

    results = []

    for sec in sections:
        anchor = sec.get("text_anchor", "")
        if not anchor or len(anchor) < 5:
            sec["start_line"] = None
            sec["anchor_found"] = False
            results.append(sec)
            continue

        norm_anchor = normalize_arabic(anchor)
        found = False

        # Try progressively shorter prefixes of the normalized anchor
        # Skip the TOC area (first ~250 lines are typically TOC/front matter)
        skip_lines = 230
        for frac in [1.0, 0.7, 0.5, 0.35]:
            search = norm_anchor[:max(5, int(len(norm_anchor) * frac))]
            for i in range(skip_lines, len(norm_windows)):
                if search in norm_windows[i]:
                    sec["start_line"] = i + 1  # 1-indexed
                    sec["anchor_found"] = True
                    if frac < 1.0:
                        sec["anchor_partial"] = True
                        sec["match_fraction"] = frac
                    found = True
                    break
            if found:
                break

        if not found:
            sec["start_line"] = None
            sec["anchor_found"] = False

        results.append(sec)

    # Sort by start_line and compute end_lines
    located = [s for s in results if s.get("start_line")]
    located.sort(key=lambda s: s["start_line"])
    for i, sec in enumerate(located):
        if i + 1 < len(located):
            sec["end_line"] = located[i + 1]["start_line"] - 1
        else:
            sec["end_line"] = len(lines)

    return results


def build_structured_volume(sections, full_text):
    """Attach the actual text content to each section."""
    lines = full_text.split("\n")
    for sec in sections:
        start = sec.get("start_line")
        end = sec.get("end_line")
        if start and end:
            sec["text"] = "\n".join(lines[start - 1:end])
            sec["line_count"] = end - start + 1
            sec["char_count"] = len(sec["text"])
        else:
            sec["text"] = None
            sec["line_count"] = 0
            sec["char_count"] = 0
    return sections


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", type=int, required=True)
    args = parser.parse_args()

    vol_num = args.volume
    hadith = HADITH_MAP.get(vol_num, "Unknown")
    print(f"Parsing structure of Volume {vol_num}: {hadith}")

    full_text = load_volume(vol_num)
    if not full_text:
        print(f"ERROR: Volume {vol_num} not found")
        sys.exit(1)

    total_lines = full_text.count("\n")
    print(f"  {len(full_text):,} chars, {total_lines:,} lines")

    # Send full text with line numbers to Grok (fits in 2M context)
    numbered_lines = [f"{i+1}\t{line}" for i, line in enumerate(full_text.split("\n"))]
    numbered_text = "\n".join(numbered_lines)
    print(f"  Numbered text: {len(numbered_text):,} chars")

    # Get section structure from Grok
    structure = get_section_structure(vol_num, numbered_text)
    sections = structure.get("sections", [])
    print(f"  Found {len(sections)} sections in TOC")

    # Sections already have start_line from Grok — just validate and compute end_lines
    print(f"  Validating section boundaries...")
    total_lines_count = len(full_text.split("\n"))
    # Sort by start_line
    sections = [s for s in sections if s.get("start_line")]
    sections.sort(key=lambda s: s["start_line"])
    # Compute end_lines
    for i, sec in enumerate(sections):
        if i + 1 < len(sections):
            sec["end_line"] = sections[i + 1]["start_line"] - 1
        else:
            sec["end_line"] = total_lines_count
        sec["anchor_found"] = True
    found = len(sections)
    print(f"  {found} sections with valid line numbers")

    # Attach text content
    sections = build_structured_volume(sections, full_text)

    # Build output
    output = {
        "volume": vol_num,
        "hadith": hadith,
        "total_lines": total_lines,
        "total_chars": len(full_text),
        "total_sections": len(sections),
        "sections_located": found,
        "sections": []
    }

    for sec in sections:
        # Don't include full text in the summary — save separately
        summary = {k: v for k, v in sec.items() if k != "text"}
        output["sections"].append(summary)

    # Save structure index
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = OUTPUT_DIR / f"vol{vol_num:02d}-structure.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  Saved structure: {index_path.relative_to(REPO_ROOT)}")

    # Save each section as a separate text file for easy consumption
    sections_dir = OUTPUT_DIR / f"vol{vol_num:02d}-sections"
    sections_dir.mkdir(parents=True, exist_ok=True)
    for sec in sections:
        if sec.get("text"):
            sec_id = sec["id"].replace(".", "-")
            sec_path = sections_dir / f"section-{sec_id}.txt"
            with open(sec_path, "w", encoding="utf-8") as f:
                f.write(sec["text"])

    # Print summary
    print(f"\n  {'ID':<6} {'Lines':>10} {'Type':<25} Title")
    print(f"  {'-'*6} {'-'*10} {'-'*25} {'-'*50}")
    for sec in sorted(sections, key=lambda s: s.get("start_line") or 99999):
        sid = sec["id"]
        stype = sec.get("section_type", "?")
        title = sec.get("title_english", "?")[:50]
        start = sec.get("start_line", "?")
        end = sec.get("end_line", "?")
        lines = sec.get("line_count", 0)
        marker = "✓" if sec.get("anchor_found") else "✗"
        print(f"  {marker} {sid:<5} {str(start)+'-'+str(end):>10} {stype:<25} {title}")

    print(f"\n  Section texts saved to: {sections_dir.relative_to(REPO_ROOT)}/")
    print("Done!")


if __name__ == "__main__":
    main()
