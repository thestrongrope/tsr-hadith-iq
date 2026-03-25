#!/usr/bin/env python3
"""
Analyze Tuhfat al-Ithna Ashariyya Chapter 7 using Gemini.
Sends the entire chapter (~387KB) in one request — well within Gemini's 1M token context.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai not installed. Run: uv pip install google-genai")
    sys.exit(1)

client = genai.Client(api_key=api_key)

MODELS = ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview"]
CHAPTER_FILE = REPO_ROOT / "docs" / "tuhfat-chapter7-imamate.txt"
OUTPUT_JSON = REPO_ROOT / "docs" / "tuhfat-chapter7-argument-map.json"
OUTPUT_MD = REPO_ROOT / "docs" / "tuhfat-chapter7-argument-map.md"

SYSTEM_INSTRUCTION = """You are an expert Islamic studies scholar with deep knowledge of Sunni-Shia polemical literature, classical Farsi, and Arabic. You are analyzing Chapter 7 (باب هفتم در امامت — On Imamate) of the Tuhfat al-Ithna Ashariyya by Shah Abdul Aziz al-Dihlawi.

This chapter is where Dehlavi refutes Shia proofs for the Imamate of Ali ibn Abi Talib. He addresses three categories of Shia evidence:
1. Quranic verses (آیات) that Shia cite
2. Hadiths/traditions (احادیث) that Shia cite
3. Rational arguments (دلایل عقلیه) that Shia make

The text is OCR'd Farsi with embedded Arabic quotations — expect OCR errors but the content is recoverable."""

PROMPT = """Analyze the ENTIRE text of Chapter 7 of Tuhfat al-Ithna Ashariyya below. Extract its complete argument structure.

For each item, provide as much detail as possible. Do NOT summarize — be exhaustive.

Return structured JSON with this schema:

{
  "chapter_overview": "Brief description of the chapter's purpose and structure",
  "sunni_doctrines": [
    {"doctrine_number": 1, "title": "...", "summary": "...", "key_claim": "..."}
  ],
  "quranic_verses_refuted": [
    {
      "verse_number": 1,
      "verse_name_common": "e.g. Verse of Wilayah",
      "verse_arabic": "the Quranic text quoted",
      "surah_ayah": "e.g. al-Ma'idah 5:55",
      "shia_argument": "What Shia claim this verse proves",
      "dehlavi_refutations": ["First counter-argument", "Second counter-argument", "..."],
      "scholars_cited_by_dehlavi": ["names of scholars he cites in this refutation"]
    }
  ],
  "hadiths_refuted": [
    {
      "hadith_number": 1,
      "hadith_name": "e.g. Hadith al-Ghadir",
      "hadith_text_arabic": "key Arabic text of the hadith",
      "narrator_chain": "who narrated it and from which source",
      "shia_argument": "What Shia claim this hadith proves",
      "dehlavi_refutations": ["First counter-argument", "Second counter-argument", "..."],
      "dehlavi_authenticity_attack": "Does he attack the chain? How?"
    }
  ],
  "rational_arguments_refuted": [
    {
      "argument_number": 1,
      "shia_claim": "The rational argument Shia make",
      "dehlavi_rebuttal": "His counter-argument",
      "evidence_cited": "Any Quran/hadith/logic he uses"
    }
  ],
  "counter_evidence_for_abu_bakr": [
    {"evidence": "...", "source": "..."}
  ],
  "scholars_mentioned": ["list of ALL scholar names mentioned in the chapter"],
  "books_referenced": ["list of ALL book titles mentioned in the chapter"],
  "key_rhetorical_strategies": ["list of argumentative techniques Dehlavi uses"]
}

HERE IS THE COMPLETE TEXT OF CHAPTER 7:

"""


