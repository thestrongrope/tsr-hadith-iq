#!/usr/bin/env python3
"""
Deep structural/methodology analysis of a single Abaqat volume.
Goal: understand the PATTERNS of how the author constructs responses,
not just what he says — so we can define the data model.
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
OUTPUT = REPO_ROOT / "docs" / "abaqat-methodology-analysis.json"
OUTPUT_MD = REPO_ROOT / "docs" / "abaqat-methodology-analysis.md"

# Volume 1: has the preface where the author describes his own methodology
VOL_NUM = 1

SYSTEM_INSTRUCTION = """You are an expert in Islamic manuscript analysis, classical Farsi, and Arabic scholarly literature. You are analyzing a single volume of Abaqat al-Anwar to understand the STRUCTURAL METHODOLOGY — the recurring patterns the author uses to build his arguments. This is for designing a database schema, not for summarizing content.

The text is OCR'd Farsi with embedded Arabic. Expect OCR errors."""

PROMPT = """I need you to do a DEEP STRUCTURAL ANALYSIS of this volume of Abaqat al-Anwar. I don't need a content summary — I need to understand the PATTERNS and BUILDING BLOCKS the author uses so I can design a data model.

Analyze and return JSON covering:

1. **document_structure**: How is the volume physically organized?
   - What markers/headings divide the text into sections?
   - What is the hierarchy of section types?
   - What Farsi/Arabic keywords signal transitions between sections?
   - How are page references (ص:) used?

2. **argument_unit_types**: What are the DISTINCT TYPES of content units? For each type:
   - What is the Farsi/Arabic label or heading pattern?
   - What is its typical length (lines)?
   - What does it contain?
   - How does it relate to other unit types?
   - Give 2-3 real examples (verbatim headings from the text)

   Look specifically for:
   - "اشاره" (remark) sections
   - "ترجمه" (biography) sections — what is their internal structure?
   - Quotation blocks (opponent's words vs author's words)
   - "جواب" (response) sections
   - "مدایح" (praises) and "معایب" (faults) sections
   - Numbered arguments (اول، دوم، سوم or اولا، ثانیا)
   - Footnote/reference patterns

3. **quotation_system**: How does the author mark different voices?
   - How are opponent's words introduced and delimited?
   - How are Sunni source quotations introduced?
   - How are prior Shia scholars' rebuttals introduced?
   - How does the author signal his own commentary?
   - What punctuation/markers separate voices? (guillemets «», brackets [], etc.)

4. **biographical_dossier_structure**: For the ترجمه (tarjama/biography) sections:
   - What is the heading pattern?
   - What data fields appear inside each dossier? (name, dates, teachers, students, evaluations)
   - How are evaluations (jarh/ta'dil) formatted?
   - How are multiple rijal sources cross-referenced within one dossier?
   - What is the typical structure: heading → source quote → evaluations → author's commentary?

5. **citation_patterns**: How does the author cite sources?
   - What format for book names?
   - What format for volume/page references?
   - How are inline footnotes marked?
   - How does he distinguish "I cite this source as evidence" vs "the opponent cites this source"?

6. **argument_flow_patterns**: What are the RECURRING SEQUENCES?
   - Does he always follow: state opponent's claim → cite prior rebuttals → add own evidence → conclude?
   - Or are there variations?
   - How does he transition between micro-arguments?
   - How does he signal "now I'm done with this point and moving to the next"?

7. **cross_reference_patterns**: How does the volume reference:
   - Other volumes of Abaqat?
   - Specific pages of the Tuhfat?
   - The opponent's other works?
   - His own earlier arguments within this volume?

8. **language_patterns**:
   - When does he switch from Farsi to Arabic?
   - Are there consistent patterns (e.g., opponent's words always in Arabic, author's commentary always in Farsi)?

Return the analysis as structured JSON. For each pattern identified, give REAL EXAMPLES from the text (verbatim quotes with approximate locations). This is critical — I need actual text examples, not abstract descriptions.

HERE IS THE COMPLETE TEXT OF VOLUME 3:

"""


def main():
    print("=" * 60)
    print(f"Abaqat al-Anwar — Deep Methodology Analysis (Volume {VOL_NUM})")
    print("=" * 60)

    path = ABAQAT_DIR / f"abaghaat al'anwaar {VOL_NUM}_djvu.txt"
    print(f"\nReading {path}...")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"  {len(text):,} chars, {text.count(chr(10)):,} lines")

    print(f"\nSending to {MODEL}...")
    print(f"  (Deep structural analysis — this may take a few minutes)")

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

    # Generate readable markdown
    print(f"Saving Markdown to {OUTPUT_MD}...")
    md_lines = ["# Abaqat al-Anwar — Methodology & Structure Analysis", ""]
    md_lines.append(f"**Source:** Volume {VOL_NUM}")
    md_lines.append(f"**Analyzed by:** {MODEL}")
    md_lines.append("")

    for section_key, section_data in result.items():
        title = section_key.replace("_", " ").title()
        md_lines.append(f"## {title}")
        md_lines.append("")
        md_lines.append(json.dumps(section_data, ensure_ascii=False, indent=2))
        md_lines.append("")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("\nDone!")


if __name__ == "__main__":
    main()
