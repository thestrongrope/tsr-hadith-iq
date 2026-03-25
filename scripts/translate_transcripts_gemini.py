#!/usr/bin/env python3
"""
Translate transcript text files to English using Gemini and combine them.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed. Run: pip install google-genai")
    sys.exit(1)

DEFAULT_MODEL = "models/gemini-3-flash-preview"

INSTRUCTION = (
    "Translate the following transcript into clear, fluent English. "
    "Retain Arabic phrases and formal Arabic statements in Arabic script exactly as written. "
    "Do not transliterate Arabic into Latin letters. "
    "Translate Urdu/Hindi and other non-Arabic content into English. "
    "Do NOT introduce honorifics or role words that are not explicitly present in the source (e.g., do not translate as 'our leaders' unless the source explicitly says leaders). "
    "Keep the intent of invocations and curses accurate and literal. "
    "Preserve paragraph breaks and keep proper names as written. "
    "Do not add commentary, headings, or extra text."
)


def split_into_chunks(text: str, max_chars: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    count = 0

    def flush():
        nonlocal current, count
        if current:
            chunks.append("\n\n".join(current))
            current = []
            count = 0

    for p in paragraphs:
        if len(p) > max_chars:
            flush()
            for i in range(0, len(p), max_chars):
                chunks.append(p[i:i + max_chars])
            continue

        if count + len(p) + 2 > max_chars:
            flush()

        current.append(p)
        count += len(p) + 2

    flush()
    return chunks


def translate_chunk(client, chunk: str, model: str) -> str:
    content = types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=INSTRUCTION),
            types.Part.from_text(text=chunk),
        ],
    )

    cfg = types.GenerateContentConfig(
        response_modalities=["TEXT"],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    resp = client.models.generate_content(model=model, contents=content, config=cfg)
    return (resp.text or "").strip()


def translate_file(client, path: Path, max_chars: int, model: str) -> str:
    text = path.read_text(encoding="utf-8")
    chunks = split_into_chunks(text, max_chars=max_chars)
    translated: list[str] = []

    for i, chunk in enumerate(chunks, start=1):
        print(f"  Translating chunk {i}/{len(chunks)} from {path.name}...")
        translated.append(translate_chunk(client, chunk, model=model))

    return "\n\n".join(t for t in translated if t)


def main():
    parser = argparse.ArgumentParser(description="Translate transcript files to English and combine")
    parser.add_argument("--inputs", nargs="+", type=Path, required=True, help="Input transcript files")
    parser.add_argument("--output", type=Path, required=True, help="Output English transcript")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Gemini model")
    parser.add_argument("--max-chars", type=int, default=3500, help="Max characters per chunk")

    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment or .env file")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    for path in args.inputs:
        if not path.exists():
            print(f"Error: Input file not found: {path}")
            sys.exit(1)

    combined: list[str] = []
    for path in args.inputs:
        print(f"Translating {path.name}...")
        combined.append(translate_file(client, path, max_chars=args.max_chars, model=args.model))

    output_text = "\n\n".join(t for t in combined if t)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_text, encoding="utf-8")
    print(f"Done. Wrote: {args.output}")


if __name__ == "__main__":
    main()
