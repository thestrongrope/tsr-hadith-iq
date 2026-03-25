#!/usr/bin/env python3
"""
Enhanced transcript processor with granular chunking to avoid output truncation.
Processes lecture in multiple small sections and assembles complete documents.
"""

import os
import sys
import google.genai as genai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not set")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def read_file(filepath):
    """Read file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def split_into_chunks(text, num_chunks=8):
    """Split text into equal chunks with overlap for context"""
    lines = text.split('\n')
    chunk_size = len(lines) // num_chunks
    overlap = 5  # 5 lines overlap for context
    
    chunks = []
    for i in range(num_chunks):
        start = max(0, i * chunk_size - overlap)
        end = min(len(lines), (i + 1) * chunk_size + overlap)
        
        # Last chunk gets everything remaining
        if i == num_chunks - 1:
            end = len(lines)
        
        chunk_text = '\n'.join(lines[start:end])
        chunks.append({
            'number': i + 1,
            'text': chunk_text,
            'line_start': start,
            'line_end': end
        })
    
    return chunks

def process_enhanced_chunk(original_chunk, english_chunk, chunk_num, total_chunks):
    """Process a single chunk for enhanced transcript"""
    
    system_prompt = """You are processing ONE SECTION of a long lecture transcript.

CRITICAL INSTRUCTIONS:
1. This is section {chunk_num} of {total_chunks} - process ONLY this section
2. Output EVERY LINE from the English text
3. When you see quotations, verses, or Arabic phrases, INSERT the original Arabic
4. Do NOT summarize or skip any content
5. Do NOT add conclusions or "to be continued" - just process the text
6. Preserve all formatting, timestamps, and structure
7. Output the COMPLETE processed section

Your task: Merge the English section with Arabic quotations from the original.""".format(
        chunk_num=chunk_num, 
        total_chunks=total_chunks
    )
    
    user_prompt = f"""ORIGINAL TRANSCRIPT SECTION (Contains Arabic/Urdu):
{original_chunk}

ENGLISH TRANSLATION SECTION:
{english_chunk}

Process this section by:
1. Taking each line from the English section
2. Where Arabic verses/quotations appear, insert them from the original
3. Output EVERY line - do not skip or summarize
4. Just process this section and output it completely

Output the complete processed section now:"""

    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=user_prompt,
        config={
            'system_instruction': system_prompt,
            'temperature': 0.3,
            'max_output_tokens': 8192,  # Maximum allowed
            'response_modalities': ['TEXT']
        }
    )
    
    return response.text

def process_article_chunk(original_chunk, english_chunk, chunk_num, total_chunks):
    """Process a single chunk for structured article"""
    
    system_prompt = """You are processing ONE SECTION of a long lecture for an article.

CRITICAL INSTRUCTIONS:
1. This is section {chunk_num} of {total_chunks} - process ONLY this section
2. Create proper headings/subheadings for this section's topics
3. Rewrite content for better flow while preserving ALL information
4. Include ALL Quranic verses, hadiths, and Arabic quotations
5. Do NOT summarize - expand and improve the writing
6. Do NOT add "to be continued" or section markers
7. Just output the formatted content for this section

Output style: Professional article with proper Markdown formatting.""".format(
        chunk_num=chunk_num,
        total_chunks=total_chunks
    )
    
    user_prompt = f"""ORIGINAL SECTION (Arabic/Urdu):
{original_chunk}

ENGLISH SECTION:
{english_chunk}

Transform this section into well-structured article content:
1. Add appropriate headings/subheadings
2. Improve flow and readability
3. Preserve ALL content - do not remove anything
4. Include ALL quotations with Arabic text
5. Output the complete formatted section