def generate_markdown(data):
    lines = []
    lines.append("# Tuhfat al-Ithna Ashariyya — Chapter 7 Argument Map")
    lines.append("")
    lines.append(f"**Source:** Tuhfat al-Ithna Ashariyya, Chapter 7 (باب هفتم در امامت)")
    lines.append(f"**Author:** Shah Abdul Aziz al-Dihlawi (d. 1239 AH)")
    lines.append(f"**Analyzed by:** {data.get('_model', 'Gemini')}")
    lines.append("")

    if data.get("chapter_overview"):
        lines.append(f"## Overview")
        lines.append(f"{data['chapter_overview']}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Sunni Doctrines
    doctrines = data.get("sunni_doctrines", [])
    if doctrines:
        lines.append(f"## Sunni Doctrines Stated ({len(doctrines)} عقائد)")
        lines.append("")
        for d in doctrines:
            n = d.get("doctrine_number", "")
            lines.append(f"### Doctrine {n}: {d.get('title', '')}")
            lines.append(f"{d.get('summary', '')}")
            if d.get("key_claim"):
                lines.append(f"**Key claim:** {d['key_claim']}")
            lines.append("")

    # Quranic Verses
    verses = data.get("quranic_verses_refuted", [])
    if verses:
        lines.append("---")
        lines.append("")
        lines.append(f"## Quranic Verses Refuted ({len(verses)} آیات)")
        lines.append("")
        for v in verses:
            n = v.get("verse_number", "")
            lines.append(f"### Verse {n}: {v.get('verse_name_common', '')}")
            if v.get("surah_ayah"):
                lines.append(f"**Reference:** {v['surah_ayah']}")
            if v.get("verse_arabic"):
                lines.append(f"**Arabic:** {v['verse_arabic']}")
            lines.append("")
            if v.get("shia_argument"):
                lines.append(f"**Shia argument:** {v['shia_argument']}")
                lines.append("")
            refutations = v.get("dehlavi_refutations", [])
            if refutations:
                lines.append(f"**Dehlavi's refutations ({len(refutations)}):**")
                for j, r in enumerate(refutations, 1):
                    lines.append(f"   {j}. {r}")
                lines.append("")
            scholars = v.get("scholars_cited_by_dehlavi", [])
            if scholars:
                lines.append(f"**Scholars cited:** {', '.join(scholars)}")
                lines.append("")

    # Hadiths
    hadiths = data.get("hadiths_refuted", [])
    if hadiths:
        lines.append("---")
        lines.append("")
        lines.append(f"## Hadiths Refuted ({len(hadiths)} احادیث)")
        lines.append("")
        for h in hadiths:
            n = h.get("hadith_number", "")
            lines.append(f"### Hadith {n}: {h.get('hadith_name', '')}")
            if h.get("hadith_text_arabic"):
                lines.append(f"**Text:** {h['hadith_text_arabic']}")
            if h.get("narrator_chain"):
                lines.append(f"**Chain/Source:** {h['narrator_chain']}")
            lines.append("")
            if h.get("shia_argument"):
                lines.append(f"**Shia argument:** {h['shia_argument']}")
                lines.append("")
            if h.get("dehlavi_authenticity_attack"):
                lines.append(f"**Authenticity attack:** {h['dehlavi_authenticity_attack']}")
                lines.append("")
            refutations = h.get("dehlavi_refutations", [])
            if refutations:
                lines.append(f"**Dehlavi's refutations ({len(refutations)}):**")
                for j, r in enumerate(refutations, 1):
                    lines.append(f"   {j}. {r}")
                lines.append("")

    # Rational Arguments
    rational = data.get("rational_arguments_refuted", [])
    if rational:
        lines.append("---")
        lines.append("")
        lines.append(f"## Rational Arguments Refuted ({len(rational)} دلایل عقلیه)")
        lines.append("")
        for ra in rational:
            n = ra.get("argument_number", "")
            lines.append(f"### Argument {n}")
            lines.append(f"**Shia claim:** {ra.get('shia_claim', '')}")
            lines.append(f"**Dehlavi's rebuttal:** {ra.get('dehlavi_rebuttal', '')}")
            if ra.get("evidence_cited"):
                lines.append(f"**Evidence cited:** {ra['evidence_cited']}")
            lines.append("")

    # Counter-evidence for Abu Bakr
    counter = data.get("counter_evidence_for_abu_bakr", [])
    if counter:
        lines.append("---")
        lines.append("")
        lines.append(f"## Counter-Evidence for Abu Bakr's Caliphate ({len(counter)} proofs)")
        lines.append("")
        for c in counter:
            lines.append(f"- **{c.get('source', '')}:** {c.get('evidence', '')}")
        lines.append("")

    # Scholars
    scholars = data.get("scholars_mentioned", [])
    if scholars:
        lines.append("---")
        lines.append("")
        lines.append(f"## Scholars Mentioned ({len(scholars)})")
        lines.append("")
        for s in sorted(scholars):
            lines.append(f"- {s}")
        lines.append("")

    # Books
    books = data.get("books_referenced", [])
    if books:
        lines.append("---")
        lines.append("")
        lines.append(f"## Books Referenced ({len(books)})")
        lines.append("")
        for b in sorted(books):
            lines.append(f"- {b}")
        lines.append("")

    # Rhetorical Strategies
    strategies = data.get("key_rhetorical_strategies", [])
    if strategies:
        lines.append("---")
        lines.append("")
        lines.append("## Rhetorical Strategies Used")
        lines.append("")
        for s in strategies:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Tuhfat Chapter 7 — Full Argument Structure Analyzer")
    print("=" * 60)

    # Read entire chapter
    print(f"\nReading {CHAPTER_FILE}...")
    with open(CHAPTER_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"  {len(text):,} chars, {text.count(chr(10)):,} lines")

    # Try models in order
    result = None
    model_used = None

    for model_name in MODELS:
        print(f"\nSending entire chapter to {model_name}...")
        print(f"  (This may take a minute — processing ~387KB of Farsi/Arabic text)")

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=PROMPT + text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=65536,
                    response_mime_type="application/json",
                ),
            )
            response_text = response.text
            if response_text:
                result = json.loads(response_text)
                model_used = model_name
                print(f"  Success with {model_name}!")
                break
            else:
                print(f"  Empty response from {model_name}")
        except Exception as e:
            print(f"  Error with {model_name}: {e}")
            continue

    if not result:
        print("\nFAILED: All models failed. Exiting.")
        sys.exit(1)

    result["_model"] = model_used

    # Summary
    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(f"{'=' * 60}")
    print(f"  Model used:         {model_used}")
    print(f"  Sunni doctrines:    {len(result.get('sunni_doctrines', []))}")
    print(f"  Quranic verses:     {len(result.get('quranic_verses_refuted', []))}")
    print(f"  Hadiths:            {len(result.get('hadiths_refuted', []))}")
    print(f"  Rational arguments: {len(result.get('rational_arguments_refuted', []))}")
    print(f"  Abu Bakr evidence:  {len(result.get('counter_evidence_for_abu_bakr', []))}")
    print(f"  Scholars mentioned: {len(result.get('scholars_mentioned', []))}")
    print(f"  Books referenced:   {len(result.get('books_referenced', []))}")

    # Save JSON
    print(f"\nSaving JSON to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Save Markdown
    print(f"Saving Markdown to {OUTPUT_MD}...")
    md = generate_markdown(result)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    print("\nDone!")


if __name__ == "__main__":
    main()
