#!/usr/bin/env python3
"""
Transcribe audio files to English using Google Gemini API.
Supports m4a, mp3, wav, and other audio formats.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

DEFAULT_MODEL = "models/gemini-3-flash-preview"

# Load .env from project root
REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"

def setup_gemini():
    """Initialize Gemini API client."""
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    else:
        load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment or .env file.")
        print(f"Checked path: {ENV_PATH}")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    return api_key

def get_mime_type(file_path: Path) -> str:
    """Get MIME type based on file extension."""
    ext = file_path.suffix.lower()
    mime_types = {
        '.m4a': 'audio/m4a',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.webm': 'audio/webm',
    }
    return mime_types.get(ext, 'audio/mpeg')

def upload_to_gemini(file_path: Path):
    """Upload file to Gemini and return uploaded file handle."""
    print(f"  Uploading {file_path.name}...")
    
    mime_type = get_mime_type(file_path)
    file_response = genai.upload_file(file_path, mime_type=mime_type)
    
    print(f"  File uploaded: {file_response.uri}")
    return file_response

def transcribe_audio(file_path: Path, output_dir: Path, language: str = "English", model_name: str = DEFAULT_MODEL) -> dict:
    """
    Transcribe audio file using Gemini API.
    
    Args:
        file_path: Path to audio file
        output_dir: Directory to save transcription
        language: Language to transcribe to (default: English)
    
    Returns:
        Dictionary with transcription details
    """
    print(f"\nTranscribing: {file_path.name}")
    
    # Upload file
    uploaded_file = upload_to_gemini(file_path)
    
    # Create prompt for transcription
    prompt = f"""Please transcribe this audio file with the main narrative in {language}.
Preserve all Arabic phrases, duas, Quranic verses, salutations, and formal statements in Arabic script exactly as spoken.
Do not transliterate Arabic into Latin letters.
Keep Urdu/Hindi speech translated into clear {language}, but retain Arabic segments in Arabic.
Provide a complete, accurate transcription with proper punctuation and paragraphs."""
    
    # Call Gemini API with model that supports audio
    print("  Sending to Gemini for transcription...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([
        prompt,
        uploaded_file,
    ])
    
    transcription = response.text
    
    # Save transcription
    output_file = output_dir / f"{file_path.stem}.transcription.{language.lower()}.txt"
    output_file.write_text(transcription)
    
    print(f"  ✓ Saved to: {output_file}")
    
    return {
        'file': file_path.name,
        'output': str(output_file),
        'language': language,
        'timestamp': datetime.now().isoformat(),
        'status': 'completed'
    }

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Gemini API"
    )
    parser.add_argument(
        'files',
        nargs='+',
        type=Path,
        help='Audio files to transcribe'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=REPO_ROOT / 'processed' / 'transcripts',
        help='Output directory for transcriptions'
    )
    parser.add_argument(
        '--language',
        default='English',
        help='Language to transcribe to (default: English)'
    )
    parser.add_argument(
        '--model',
        default=DEFAULT_MODEL,
        help=f'Gemini model to use (default: {DEFAULT_MODEL})'
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_gemini()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process files
    results = []
    for file_path in args.files:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            continue
        
        if not file_path.is_file():
            print(f"Error: Not a file: {file_path}")
            continue
        
        try:
            result = transcribe_audio(file_path, output_dir, args.language, args.model)
            results.append(result)
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append({
                'file': file_path.name,
                'status': 'failed',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("TRANSCRIPTION SUMMARY")
    print("="*60)
    success = sum(1 for r in results if r.get('status') == 'completed')
    failed = sum(1 for r in results if r.get('status') == 'failed')
    print(f"Successfully transcribed: {success}")
    print(f"Failed: {failed}")
    
    # Save results log
    log_file = output_dir / "transcription_log.json"
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nLog saved to: {log_file}")

if __name__ == '__main__':
    main()
