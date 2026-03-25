#!/usr/bin/env python3
"""
Analyze Abaqat al-Anwar volumes against Dehlavi's Chapter 7 claims.
Sends each volume to Gemini 3.1 Pro to catalog how the author responds
to each of Dehlavi's arguments.
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
ARGUMENT_MAP = REPO_ROOT / "docs" / "tuhfat-chapter7-argument-map.json"
OUTPUT_DIR = REPO_ROOT / "docs" / "abaqat-responses"

# All 23 volumes
VOLUMES = list(range(1, 24))

SYSTEM_INSTRUCTION = """You are an expert Islamic studies scholar with deep knowledge of Sunni-Shia polemical literature, classical Farsi, and Arabic.

You are analyzing volumes of Abaqat al-Anwar (عبقات الانوار) by Mir Hamid Husain (d. 1306 AH). This book is a systematic refutation of Chapter 7 (باب هفتم در امامت) of Tuhfat al-Ithna Ashariyya by Shah Abdul Aziz al-Dihlawi.

The text is OCR'd Farsi with embedded Arabic — expect OCR errors but the content is recoverable.

You have been given Dehlavi's argument map (his claims, the verses and hadiths he refuted, and his refutation strategies). Your job is to identify how this specific volume of Abaqat RESPONDS to those claims."""


def load_argument_map():
    with open(ARGUMENT_MAP, "r", encoding="utf-8") as f:
        return json.load(f)


def load_volume(vol_num):
    path = ABAQAT_DIR / f"abaghaat al'anwaar {vol_num}_djvu.txt"
    if not path.exists():
        return None, path
    with open(path, "r", encoding="utf-8") as f:
        return f.read(), path


def build_dehlavi_summary(arg_map):
    """Build a concise summary of Dehlavi's claims for the prompt."""
    lines = ["DEHLAVI'S KEY CLAIMS FROM TUHFAT CHAPTER 7:\n"]

    lines.append("QURANIC VERSES HE REFUTED:")
    for v in arg_map.get("quranic_verses_refuted", []):
        name = v.get("verse_name_common", "")
        ref = v.get("surah_ayah", "")
        shia = v.get("shia_argument", "")
        lines.append(f"  - {name} ({ref}): Shia say: {shia}")
        for r in v.get("dehlavi_refutations", [])[:2]:
            lines.append(f"    Dehlavi's attack: {r}")

    lines.append("\nHADITHS HE REFUTED:")
    for h in arg_map.get("hadiths_refuted", []):
        name = h.get("hadith_name", "")
        shia = h.get("shia_argument", "")
        lines.append(f"  - {name}: Shia say: {shia}")
        attack = h.get("dehlavi_authenticity_attack", "")
        if attack:
            lines.append(f"    Dehlavi's attack: {attack}")

    lines.append("\nRATIONAL ARGUMENTS HE REFUTED:")
    for ra in arg_map.get("rational_arguments_refuted", []):
        claim = ra.get("shia_claim", "")
        rebuttal = ra.get("dehlavi_rebuttal", "")
        lines.append(f"  - Shia: {claim}")
        lines.append(f"    Dehlavi: {rebuttal}")

    lines.append("\nHIS RHETORICAL STRATEGIES:")
    for s in arg_map.get("key_rhetorical_strategies", []):
        lines.append(f"  - {s}")

    return "\n".join(lines)


