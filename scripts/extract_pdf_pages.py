#!/usr/bin/env python3
"""
Created: 09/22/25 6:26PM
Updated: 09/22/25 6:43PM - Added text-only extraction for token efficiency
Purpose: Extract specific pages from a PDF file to reduce token usage when reading PDFs

Extract specific pages from a PDF file as text or full PDF.
Usage:
  python extract_pdf_pages.py input.pdf output.pdf start_page [end_page]           # Extract full PDF pages
  python extract_pdf_pages.py input.pdf output.txt start_page [end_page] --text   # Extract text only
"""

import sys
import PyPDF2
from pathlib import Path

def extract_text_only(input_pdf_path, output_text_path, start_page, end_page=None):
    """
    Extract text from specific pages of a PDF file for token-efficient reading.

    Args:
        input_pdf_path: Path to input PDF
        output_text_path: Path to output text file
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed), if None uses start_page
    """
    if end_page is None:
        end_page = start_page

    # Convert to 0-indexed
    start_idx = start_page - 1
    end_idx = end_page - 1

    try:
        with open(input_pdf_path, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)

            # Validate page numbers
            total_pages = len(reader.pages)
            if start_idx < 0 or end_idx >= total_pages:
                print(f"Error: Page numbers out of range. PDF has {total_pages} pages.")
                return False

            # Extract text from pages
            extracted_text = ""
            for page_idx in range(start_idx, end_idx + 1):
                page_text = reader.pages[page_idx].extract_text()
                extracted_text += f"=== PAGE {page_idx + 1} ===\n{page_text}\n\n"

            # Write text output
            with open(output_text_path, 'w', encoding='utf-8') as output_file:
                output_file.write(extracted_text)

            pages_extracted = end_idx - start_idx + 1
            char_count = len(extracted_text)
            print(f"Successfully extracted text from {pages_extracted} page(s) to {output_text_path}")
            print(f"Total characters: {char_count}")
            return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def extract_pages(input_pdf_path, output_pdf_path, start_page, end_page=None):
    """
    Extract specific pages from a PDF file.

    Args:
        input_pdf_path: Path to input PDF
        output_pdf_path: Path to output PDF
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed), if None uses start_page
    """
    if end_page is None:
        end_page = start_page

    # Convert to 0-indexed
    start_idx = start_page - 1
    end_idx = end_page - 1

    try:
        with open(input_pdf_path, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()

            # Validate page numbers
            total_pages = len(reader.pages)
            if start_idx < 0 or end_idx >= total_pages:
                print(f"Error: Page numbers out of range. PDF has {total_pages} pages.")
                return False

            # Extract pages
            for page_idx in range(start_idx, end_idx + 1):
                writer.add_page(reader.pages[page_idx])

            # Write output
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)

            pages_extracted = end_idx - start_idx + 1
            print(f"Successfully extracted {pages_extracted} page(s) to {output_pdf_path}")
            return True

    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python extract_pdf_pages.py input.pdf output.pdf start_page [end_page]           # Extract full PDF pages")
        print("  python extract_pdf_pages.py input.pdf output.txt start_page [end_page] --text   # Extract text only")
        print("Examples:")
        print("  python extract_pdf_pages.py statement.pdf first_page.pdf 1")
        print("  python extract_pdf_pages.py statement.pdf first_two.pdf 1 2")
        print("  python extract_pdf_pages.py statement.pdf first_two.txt 1 2 --text")
        sys.exit(1)

    # Check for --text flag
    text_only = '--text' in sys.argv
    if text_only:
        sys.argv.remove('--text')  # Remove flag to simplify parsing

    input_pdf = sys.argv[1]
    output_file = sys.argv[2]
    start_page = int(sys.argv[3])
    end_page = int(sys.argv[4]) if len(sys.argv) > 4 else None

    # Validate input file exists
    if not Path(input_pdf).exists():
        print(f"Error: Input file {input_pdf} does not exist")
        sys.exit(1)

    # Choose extraction method based on flag
    if text_only:
        success = extract_text_only(input_pdf, output_file, start_page, end_page)
    else:
        success = extract_pages(input_pdf, output_file, start_page, end_page)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()