Output the formatted section now:"""

    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=user_prompt,
        config={
            'system_instruction': system_prompt,
            'temperature': 0.4,
            'max_output_tokens': 8192,
            'response_modalities': ['TEXT']
        }
    )
    
    return response.text

def create_enhanced_transcript(original_text, english_text, output_path):
    """Create complete enhanced transcript by processing in chunks"""
    
    print("Creating enhanced transcript in chunks...")
    
    # Split into chunks
    original_chunks = split_into_chunks(original_text, num_chunks=8)
    english_chunks = split_into_chunks(english_text, num_chunks=8)
    
    processed_sections = []
    
    for i, (orig_chunk, eng_chunk) in enumerate(zip(original_chunks, english_chunks)):
        chunk_num = i + 1
        print(f"  Processing chunk {chunk_num}/8...")
        
        try:
            result = process_enhanced_chunk(
                orig_chunk['text'],
                eng_chunk['text'],
                chunk_num,
                8
            )
            processed_sections.append(result)
        except Exception as e:
            print(f"    Error on chunk {chunk_num}: {e}")
            print(f"    Using English text as fallback")
            processed_sections.append(eng_chunk['text'])
    
    # Combine all sections
    complete_transcript = '\n\n'.join(processed_sections)
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(complete_transcript)
    
    print(f"✓ Saved: {output_path}")

def create_structured_article(original_text, english_text, output_path, base_filename):
    """Create complete structured article by processing in chunks"""
    
    print("Creating structured article in chunks...")
    
    # Split into chunks
    original_chunks = split_into_chunks(original_text, num_chunks=8)
    english_chunks = split_into_chunks(english_text, num_chunks=8)
    
    # Create header/TOC section first
    print("  Creating header and TOC...")
    
    header_prompt = f"""Create the HEADER AND TABLE OF CONTENTS ONLY for this lecture article.

Based on this lecture content, create:
1. Title
2. Brief introduction (2-3 sentences)
3. Detailed Table of Contents with main sections and subsections

The lecture covers: Imam-e-Zaman, spiritual orphans, intizar, occultation as trial, qualities of Ahl-e-Siqa, Du'a Nudba, and Q&A.

Output ONLY the header and TOC in proper Markdown format. Do not include any body content."""

    header_response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=header_prompt,
        config={
            'temperature': 0.4,
            'max_output_tokens': 2048,
            'response_modalities': ['TEXT']
        }
    )
    
    article_parts = [header_response.text]
    
    # Process each content chunk
    for i, (orig_chunk, eng_chunk) in enumerate(zip(original_chunks, english_chunks)):
        chunk_num = i + 1
        print(f"  Processing chunk {chunk_num}/8...")
        
        try:
            result = process_article_chunk(
                orig_chunk['text'],
                eng_chunk['text'],
                chunk_num,
                8
            )
            article_parts.append(result)
        except Exception as e:
            print(f"    Error on chunk {chunk_num}: {e}")
            # Add basic formatted version as fallback
            article_parts.append(f"\n\n{eng_chunk['text']}\n\n")
    
    # Add key takeaways and references at the end
    print("  Creating conclusion sections...")
    
    conclusion_prompt = f"""Based on this lecture, create:

1. ## Key Takeaways (12-15 concise points)
2. ## References (list the Islamic sources mentioned)

Be comprehensive but concise. Output in proper Markdown format."""

    conclusion_response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=conclusion_prompt + f"\n\nLecture summary: {english_chunks[0]['text'][:2000]}",
        config={
            'temperature': 0.4,
            'max_output_tokens': 2048,
            'response_modalities': ['TEXT']
        }
    )
    
    article_parts.append(conclusion_response.text)
    
    # Combine all parts
    complete_article = '\n\n'.join(article_parts)
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(complete_article)
    
    print(f"✓ Saved: {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python chunked_enhance.py <original_file> <english_file>")
        sys.exit(1)
    
    original_file = sys.argv[1]
    english_file = sys.argv[2]
    
    # Validate files
    if not os.path.exists(original_file) or not os.path.exists(english_file):
        print("Error: Input files not found")
        sys.exit(1)
    
    print("Reading files...")
    original_text = read_file(original_file)
    english_text = read_file(english_file)
    
    # Get base filename
    base_name = Path(original_file).stem.replace('.transcription', '')
    output_dir = Path(original_file).parent
    
    print(f"\n{'='*60}")
    print(f"Processing: {base_name}")
    print(f"{'='*60}\n")
    
    # Create enhanced transcript
    enhanced_path = output_dir / f"{base_name}.enhanced.md"
    create_enhanced_transcript(original_text, english_text, enhanced_path)
    
    # Create structured article
    article_path = output_dir / f"{base_name}.article.md"
    create_structured_article(original_text, english_text, article_path, base_name)
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETE!")
    print(f"{'='*60}\n")
    print("Generated:")
    print(f"  1. {enhanced_path}")
    print(f"  2. {article_path}")
    print("\nConvert:")
    print(f"  pandoc '{enhanced_path}' -o output.pdf")
    print(f"  pandoc '{article_path}' -o output.pdf")

if __name__ == '__main__':
    main()
