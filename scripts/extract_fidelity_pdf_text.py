#!/usr/bin/env python3
"""
Fidelity Statement PDF Text Extractor using PDF Plumber

Created: 2025-09-26 4:54PM - Purpose: Extract structured text from Fidelity PDF statements
Author: Claude Code Assistant
Version: 1.0

This script uses PDF Plumber to extract structured text from Fidelity financial statements,
preserving table structure critical for financial data processing.

Requirements:
- pdfplumber
- json
- logging
- datetime

Usage:
    python3 extract_fidelity_pdf_text.py [pdf_path] [output_path]
"""

import pdfplumber
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/claude/fidelity_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FidelityPDFExtractor:
    """Extract structured text from Fidelity PDF statements"""

    def __init__(self, pdf_path: str, output_dir: str):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.extraction_timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M")
        self.extracted_data = {
            "extraction_metadata": {
                "source_pdf": pdf_path,
                "extraction_timestamp": self.extraction_timestamp,
                "extractor_version": "pdfplumber_1.0",
                "extraction_method": "structured_text_tables"
            },
            "document_info": {},
            "pages_processed": [],
            "tables_found": [],
            "text_sections": {},
            "extraction_summary": {}
        }

    def detect_table_structure(self, page) -> List[Dict]:
        """Detect and extract table structures from a page"""
        tables = []

        # Try to extract tables using PDF Plumber's table detection
        page_tables = page.extract_tables()

        for i, table in enumerate(page_tables):
            if table and len(table) > 0:
                # Clean and structure the table data
                cleaned_table = self.clean_table_data(table)

                table_info = {
                    "table_index": i,
                    "page_number": page.page_number,
                    "rows": len(cleaned_table),
                    "columns": len(cleaned_table[0]) if cleaned_table else 0,
                    "data": cleaned_table,
                    "table_type": self.identify_table_type(cleaned_table)
                }
                tables.append(table_info)

        # If no tables found with automatic detection, try text-based parsing
        if not tables:
            text_tables = self.extract_text_based_tables(page)
            tables.extend(text_tables)

        return tables

    def extract_text_based_tables(self, page) -> List[Dict]:
        """Extract table-like structures from text when automatic detection fails"""
        tables = []
        full_text = page.extract_text() or ""

        # Split text into lines
        lines = full_text.split('\n')

        # Look for holdings tables (Description, Quantity, Price, Market Value patterns)
        holdings_table = self.extract_holdings_table(lines, page.page_number)
        if holdings_table:
            tables.append(holdings_table)

        # Look for activity/transaction tables
        activity_table = self.extract_activity_table(lines, page.page_number)
        if activity_table:
            tables.append(activity_table)

        # Look for account summary tables
        summary_table = self.extract_summary_table(lines, page.page_number)
        if summary_table:
            tables.append(summary_table)

        return tables

    def extract_holdings_table(self, lines: List[str], page_num: int) -> Optional[Dict]:
        """Extract holdings table from text lines"""
        table_data = []
        in_holdings = False

        # Look for holdings section indicators
        holdings_indicators = [
            "description", "quantity", "price", "market value", "cost basis",
            "symbol", "shares", "current price", "total value"
        ]

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if this line contains holdings header indicators
            if any(indicator in line_lower for indicator in holdings_indicators):
                if len([ind for ind in holdings_indicators if ind in line_lower]) >= 2:
                    in_holdings = True
                    # This is likely a header row
                    headers = self.parse_line_into_columns(line)
                    if headers:
                        table_data.append(headers)
                    continue

            if in_holdings:
                # Look for data rows (containing financial amounts or quantities)
                if re.search(r'\$[\d,]+\.?\d*|\d+\.\d+|\d{1,3}(?:,\d{3})*', line):
                    cols = self.parse_line_into_columns(line)
                    if cols and len(cols) >= 3:  # At least 3 columns for a meaningful row
                        table_data.append(cols)
                elif line.strip() == "" or re.match(r'^[A-Z\s]+$', line.strip()):
                    # Empty line or header-like line might end the table
                    if len(table_data) > 2:  # If we have header + data
                        break

        if len(table_data) >= 2:  # At least header + one data row
            return {
                "table_index": 0,
                "page_number": page_num,
                "rows": len(table_data),
                "columns": len(table_data[0]) if table_data else 0,
                "data": table_data,
                "table_type": "holdings_table"
            }

        return None

    def extract_activity_table(self, lines: List[str], page_num: int) -> Optional[Dict]:
        """Extract activity/transaction table from text lines"""
        table_data = []
        in_activity = False

        activity_indicators = [
            "date", "transaction", "amount", "activity", "description",
            "buy", "sell", "dividend", "interest", "deposit", "withdrawal"
        ]

        for line in lines:
            line_lower = line.lower().strip()

            # Check for activity section
            if any(indicator in line_lower for indicator in activity_indicators):
                if len([ind for ind in activity_indicators if ind in line_lower]) >= 2:
                    in_activity = True
                    headers = self.parse_line_into_columns(line)
                    if headers:
                        table_data.append(headers)
                    continue

            if in_activity:
                # Look for date patterns and amounts
                if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}', line):
                    cols = self.parse_line_into_columns(line)
                    if cols and len(cols) >= 3:
                        table_data.append(cols)
                elif line.strip() == "":
                    if len(table_data) > 2:
                        break

        if len(table_data) >= 2:
            return {
                "table_index": 1,
                "page_number": page_num,
                "rows": len(table_data),
                "columns": len(table_data[0]) if table_data else 0,
                "data": table_data,
                "table_type": "activity_table"
            }

        return None

    def extract_summary_table(self, lines: List[str], page_num: int) -> Optional[Dict]:
        """Extract account summary table from text lines"""
        table_data = []

        # Look for summary patterns
        for line in lines:
            if re.search(r'(beginning|ending|net)\s+(value|balance)', line, re.IGNORECASE):
                cols = self.parse_line_into_columns(line)
                if cols:
                    table_data.append(cols)
            elif re.search(r'(income|gains|losses)\s+summary', line, re.IGNORECASE):
                cols = self.parse_line_into_columns(line)
                if cols:
                    table_data.append(cols)

        if len(table_data) >= 1:
            return {
                "table_index": 2,
                "page_number": page_num,
                "rows": len(table_data),
                "columns": len(table_data[0]) if table_data else 0,
                "data": table_data,
                "table_type": "account_summary"
            }

        return None

    def parse_line_into_columns(self, line: str) -> List[str]:
        """Parse a line into columns based on spacing and content patterns"""
        # Clean the line
        line = line.strip()
        if not line:
            return []

        # Method 1: Split by multiple spaces (common in financial statements)
        cols = re.split(r'\s{2,}', line)

        # Method 2: If that doesn't work well, try to identify dollar amounts and split around them
        if len(cols) <= 2:
            # Look for patterns like amounts, dates, percentages
            money_pattern = r'\$?[\d,]+\.?\d*'
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            percent_pattern = r'\d+\.?\d*%'

            # Split more aggressively around these patterns
            parts = re.split(f'({money_pattern}|{date_pattern}|{percent_pattern})', line)
            cols = [part.strip() for part in parts if part.strip()]

        # Clean up each column
        cleaned_cols = []
        for col in cols:
            cleaned = col.strip()
            if cleaned:
                cleaned_cols.append(cleaned)

        return cleaned_cols

    def clean_table_data(self, raw_table: List[List]) -> List[List]:
        """Clean and normalize table data"""
        cleaned = []

        for row in raw_table:
            if row:  # Skip empty rows
                cleaned_row = []
                for cell in row:
                    # Clean cell content
                    if cell is None:
                        cleaned_row.append("")
                    else:
                        # Remove excessive whitespace and normalize
                        cleaned_cell = re.sub(r'\s+', ' ', str(cell).strip())
                        cleaned_row.append(cleaned_cell)
                cleaned.append(cleaned_row)

        return cleaned

    def identify_table_type(self, table_data: List[List]) -> str:
        """Identify the type of financial table based on headers"""
        if not table_data or len(table_data) < 2:
            return "unknown"

        # Check first few rows for headers
        header_text = " ".join([" ".join(row) for row in table_data[:3]]).lower()

        if any(keyword in header_text for keyword in ["description", "quantity", "price", "market value", "cost basis"]):
            return "holdings_table"
        elif any(keyword in header_text for keyword in ["date", "transaction", "amount", "activity"]):
            return "activity_table"
        elif any(keyword in header_text for keyword in ["account", "summary", "net value"]):
            return "account_summary"
        elif any(keyword in header_text for keyword in ["income", "dividend", "interest"]):
            return "income_summary"
        else:
            return "other_table"

    def extract_text_sections(self, page) -> Dict[str, str]:
        """Extract text sections that aren't in tables"""
        full_text = page.extract_text()

        # Split text into logical sections
        sections = {}

        # Look for common Fidelity statement sections
        section_patterns = {
            "account_info": r"Account\s+Number:.*?(?=\n\n|\n[A-Z]|\Z)",
            "period_info": r"Statement\s+Period:.*?(?=\n\n|\n[A-Z]|\Z)",
            "portfolio_summary": r"Portfolio\s+Summary.*?(?=\n\n[A-Z]|\Z)",
            "footnotes": r"Footnotes?:.*?(?=\Z)",
            "disclosures": r"Important\s+Information.*?(?=\Z)"
        }

        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group().strip()

        # Also capture any remaining unclassified text
        sections["full_page_text"] = full_text

        return sections

    def extract_account_information(self, text: str) -> Dict[str, Any]:
        """Extract account-specific information from text"""
        account_info = {}

        # Extract account numbers
        account_pattern = r"(?:Account\s+Number:?\s*)?([A-Z]?\d{2,3}[-\s]?\d{6,8})"
        accounts = re.findall(account_pattern, text, re.IGNORECASE)
        if accounts:
            account_info["account_numbers"] = list(set(accounts))

        # Extract statement period
        period_pattern = r"Statement\s+Period:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})\s*(?:[-–]\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4}))"
        period_match = re.search(period_pattern, text, re.IGNORECASE)
        if period_match:
            account_info["period_start"] = period_match.group(1)
            account_info["period_end"] = period_match.group(2)

        # Extract account values
        value_patterns = {
            "net_account_value": r"Net\s+Account\s+Value:?\s*\$?([\d,]+\.?\d*)",
            "beginning_value": r"Beginning\s+(?:Account\s+)?Value:?\s*\$?([\d,]+\.?\d*)",
            "ending_value": r"Ending\s+(?:Account\s+)?Value:?\s*\$?([\d,]+\.?\d*)"
        }

        for key, pattern in value_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                account_info[key] = matches

        return account_info

    def extract_security_descriptions(self, text: str) -> List[Dict[str, str]]:
        """Extract multi-line security descriptions that might span table rows"""
        securities = []

        # Look for patterns that indicate security descriptions
        # Bonds often have complex multi-line descriptions
        bond_pattern = r"([A-Z\s&]+(?:BOND|BD|MUNICIPAL|CORP|GOVT).*?)(?=\n\s*\d+\.?\d*\s|\n[A-Z]|\Z)"
        bond_matches = re.findall(bond_pattern, text, re.IGNORECASE | re.DOTALL)

        for match in bond_matches:
            clean_desc = re.sub(r'\s+', ' ', match.strip())
            securities.append({
                "type": "bond",
                "description": clean_desc
            })

        # Stock descriptions
        stock_pattern = r"([A-Z\s&]+(?:INC|CORP|CO|LLC|LTD).*?)(?=\n\s*\d+\.?\d*\s|\n[A-Z]|\Z)"
        stock_matches = re.findall(stock_pattern, text, re.IGNORECASE | re.DOTALL)

        for match in stock_matches:
            clean_desc = re.sub(r'\s+', ' ', match.strip())
            securities.append({
                "type": "stock",
                "description": clean_desc
            })

        return securities

    def process_pdf(self) -> Dict[str, Any]:
        """Main processing function"""
        logger.info(f"Starting extraction of {self.pdf_path}")

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                logger.info(f"PDF opened successfully. Pages: {len(pdf.pages)}")

                self.extracted_data["document_info"] = {
                    "total_pages": len(pdf.pages),
                    "pdf_metadata": pdf.metadata if hasattr(pdf, 'metadata') else {}
                }

                all_tables = []
                all_text_sections = {}
                all_account_info = {}
                all_securities = []

                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}")

                    # Extract tables from this page
                    page_tables = self.detect_table_structure(page)
                    all_tables.extend(page_tables)

                    # Extract text sections
                    text_sections = self.extract_text_sections(page)
                    all_text_sections[f"page_{page_num}"] = text_sections

                    # Extract account information
                    page_text = page.extract_text() or ""
                    account_info = self.extract_account_information(page_text)
                    if account_info:
                        all_account_info[f"page_{page_num}"] = account_info

                    # Extract security descriptions
                    securities = self.extract_security_descriptions(page_text)
                    all_securities.extend(securities)

                    # Record page processing
                    self.extracted_data["pages_processed"].append({
                        "page_number": page_num,
                        "tables_found": len(page_tables),
                        "text_length": len(page_text),
                        "has_account_info": bool(account_info)
                    })

                # Compile results
                self.extracted_data["tables_found"] = all_tables
                self.extracted_data["text_sections"] = all_text_sections
                self.extracted_data["account_information"] = all_account_info
                self.extracted_data["securities_found"] = all_securities

                # Generate extraction summary
                self.extracted_data["extraction_summary"] = {
                    "total_pages": len(pdf.pages),
                    "total_tables": len(all_tables),
                    "tables_by_type": self._summarize_table_types(all_tables),
                    "accounts_detected": self._extract_unique_accounts(all_account_info),
                    "securities_count": len(all_securities),
                    "extraction_status": "success"
                }

                logger.info("PDF extraction completed successfully")
                return self.extracted_data

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            self.extracted_data["extraction_summary"] = {
                "extraction_status": "failed",
                "error_message": str(e)
            }
            return self.extracted_data

    def _summarize_table_types(self, tables: List[Dict]) -> Dict[str, int]:
        """Summarize table types found"""
        type_counts = {}
        for table in tables:
            table_type = table.get("table_type", "unknown")
            type_counts[table_type] = type_counts.get(table_type, 0) + 1
        return type_counts

    def _extract_unique_accounts(self, account_info: Dict) -> List[str]:
        """Extract unique account numbers found"""
        unique_accounts = set()
        for page_info in account_info.values():
            if "account_numbers" in page_info:
                unique_accounts.update(page_info["account_numbers"])
        return list(unique_accounts)

    def save_results(self, output_format: str = "json") -> str:
        """Save extraction results to file"""
        # Generate output filename
        pdf_basename = os.path.splitext(os.path.basename(self.pdf_path))[0]

        if output_format == "json":
            output_filename = f"{pdf_basename}_extracted_text_{self.extraction_timestamp}.json"
            output_path = os.path.join(self.output_dir, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)

        else:  # text format
            output_filename = f"{pdf_basename}_extracted_text_{self.extraction_timestamp}.txt"
            output_path = os.path.join(self.output_dir, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("FIDELITY PDF TEXT EXTRACTION REPORT\n")
                f.write("="*50 + "\n\n")

                # Write summary
                summary = self.extracted_data.get("extraction_summary", {})
                f.write(f"SOURCE PDF: {self.pdf_path}\n")
                f.write(f"EXTRACTION TIME: {self.extraction_timestamp}\n")
                f.write(f"TOTAL PAGES: {summary.get('total_pages', 'unknown')}\n")
                f.write(f"TOTAL TABLES: {summary.get('total_tables', 'unknown')}\n")
                f.write(f"EXTRACTION STATUS: {summary.get('extraction_status', 'unknown')}\n\n")

                # Write table summary
                f.write("TABLES BY TYPE:\n")
                tables_by_type = summary.get('tables_by_type', {})
                for table_type, count in tables_by_type.items():
                    f.write(f"- {table_type}: {count}\n")
                f.write("\n")

                # Write accounts detected
                accounts = summary.get('accounts_detected', [])
                f.write(f"ACCOUNTS DETECTED: {len(accounts)}\n")
                for account in accounts:
                    f.write(f"- {account}\n")
                f.write("\n")

                # Write detailed table data
                f.write("DETAILED TABLE DATA:\n")
                f.write("="*30 + "\n")
                for table in self.extracted_data.get("tables_found", []):
                    f.write(f"\nTable {table['table_index']} (Page {table['page_number']}) - {table['table_type']}\n")
                    f.write(f"Rows: {table['rows']}, Columns: {table['columns']}\n")
                    f.write("-" * 20 + "\n")

                    for row in table['data'][:10]:  # Show first 10 rows
                        f.write(" | ".join(str(cell)[:50] for cell in row) + "\n")

                    if table['rows'] > 10:
                        f.write(f"... ({table['rows'] - 10} more rows)\n")
                    f.write("\n")

        logger.info(f"Results saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    # Set default paths
    default_pdf_path = '/Users/richkernan/Projects/Finances/documents/3processed/Fid_Stmnt_2025-08_KernBrok+KernCMA.pdf'
    default_output_dir = '/Users/richkernan/Projects/Finances/documents/4extractions/'

    # Use command line arguments if provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = default_pdf_path

    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = default_output_dir

    # Verify paths exist
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)

    if not os.path.exists(output_dir):
        logger.error(f"Output directory not found: {output_dir}")
        sys.exit(1)

    # Create temp directory for logs
    os.makedirs('/tmp/claude', exist_ok=True)

    # Initialize extractor and process
    extractor = FidelityPDFExtractor(pdf_path, output_dir)

    logger.info("="*60)
    logger.info("FIDELITY PDF TEXT EXTRACTION STARTING")
    logger.info("="*60)

    # Process the PDF
    results = extractor.process_pdf()

    # Save results in both formats
    json_output = extractor.save_results("json")
    text_output = extractor.save_results("text")

    # Print summary
    summary = results.get("extraction_summary", {})
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Status: {summary.get('extraction_status', 'unknown')}")
    print(f"Pages processed: {summary.get('total_pages', 'unknown')}")
    print(f"Tables found: {summary.get('total_tables', 'unknown')}")
    print(f"Accounts detected: {len(summary.get('accounts_detected', []))}")
    print(f"Securities found: {summary.get('securities_count', 'unknown')}")
    print(f"\nOutput files:")
    print(f"- JSON: {json_output}")
    print(f"- Text: {text_output}")

    if summary.get('extraction_status') == 'failed':
        print(f"Error: {summary.get('error_message', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()