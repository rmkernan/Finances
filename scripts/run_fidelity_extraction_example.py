#!/usr/bin/env python3
"""
Fidelity PDF Extraction Usage Example

Created: 2025-09-26 4:54PM - Purpose: Demonstrate usage of the Fidelity PDF text extractor

This script shows how to use the extract_fidelity_pdf_text.py script programmatically.
"""

import os
import sys
from extract_fidelity_pdf_text import FidelityPDFExtractor

def main():
    """Example usage of the Fidelity PDF extractor"""

    # Example paths - adjust as needed
    pdf_path = '/Users/richkernan/Projects/Finances/documents/3processed/Fid_Stmnt_2025-08_KernBrok+KernCMA.pdf'
    output_dir = '/Users/richkernan/Projects/Finances/documents/4extractions/'

    # Verify paths exist
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1

    if not os.path.exists(output_dir):
        print(f"Error: Output directory not found: {output_dir}")
        return 1

    print("="*60)
    print("FIDELITY PDF EXTRACTION EXAMPLE")
    print("="*60)
    print(f"Input PDF: {pdf_path}")
    print(f"Output Directory: {output_dir}")
    print()

    # Create extractor instance
    extractor = FidelityPDFExtractor(pdf_path, output_dir)

    # Process the PDF
    results = extractor.process_pdf()

    # Save results
    json_output = extractor.save_results("json")
    text_output = extractor.save_results("text")

    # Display summary
    summary = results.get("extraction_summary", {})
    print("EXTRACTION RESULTS:")
    print("-" * 30)
    print(f"Status: {summary.get('extraction_status', 'unknown')}")
    print(f"Pages processed: {summary.get('total_pages', 'unknown')}")
    print(f"Tables found: {summary.get('total_tables', 'unknown')}")
    print(f"Table types: {summary.get('tables_by_type', {})}")
    print(f"Accounts detected: {len(summary.get('accounts_detected', []))}")
    print(f"Securities found: {summary.get('securities_count', 'unknown')}")
    print()
    print("OUTPUT FILES:")
    print(f"- JSON: {json_output}")
    print(f"- Text: {text_output}")

    # Show sample of extracted data
    tables = results.get("tables_found", [])
    if tables:
        print(f"\nSAMPLE TABLE DATA (first table):")
        print("-" * 30)
        first_table = tables[0]
        print(f"Type: {first_table['table_type']}")
        print(f"Page: {first_table['page_number']}")
        print(f"Rows: {first_table['rows']}, Columns: {first_table['columns']}")
        print("First few rows:")
        for i, row in enumerate(first_table['data'][:3]):
            print(f"  Row {i}: {row}")

    return 0

if __name__ == "__main__":
    sys.exit(main())