#!/usr/bin/env python3
"""
Extract text from page 1 of a K-1 PDF
Created: 10/01/25 8:58PM
Purpose: Dual-verification approach - combine visual layout understanding with precise text extraction
         to prevent hallucinations in data entry
"""

import sys
import PyPDF2

def extract_page1_text(pdf_path):
    """Extract text from page 1 of PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Get only page 1 (index 0)
            page = pdf_reader.pages[0]
            text = page.extract_text()

            return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_k1_page1.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    text = extract_page1_text(pdf_path)
    print(text)
