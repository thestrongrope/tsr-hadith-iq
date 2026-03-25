#!/usr/bin/env python3
"""
translate_markdown.py

Translate a markdown file (Arabic/Farsi) into English using Google Gemini,
producing an interlaced output (Original -> Translation).

Usage:
    python scripts/translate_markdown.py --input processed/books/al-kafi-preface/preface-ar.md --output processed/books/al-kafi-preface/preface-interlaced.md
"""

import argparse
import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed. Run: pip install google-genai")
    sys.exit(1)

load_dotenv()

DEFAULT_MODEL = "models/gemini-3-flash-preview"
FALLBACK_MODELS = [
    "models/gemini-flash-latest",
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash",
]

TRANSLATION_GUIDELINES = """\
You are an expert translator specializing in Shia Islamic traditions, tasked with translating Arabic/Farsi texts into English with precision and respect for Shia perspectives.

Translation rules:
1. Formatting: Preserve existing markdown formatting.
2. Tradition structure: Preserve tradition numbers, book titles, chains of narration, and reference details.
3. Honorifics: Use "Messenger of Allah (peace be upon him and his holy progeny)" for the Prophet, "Ameerul Momineen, Imam Ali (peace be upon him)" for Imam Ali, and "Imam [Name] (peace be upon him)" for other Imams. For Sayyedah Zahra, write "Sayyedah Zahra (peace be upon her)." 
4. Qur'anic verses: Put verse citations in parentheses.
5. Shia perspective: Maintain a respectful Shia viewpoint throughout.
6. No extra commentary: Provide a direct translation only.
7. Technical terms: Preserve technical terms with transliteration in parentheses on first use where appropriate.
"""

def clean_response_text(raw: str) -> str:
    """Strip code fences."""
    raw = raw.strip()
    if raw.startswith('```'):
        code = re.sub(r'^```[a-zA-Z0-9]*', '', raw)
        code = code.replace('```', '')
        raw = code.strip()
    return raw

def translate_markdown(client, text: str, model: str) -> str:
    instruction = (
        f"{TRANSLATION_GUIDELINES}\n\n"
        "Task: Translate the following Markdown text from Arabic into English.\n"
        "Output Style: INTERLACED.\n"
        "For each paragraph, heading, or distinct block of text in the original:\n"
        "1. Output the original Arabic paragraph/heading exactly as is.\n"
        "2. Output the English translation of that paragraph/heading immediately below it.\n"
        "3. Separate them with a blank line.\n"
        "4. Preserve footnote markers if any, and translate the footnotes at the end similarly.\n"
        "Do not wrap the whole thing in a code block unless the original was. Just return the markdown content."
    )

    content = types.Content(role='user', parts=[
        types.Part.from_text(text=instruction),
        types.Part.from_text(text=f"INPUT TEXT:\n\n{text}")
    ])

    cfg = types.GenerateContentConfig(
        response_modalities=['TEXT'],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = None

    for current_model in models_to_try:
        try:
            if current_model != model:
                print(f"Retrying with fallback model: {current_model}")
            resp = client.models.generate_content(model=current_model, contents=content, config=cfg)
            return clean_response_text(resp.text)
        except Exception as e:
            print(f"Error calling Gemini with {current_model}: {e}")
            last_error = e

    if last_error:
        print(f"Translation failed after trying {len(models_to_try)} model(s).")
    return ""

def main():
    parser = argparse.ArgumentParser(description='Translate Markdown file to Interlaced Markdown')
    parser.add_argument('--input', type=Path, required=True, help='Input Markdown file')
    parser.add_argument('--output', type=Path, required=True, help='Output Markdown file')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='Gemini model to use')

    args = parser.parse_args()

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment or .env file")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if not args.input.exists():
        print(f"Error: Input file {args.input} not found.")
        sys.exit(1)

    print(f"Reading {args.input}...")
    text = args.input.read_text(encoding='utf-8')

    print(f"Translating with {args.model}...")
    translated_text = translate_markdown(client, text, model=args.model)

    if translated_text:
        print(f"Writing to {args.output}...")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(translated_text, encoding='utf-8')
        print("Done.")
    else:
        print("Translation failed.")

if __name__ == "__main__":
    main()
