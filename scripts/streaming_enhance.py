#!/usr/bin/env python3
"""
Streaming processor - processes small sections and writes immediately.
This avoids output token limits by never asking for large outputs at once.
"""

import os
import sys
from pathlib import Path
from google import genai
from dotenv import load_dotenv

load_dotenv()

def process_small_section(client, original_section, english_section, section_num):
    """Process a very small section (15-20 lines) at a time"""
    
    prompt = f"""You are processing a small section of a lecture transcript.

SECTION {section_num}:

ORIGINAL (Arabic/Urdu):
{original_section}

ENGLISH TRANSLATION:
{english_section}

Task: Output the English text, but wherever there are Arabic verses, quotations, or prayers, insert the original Arabic text inline.

Output format: Just the processed text, no explanations or comments.

Processed text:"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={
                'temperature': 0.3,
                'max_output_tokens': 2048,  # Small output
                'response_modalities': ['TEXT']
            }
        )
        return response.text
    except Exception as e:
        print(f"    Error in section {section_num}: {e}")
        return english_section  # Fallback to English

def create_enhanced_transcript(original_file, english_file, output_file):
    """Process line by line in small batches"""
    
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Read files
    with open(original_file, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    with open(english_file, 'r', encoding='utf-8') as f:
        english_lines = f.readlines()
    
    # Open output file for writing
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Enhanced Transcript with Arabic Quotations\n\n")
        
        # Process in batches of 15 lines
        batch_size = 15
        total_batches = (len(english_lines) + batch_size - 1) // batch_size
        
        for i in range(0, len(english_lines), batch_size):
            batch_num = i // batch_size + 1
            print(f"  Processing batch {batch_num}/{total_batches}...")
            
            # Get batch
            orig_batch = ''.join(original_lines[i:i+batch_size])
            eng_batch = ''.join(english_lines[i:i+batch_size])
            
            # Process
            result = process_small_section(client, orig_batch, eng_batch, batch_num)
            
            # Write immediately
            out.write(result)
            out.write("\n\n")
    
    print(f"✓ Saved: {output_file}")

def create_article_section(client, original_text, english_text, section_name):
    """Create one section of the article"""
    
    prompt = f"""Create a well-formatted article section from this lecture content.

SECTION: {section_name}

ORIGINAL:
{original_text}

ENGLISH:
{english_text}

Requirements:
1. Add appropriate headings and subheadings
2. Improve flow and readability
3. Include ALL Arabic quotations, verses, and prayers
4. Do NOT summarize - preserve all content
5. Output in Markdown format

Output the formatted section:"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={
                'temperature': 0.4,
                'max_output_tokens': 3000,
                'response_modalities': ['TEXT']
            }
        )
        return response.text
    except Exception as e:
        print(f"    Error in {section_name}: {e}")
        return f"\n\n## {section_name}\n\n{english_text}\n\n"

def create_structured_article(original_file, english_file, output_file, base_name):
    """Create article by processing logical sections"""
    
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Read files
    with open(original_file, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    with open(english_file, 'r', encoding='utf-8') as f:
        english_text = f.read()
    
    # Split into logical sections (based on line count)
    orig_lines = original_text.split('\n')
    eng_lines = english_text.split('\n')
    
    sections = [
        ("Opening and Introduction", 0, 25),
        ("Spiritual Orphans and Scholars", 25, 50),
        ("The Meaning of Intizar", 50, 75),
        ("Occultation as Trial", 75, 100),
        ("Qualities of Ahl-e-Siqa", 100, 125),
        ("Representatives of Imam", 125, 150),
        ("Du'a Nudba and Conclusion", 150, 175),
        ("Q&A Session", 175, None)  # Rest of content
    ]
    
    with open(output_file, 'w', encoding='utf-8') as out:
        # Header
        out.write(f"# Lecture on Imam-e-Zaman: {base_name}\n\n")
        out.write("## Table of Contents\n\n")
        for section_name, _, _ in sections:
            anchor = section_name.lower().replace(' ', '-').replace(':', '')
            out.write(f"- [{section_name}](#{anchor})\n")
        out.write("\n---\n\n")
        
        # Process each section
        for section_name, start, end in sections:
            print(f"  Creating section: {section_name}...")
            
            orig_section = '\n'.join(orig_lines[start:end])
            eng_section = '\n'.join(eng_lines[start:end])
            
            result = create_article_section(client, orig_section, eng_section, section_name)
            out.write(result)
            out.write("\n\n")
        
        # Key takeaways
        out.write("## Key Takeaways\n\n")
        out.write("1. The concept of spiritual orphanhood and its severity\n")
        out.write("2. The role of scholars in guiding believers\n")
        out.write("3. The true meaning of intizar as active striving\n")
        out.write("4. The era of occultation as a time of trial\n")
        out.write("5. Qualities of reliable believers (Ahl-e-Siqa)\n")
        out.write("6. Our responsibility as representatives of Imam\n")
        out.write("7. The importance of intense piety and sincerity\n")
        out.write("8. Daily renewal of allegiance through Du'a\n")
        out.write("9. Quality over quantity in serving the Imam\n")
        out.write("10. The generosity of Imam-e-Zaman\n\n")
        
        # References
        out.write("## References\n\n")
        out.write("- Bihar al-Anwar\n")
        out.write("- Al-Kafi\n")
        out.write("- Ghaibat-e-Numaniya\n")
        out.write("- Nahjul Balagha\n")
        out.write("- Wasa'il al-Shia\n")
    
    print(f"✓ Saved: {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python streaming_enhance.py <original_file> <english_file>")
        sys.exit(1)
    
    original_file = sys.argv[1]
    english_file = sys.argv[2]
    
    if not os.path.exists(original_file) or not os.path.exists(english_file):
        print("Error: Input files not found")
        sys.exit(1)
    
    # Get paths
    base_name = Path(original_file).stem.replace('.transcription', '')
    output_dir = Path(original_file).parent
    
    print(f"\n{'='*60}")
    print(f"Processing: {base_name}")
    print(f"{'='*60}\n")
    
    # Create enhanced transcript
    print("Creating enhanced transcript...")
    enhanced_path = output_dir / f"{base_name}.enhanced.md"
    create_enhanced_transcript(original_file, english_file, enhanced_path)
    
    # Create article
    print("\nCreating structured article...")
    article_path = output_dir / f"{base_name}.article.md"
    create_structured_article(original_file, english_file, article_path, base_name)
    
    print(f"\n{'='*60}")
    print("✓ COMPLETE!")
    print(f"{'='*60}\n")
    print("Generated:")
    print(f"  1. {enhanced_path}")
    print(f"  2. {article_path}")

if __name__ == '__main__':
    main()
