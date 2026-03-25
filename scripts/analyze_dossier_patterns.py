#!/usr/bin/env python3
"""
Deep analysis of biographical dossier (ترجمه) patterns in Abaqat al-Anwar.
Uses Volume 3 (richest in dossiers — 54 ترجمه headings) and Volume 2 (43 headings).
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
MODEL = "gemini-3.1-pro-preview"
ABAQAT_DIR = REPO_ROOT / "AbaghaatAlanwaarfarsi"
OUTPUT = REPO_ROOT / "docs" / "abaqat-dossier-patterns.json"
OUTPUT_MD = REPO_ROOT / "docs" / "abaqat-dossier-patterns.md"

SYSTEM_INSTRUCTION = """You are an expert in Islamic rijal (biographical criticism) literature, classical Farsi, and Arabic hadith sciences. You are analyzing the biographical dossier sections (ترجمه) in Abaqat al-Anwar to identify their internal structure and recurring patterns. This is for designing a database schema.

The text is OCR'd Farsi with embedded Arabic. Expect OCR errors but the content is recoverable."""

PROMPT = """I need an EXHAUSTIVE analysis of the biographical dossier (ترجمه / tarjama) sections in this volume of Abaqat al-Anwar. These are the sections where the author compiles evaluations of a scholar from multiple Sunni rijal sources.

Analyze EVERY dossier you can find and extract the patterns:

1. **dossier_catalog**: List EVERY ترجمه section you find. For each give:
   - The exact heading text
   - The subject scholar (who is being evaluated)
   - The rijal authority (who is doing the evaluating)
   - The rijal source book
   - What argumentative purpose this dossier serves (why is the author evaluating this person here?)

2. **internal_structure_patterns**: Analyze the INTERNAL structure of the dossiers:
   - What data fields consistently appear? (name, kunya, nisba, birth date, death date, teachers, students, etc.)
   - How are jarh (criticism) evaluations formatted? Give real examples.
   - How are ta'dil (authentication) evaluations formatted? Give real examples.
   - Are evaluations always direct quotes (قال X: ...) or sometimes paraphrased?
   - Does the author add his own commentary within dossiers? How?
   - How does a dossier start and how does it end?

3. **multi_source_patterns**: When the author compiles MULTIPLE sources for ONE scholar:
   - How does he transition between sources?
   - Does he present them in a specific order (chronological? most authoritative first?)
   - Does he present positive evaluations first then negative, or mixed?
   - How does he synthesize/conclude after presenting multiple sources?

4. **evaluation_vocabulary**: Extract the COMPLETE list of jarh/ta'dil terms used:
   - Positive terms (ثقة, حافظ, امام, etc.) with examples
   - Negative terms (ضعیف, متروک, کذاب, etc.) with examples
   - The formulaic phrases used to introduce evaluations (قال..., و قال..., etc.)

5. **dossier_types**: Are there different TYPES of dossiers?
   - Full biographical entry (name, dates, teachers, students, evaluations)
   - Brief evaluation only (just a quote or two)
   - Comparative dossier (contrasting what different authorities say)
   - Polemical dossier (showing the opponent's own authorities contradict the opponent)

6. **argumentative_integration**: How are dossiers embedded in the argument?
   - What triggers the author to build a dossier? (opponent attacks a narrator? author needs to prove reliability?)
   - How does he transition FROM the argument INTO the dossier?
   - How does he transition FROM the dossier BACK to the argument?
   - Does he always draw an explicit conclusion from the dossier?

7. **cross_referencing_within_dossiers**: When the same scholar appears in multiple dossiers across the text:
   - Does the author note this? How?
   - Does he build cumulative cases across multiple dossiers?

Return structured JSON with real examples (verbatim Arabic/Farsi quotes from the text) for every pattern.

HERE IS THE COMPLETE TEXT:

"""


def main():
    # Use Volume 3 — richest in dossiers
    vol_num = 3
    path = ABAQAT_DIR / f"abaghaat al'anwaar {vol_num}_djvu.txt"

    print("=" * 60)
    print(f"Abaqat al-Anwar — Dossier Pattern Analysis (Volume {vol_num})")
    print("=" * 60)

    print(f"\nReading {path}...")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"  {len(text):,} chars, {text.count(chr(10)):,} lines")

    print(f"\nSending to {MODEL}...")
    print(f"  (Deep dossier analysis — may take a few minutes)")

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=PROMPT + text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=65536,
                response_mime_type="application/json",
            ),
        )
        result = json.loads(response.text)
        print("  Success!")
    except Exception as e:
        print(f"  Error: {e}")
        sys.exit(1)

    # Save JSON
    print(f"\nSaving JSON to {OUTPUT}...")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Generate markdown
    print(f"Saving Markdown to {OUTPUT_MD}...")
    md = ["# Abaqat al-Anwar — Biographical Dossier Patterns", ""]
    md.append(f"**Source:** Volume {vol_num}")
    md.append(f"**Analyzed by:** {MODEL}")
    md.append("")

    catalog = result.get("dossier_catalog", [])
    md.append(f"## Dossier Catalog ({len(catalog)} entries)")
    md.append("")
    for i, d in enumerate(catalog, 1):
        md.append(f"### {i}. {d.get('heading_text', '')}")
        md.append(f"- **Subject:** {d.get('subject_scholar', '')}")
        md.append(f"- **Authority:** {d.get('rijal_authority', '')}")
        md.append(f"- **Source book:** {d.get('rijal_source_book', '')}")
        md.append(f"- **Purpose:** {d.get('argumentative_purpose', '')}")
        md.append("")

    for key in ["internal_structure_patterns", "multi_source_patterns",
                 "evaluation_vocabulary", "dossier_types",
                 "argumentative_integration", "cross_referencing_within_dossiers"]:
        data = result.get(key)
        if data:
            title = key.replace("_", " ").title()
            md.append(f"## {title}")
            md.append("")
            md.append("```json")
            md.append(json.dumps(data, ensure_ascii=False, indent=2))
            md.append("```")
            md.append("")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # Summary
    print(f"\n  Dossiers found: {len(catalog)}")
    types_found = result.get("dossier_types", {})
    if isinstance(types_found, list):
        print(f"  Dossier types: {len(types_found)}")
    vocab = result.get("evaluation_vocabulary", {})
    pos = vocab.get("positive_terms", []) if isinstance(vocab, dict) else []
    neg = vocab.get("negative_terms", []) if isinstance(vocab, dict) else []
    print(f"  Positive evaluation terms: {len(pos)}")
    print(f"  Negative evaluation terms: {len(neg)}")

    print("\nDone!")


if __name__ == "__main__":
    main()