PROMPT_TEMPLATE = """Analyze this volume of Abaqat al-Anwar and catalog how the author responds to Dehlavi's claims.

{dehlavi_summary}

---

For this volume, extract:

1. **Which hadith does this volume defend?** (e.g., Ghadir, Manzila, Thaqalayn, etc.)
2. **Which specific Dehlavi claims does the author address?** Map each response to the corresponding Dehlavi claim above.
3. **What is the author's approach for each response?** Categories:
   - SANAD_DEFENSE: Proving the hadith chain is authentic
   - DALALAH_DEFENSE: Proving the hadith meaning supports Imamate
   - BIOGRAPHICAL_DOSSIER: Building a tarjama of a narrator/scholar from multiple rijal sources
   - CONTRADICTION_EXPOSURE: Showing the opponent contradicts himself or his own sources
   - LINGUISTIC_ANALYSIS: Arabic grammar/lexicon arguments
   - REBUTTAL_LINEAGE: Citing prior scholars who already answered this claim
   - ARGUMENT_LINEAGE: Tracing who originated and copied the claim
   - COUNTER_CITATION: Using Sunni sources as evidence for the Shia position
4. **Biographical dossiers (تراجم)**: List any scholars whose biographies are compiled with cross-references from multiple rijal books
5. **Key scholars mentioned** as opponents or authorities
6. **Books cited** as evidence

Return structured JSON:

{{
  "volume_number": {vol_num},
  "hadith_defended": "name of the hadith this volume defends",
  "volume_section": "Sanad or Dalalat or other",
  "overview": "brief description of this volume's content and approach",
  "responses_to_dehlavi": [
    {{
      "dehlavi_claim_addressed": "which specific claim from Dehlavi",
      "author_response_summary": "what the author argues in response",
      "response_type": "SANAD_DEFENSE | DALALAH_DEFENSE | BIOGRAPHICAL_DOSSIER | CONTRADICTION_EXPOSURE | LINGUISTIC_ANALYSIS | REBUTTAL_LINEAGE | ARGUMENT_LINEAGE | COUNTER_CITATION",
      "key_evidence_cited": ["specific sources or arguments used"]
    }}
  ],
  "biographical_dossiers": [
    {{
      "scholar_name": "name of scholar evaluated",
      "rijal_sources_cited": ["list of rijal books used"],
      "evaluation_summary": "positive/negative and key judgments"
    }}
  ],
  "argument_lineage_traced": [
    {{
      "claim": "the claim being traced",
      "chain": ["Scholar A (d.XXX) -> Scholar B (d.XXX) -> ..."]
    }}
  ],
  "rebuttal_lineage_cited": [
    {{
      "prior_scholar": "name",
      "work": "book title",
      "what_they_refuted": "which claim they addressed"
    }}
  ],
  "scholars_mentioned": ["list"],
  "books_cited": ["list"]
}}

HERE IS THE COMPLETE TEXT OF VOLUME {vol_num}:

"""


def analyze_volume(vol_num, text, dehlavi_summary):
    prompt = PROMPT_TEMPLATE.format(
        dehlavi_summary=dehlavi_summary,
        vol_num=vol_num,
    ) + text

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=65536,
                response_mime_type="application/json",
            ),
        )
        if response.text:
            return json.loads(response.text)
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def generate_volume_markdown(data):
    lines = []
    vol = data.get("volume_number", "?")
    lines.append(f"# Abaqat al-Anwar — Volume {vol} Response Analysis")
    lines.append("")
    lines.append(f"**Hadith defended:** {data.get('hadith_defended', 'Unknown')}")
    lines.append(f"**Section:** {data.get('volume_section', 'Unknown')}")
    lines.append(f"**Analyzed by:** Gemini 3.1 Pro")
    lines.append("")
    if data.get("overview"):
        lines.append(f"## Overview")
        lines.append(data["overview"])
        lines.append("")

    responses = data.get("responses_to_dehlavi", [])
    if responses:
        lines.append(f"## Responses to Dehlavi ({len(responses)})")
        lines.append("")
        for i, r in enumerate(responses, 1):
            lines.append(f"### Response {i}: {r.get('dehlavi_claim_addressed', '')}")
            lines.append(f"**Type:** {r.get('response_type', '')}")
            lines.append(f"**Author's response:** {r.get('author_response_summary', '')}")
            evidence = r.get("key_evidence_cited", [])
            if evidence:
                lines.append(f"**Evidence:** {', '.join(evidence)}")
            lines.append("")

    dossiers = data.get("biographical_dossiers", [])
    if dossiers:
        lines.append(f"## Biographical Dossiers ({len(dossiers)})")
        lines.append("")
        for d in dossiers:
            lines.append(f"- **{d.get('scholar_name', '')}** — {d.get('evaluation_summary', '')}")
            sources = d.get("rijal_sources_cited", [])
            if sources:
                lines.append(f"  Sources: {', '.join(sources)}")
        lines.append("")

    arg_lineage = data.get("argument_lineage_traced", [])
    if arg_lineage:
        lines.append(f"## Argument Lineages Traced ({len(arg_lineage)})")
        lines.append("")
        for a in arg_lineage:
            lines.append(f"- **{a.get('claim', '')}**")
            for c in a.get("chain", []):
                lines.append(f"  {c}")
        lines.append("")

    rebuttal = data.get("rebuttal_lineage_cited", [])
    if rebuttal:
        lines.append(f"## Prior Rebuttals Cited ({len(rebuttal)})")
        lines.append("")
        for r in rebuttal:
            lines.append(f"- **{r.get('prior_scholar', '')}** in *{r.get('work', '')}*: {r.get('what_they_refuted', '')}")
        lines.append("")

    scholars = data.get("scholars_mentioned", [])
    if scholars:
        lines.append(f"## Scholars Mentioned ({len(scholars)})")
        lines.append("")
        for s in sorted(scholars):
            lines.append(f"- {s}")
        lines.append("")

    books = data.get("books_cited", [])
    if books:
        lines.append(f"## Books Cited ({len(books)})")
        lines.append("")
        for b in sorted(books):
            lines.append(f"- {b}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Abaqat al-Anwar — Response Catalog (All Volumes)")
    print("=" * 60)

    # Load Dehlavi's argument map
    print(f"\nLoading Dehlavi's argument map...")
    arg_map = load_argument_map()
    dehlavi_summary = build_dehlavi_summary(arg_map)
    print(f"  {len(dehlavi_summary)} chars of context")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []

    for vol_num in VOLUMES:
        text, path = load_volume(vol_num)
        if text is None:
            print(f"\nVolume {vol_num}: FILE NOT FOUND ({path})")
            continue

        chars = len(text)
        lines_count = text.count("\n")
        print(f"\nVolume {vol_num}: {chars:,} chars, {lines_count:,} lines")
        print(f"  Sending to {MODEL}...")

        result = analyze_volume(vol_num, text, dehlavi_summary)

        if result:
            nr = len(result.get("responses_to_dehlavi", []))
            nd = len(result.get("biographical_dossiers", []))
            ns = len(result.get("scholars_mentioned", []))
            print(f"  Found: {nr} responses, {nd} dossiers, {ns} scholars")
            print(f"  Hadith: {result.get('hadith_defended', '?')}, Section: {result.get('volume_section', '?')}")

            # Save individual volume JSON
            vol_json = OUTPUT_DIR / f"volume-{vol_num:02d}.json"
            with open(vol_json, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # Save individual volume markdown
            vol_md = OUTPUT_DIR / f"volume-{vol_num:02d}.md"
            md = generate_volume_markdown(result)
            with open(vol_md, "w", encoding="utf-8") as f:
                f.write(md)

            all_results.append(result)
        else:
            print(f"  FAILED")

    # Save combined results
    combined_json = OUTPUT_DIR / "all-volumes-combined.json"
    with open(combined_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Volumes analyzed: {len(all_results)} / {len(VOLUMES)}")
    total_responses = sum(len(r.get("responses_to_dehlavi", [])) for r in all_results)
    total_dossiers = sum(len(r.get("biographical_dossiers", [])) for r in all_results)
    total_scholars = len(set(s for r in all_results for s in r.get("scholars_mentioned", [])))
    total_books = len(set(b for r in all_results for b in r.get("books_cited", [])))
    print(f"  Total responses to Dehlavi: {total_responses}")
    print(f"  Total biographical dossiers: {total_dossiers}")
    print(f"  Unique scholars mentioned: {total_scholars}")
    print(f"  Unique books cited: {total_books}")

    print(f"\n  Volume-by-volume:")
    for r in all_results:
        v = r.get("volume_number", "?")
        h = r.get("hadith_defended", "?")
        s = r.get("volume_section", "?")
        nr = len(r.get("responses_to_dehlavi", []))
        nd = len(r.get("biographical_dossiers", []))
        print(f"    Vol {v:>2}: {h:<30} ({s:<10}) — {nr} responses, {nd} dossiers")

    print(f"\nResults saved to: {OUTPUT_DIR}/")
    print("Done!")


if __name__ == "__main__":
    main()
