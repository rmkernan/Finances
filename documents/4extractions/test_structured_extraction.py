#!/usr/bin/env python3
"""
Test Script: Structured Text to Complete Holdings JSON
Created: 2025-09-26 - Test structured extraction vs direct PDF processing

Purpose: Process structured text extracted from Fidelity PDF to produce complete
holdings JSON according to JSON_Stmnt_Fid_Positions.md specification.

Tests the token efficiency of using structured text extraction as intermediate
format before LLM processing.
"""

import json
import hashlib
import re
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal
import traceback

class StructuredTextProcessor:
    """Process structured text extraction to complete holdings JSON"""

    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.processing_stats = {
            'start_time': datetime.now(),
            'accounts_found': 0,
            'holdings_extracted': 0,
            'field_completeness': {},
            'parsing_issues': [],
            'security_types': {}
        }

    def load_structured_data(self) -> Dict[str, Any]:
        """Load the structured text extraction file"""
        try:
            with open(self.input_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.processing_stats['parsing_issues'].append(f"Failed to load input file: {e}")
            raise

    def extract_document_metadata(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document-level metadata from structured text"""
        extraction_metadata = {
            "json_output_id": "fid_stmnt_2025-08_kernbrok_kerncma_holdings_test",
            "source_pdf_filepath": structured_data.get('extraction_metadata', {}).get('source_pdf', ''),
            "json_output_md5_hash": "",  # Will calculate later
            "doc_md5_hash": "test_extraction_hash",  # Placeholder
            "extraction_type": "holdings",
            "extraction_timestamp": structured_data.get('extraction_metadata', {}).get('extraction_timestamp', ''),
            "extractor_version": "structured_text_test_1.0",
            "pages_processed": structured_data.get('document_info', {}).get('total_pages', 0),
            "extraction_notes": ["Test extraction from structured text format"]
        }

        # Extract document dates - look for statement period info
        document_data = {
            "institution": "Fidelity",
            "statement_date": "2025-08-31",  # Default, should extract from text
            "period_start": "2025-08-01",
            "period_end": "2025-08-31"
        }

        return extraction_metadata, document_data

    def parse_currency_value(self, value_str: str) -> Optional[str]:
        """Parse currency values from text, handling various formats"""
        if not value_str or value_str.lower() in ['unavailable', 'not applicable', '-', '']:
            return None

        # Remove currency symbols, commas, parentheses (for negatives)
        cleaned = re.sub(r'[\$,()]', '', str(value_str))

        # Handle negative values in parentheses
        is_negative = '(' in str(value_str) or cleaned.startswith('-')
        cleaned = cleaned.replace('-', '')

        try:
            value = float(cleaned)
            if is_negative:
                value = -value
            return f"{value:.2f}"
        except ValueError:
            self.processing_stats['parsing_issues'].append(f"Could not parse currency: {value_str}")
            return None

    def parse_quantity(self, qty_str: str) -> Optional[str]:
        """Parse quantity values preserving decimal precision"""
        if not qty_str or qty_str.lower() in ['unavailable', '-', '']:
            return None

        try:
            # Handle negative quantities (short positions)
            is_negative = qty_str.startswith('-')
            cleaned = qty_str.replace('-', '').replace(',', '')
            value = float(cleaned)
            if is_negative:
                value = -value
            return f"{value:.6f}"
        except ValueError:
            self.processing_stats['parsing_issues'].append(f"Could not parse quantity: {qty_str}")
            return None

    def parse_percentage(self, pct_str: str) -> Optional[str]:
        """Parse percentage values as percentage format (not decimal)"""
        if not pct_str or pct_str.lower() in ['unavailable', '-', '']:
            return None

        # Remove % symbol and convert to percentage format
        cleaned = pct_str.replace('%', '').strip()
        try:
            value = float(cleaned)
            return f"{value:.3f}"
        except ValueError:
            self.processing_stats['parsing_issues'].append(f"Could not parse percentage: {pct_str}")
            return None

    def extract_holdings_from_page(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract holdings data from a single page's structured text"""
        holdings = []

        # Look for structured table data in the page
        if 'full_page_text' not in page_data:
            return holdings

        text = page_data['full_page_text']

        # Parse different security types based on headers
        self.extract_mutual_funds(text, holdings)
        self.extract_stocks(text, holdings)
        self.extract_bonds(text, holdings)
        self.extract_etps(text, holdings)

        return holdings

    def extract_mutual_funds(self, text: str, holdings: List[Dict[str, Any]]):
        """Extract mutual fund holdings from page text"""
        # Look for Mutual Funds section
        mf_pattern = r'Mutual Funds.*?(?=(?:Stocks|Exchange Traded|Bonds|Total|\n\n|\Z))'
        mf_match = re.search(mf_pattern, text, re.DOTALL | re.IGNORECASE)

        if not mf_match:
            return

        mf_section = mf_match.group(0)

        # Parse individual fund entries
        # Pattern for fund lines with market values, quantities, prices
        fund_pattern = r'([A-Z][A-Z\s&\-\.]+)\s+\$?([\d,\.]+)\s+([\d,\.]+)\s+\$?([\d,\.]+)\s+\$?([\d,\.]+)'

        for match in re.finditer(fund_pattern, mf_section):
            description = match.group(1).strip()

            # Skip total lines and headers
            if any(skip in description.lower() for skip in ['total', 'beginning', 'ending', 'market value', 'description']):
                continue

            holding = {
                "sec_type": "Mutual Funds",
                "sec_subtype": self.determine_fund_subtype(description),
                "sec_symbol": self.extract_symbol_from_description(description),
                "cusip": None,
                "sec_description": description,
                "beg_market_value": self.parse_currency_value(match.group(2)),
                "quantity": self.parse_quantity(match.group(3)),
                "price_per_unit": self.parse_currency_value(match.group(4)),
                "end_market_value": self.parse_currency_value(match.group(5)),
                "cost_basis": None,  # Would need additional parsing
                "unrealized_gain_loss": None,  # PDF-only field
                "estimated_ann_inc": None,  # PDF-only field
                "est_yield": None  # PDF-only field
            }

            holdings.append(holding)
            self.processing_stats['holdings_extracted'] += 1
            self.processing_stats['security_types']['Mutual Funds'] = \
                self.processing_stats['security_types'].get('Mutual Funds', 0) + 1

    def extract_stocks(self, text: str, holdings: List[Dict[str, Any]]):
        """Extract stock holdings from page text"""
        # Look for Stocks section
        stocks_pattern = r'Stocks.*?(?=(?:Bonds|Exchange Traded|Total|\n\n|\Z))'
        stocks_match = re.search(stocks_pattern, text, re.DOTALL | re.IGNORECASE)

        if not stocks_match:
            return

        stocks_section = stocks_match.group(0)

        # Pattern for stock entries - more complex due to varied formats
        # Look for lines with ticker symbols in parentheses
        stock_pattern = r'([A-Z][^()]+)\s*\(([A-Z]{1,5})\).*?\$?([\d,\.\-]+)'

        for match in re.finditer(stock_pattern, stocks_section):
            description = match.group(1).strip()
            symbol = match.group(2)

            # Skip headers and totals
            if any(skip in description.lower() for skip in ['total', 'beginning', 'common stock', 'preferred stock']):
                continue

            holding = {
                "sec_type": "Stocks",
                "sec_subtype": self.determine_stock_subtype(description),
                "sec_symbol": symbol,
                "cusip": None,
                "sec_description": description,
                "beg_market_value": None,  # Would need more parsing
                "quantity": None,  # Would need more parsing
                "price_per_unit": None,  # Would need more parsing
                "end_market_value": self.parse_currency_value(match.group(3)),
                "cost_basis": None,
                "unrealized_gain_loss": None,  # PDF-only field
                "estimated_ann_inc": None,  # PDF-only field
                "est_yield": None  # PDF-only field
            }

            holdings.append(holding)
            self.processing_stats['holdings_extracted'] += 1
            self.processing_stats['security_types']['Stocks'] = \
                self.processing_stats['security_types'].get('Stocks', 0) + 1

    def extract_bonds(self, text: str, holdings: List[Dict[str, Any]]):
        """Extract bond holdings from page text"""
        bonds_pattern = r'Bonds.*?(?=(?:Stocks|Exchange Traded|Total|\n\n|\Z))'
        bonds_match = re.search(bonds_pattern, text, re.DOTALL | re.IGNORECASE)

        if not bonds_match:
            return

        bonds_section = bonds_match.group(0)

        # Look for bond entries with maturity dates
        bond_pattern = r'([A-Z][^0-9]+)\s+(\d{2}/\d{2}/\d{2,4})'

        for match in re.finditer(bond_pattern, bonds_section):
            description = match.group(1).strip()
            maturity_raw = match.group(2)

            # Convert maturity date to ISO format
            maturity_date = self.parse_bond_maturity(maturity_raw)

            holding = {
                "sec_type": "Bonds",
                "sec_subtype": self.determine_bond_subtype(description),
                "sec_symbol": None,
                "cusip": self.extract_cusip_from_text(bonds_section),
                "sec_description": description,
                "maturity_date": maturity_date,
                "coupon_rate": None,  # PDF-only field
                "beg_market_value": None,
                "quantity": None,
                "price_per_unit": None,
                "end_market_value": None,
                "accrued_int": None,  # PDF-only field
                "cost_basis": None,
                "unrealized_gain_loss": None,  # PDF-only field
                "estimated_ann_inc": None,  # PDF-only field
                "est_yield": None,
                "agency_ratings": None,  # PDF-only field
                "next_call_date": None,  # PDF-only field
                "call_price": None,  # PDF-only field
                "payment_freq": None,  # PDF-only field
                "bond_features": None  # PDF-only field
            }

            holdings.append(holding)
            self.processing_stats['holdings_extracted'] += 1
            self.processing_stats['security_types']['Bonds'] = \
                self.processing_stats['security_types'].get('Bonds', 0) + 1

    def extract_etps(self, text: str, holdings: List[Dict[str, Any]]):
        """Extract Exchange Traded Products from page text"""
        etp_pattern = r'Exchange Traded Products.*?(?=(?:Stocks|Bonds|Total|\n\n|\Z))'
        etp_match = re.search(etp_pattern, text, re.DOTALL | re.IGNORECASE)

        if not etp_match:
            return

        etp_section = etp_match.group(0)

        # Similar parsing to stocks for ETPs
        etp_line_pattern = r'([A-Z][^()]+)\s*\(([A-Z]{2,5})\)'

        for match in re.finditer(etp_line_pattern, etp_section):
            description = match.group(1).strip()
            symbol = match.group(2)

            holding = {
                "sec_type": "Exchange Traded Products",
                "sec_subtype": "Equity ETPs",  # Default
                "sec_symbol": symbol,
                "cusip": None,
                "sec_description": description,
                "beg_market_value": None,
                "quantity": None,
                "price_per_unit": None,
                "end_market_value": None,
                "cost_basis": None,
                "unrealized_gain_loss": None,  # PDF-only field
                "estimated_ann_inc": None,  # PDF-only field
                "est_yield": None  # PDF-only field
            }

            holdings.append(holding)
            self.processing_stats['holdings_extracted'] += 1
            self.processing_stats['security_types']['Exchange Traded Products'] = \
                self.processing_stats['security_types'].get('Exchange Traded Products', 0) + 1

    def determine_fund_subtype(self, description: str) -> str:
        """Determine mutual fund subtype from description"""
        desc_lower = description.lower()
        if any(term in desc_lower for term in ['bond', 'fixed', 'income']):
            return "Bond Funds"
        elif any(term in desc_lower for term in ['stock', 'equity', 'growth', 'value']):
            return "Stock Funds"
        elif any(term in desc_lower for term in ['money market', 'cash', 'short']):
            return "Short-Term Funds"
        else:
            return "Other Funds"

    def determine_stock_subtype(self, description: str) -> str:
        """Determine stock subtype from description"""
        desc_lower = description.lower()
        if any(term in desc_lower for term in ['preferred', 'pfd']):
            return "Preferred Stock"
        else:
            return "Common Stock"

    def determine_bond_subtype(self, description: str) -> str:
        """Determine bond subtype from description"""
        desc_lower = description.lower()
        if any(term in desc_lower for term in ['municipal', 'city', 'state', 'county']):
            return "Municipal Bonds"
        else:
            return "Corporate Bonds"

    def extract_symbol_from_description(self, description: str) -> Optional[str]:
        """Extract symbol from fund description if present"""
        # Look for symbols in parentheses
        symbol_match = re.search(r'\(([A-Z]{4,5})\)', description)
        return symbol_match.group(1) if symbol_match else None

    def extract_cusip_from_text(self, text: str) -> Optional[str]:
        """Extract CUSIP from bond text"""
        cusip_match = re.search(r'CUSIP[:]\s*([A-Z0-9]{9})', text)
        return cusip_match.group(1) if cusip_match else None

    def parse_bond_maturity(self, maturity_str: str) -> Optional[str]:
        """Convert bond maturity date to ISO format"""
        try:
            # Handle MM/DD/YY or MM/DD/YYYY format
            if len(maturity_str.split('/')[-1]) == 2:
                year = int(maturity_str.split('/')[-1])
                year = 2000 + year if year > 30 else 1900 + year  # Y2K assumption
                month, day = maturity_str.split('/')[:-1]
                return f"{year:04d}-{int(month):02d}-{int(day):02d}"
            else:
                month, day, year = maturity_str.split('/')
                return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        except:
            self.processing_stats['parsing_issues'].append(f"Could not parse bond maturity: {maturity_str}")
            return None

    def extract_account_data(self, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract account-level data and holdings"""
        accounts = []

        # Look for account information in page texts
        account_numbers = set()

        # Scan for account numbers in the text
        for page_key, page_data in structured_data.items():
            if not page_key.startswith('page_'):
                continue

            if 'full_page_text' in page_data:
                text = page_data['full_page_text']

                # Look for account numbers (format: Z##-######)
                acct_matches = re.findall(r'[XYZ]\d{2}-\d{6}', text)
                account_numbers.update(acct_matches)

        # Process each account found
        for acct_num in account_numbers:
            account = {
                "account_number": acct_num,
                "account_name": self.determine_account_name(acct_num, structured_data),
                "account_holder_name": self.extract_account_holder(structured_data),
                "account_type": self.determine_account_type(acct_num),
                "net_account_value": self.create_empty_net_account_value(),
                "income_summary": self.create_empty_income_summary(),
                "realized_gains": self.create_empty_realized_gains(),
                "holdings": []
            }

            # Extract holdings for this account
            for page_key, page_data in structured_data.items():
                if page_key.startswith('page_'):
                    page_holdings = self.extract_holdings_from_page(page_data)
                    account["holdings"].extend(page_holdings)

            accounts.append(account)
            self.processing_stats['accounts_found'] += 1

        return accounts

    def determine_account_name(self, account_num: str, structured_data: Dict[str, Any]) -> str:
        """Determine account name from context"""
        # Look for account type descriptions in text
        for page_key, page_data in structured_data.items():
            if page_key.startswith('page_') and 'full_page_text' in page_data:
                text = page_data['full_page_text']
                if account_num in text:
                    # Look for account type near the account number
                    if 'JOINT WROS' in text:
                        return "INDIVIDUAL - TOD"
                    elif 'CASH MANAGEMENT' in text:
                        return "CASH MANAGEMENT ACCOUNT"
                    elif 'BROKERAGE' in text:
                        return "BROKERAGE ACCOUNT"

        return "FIDELITY ACCOUNT"  # Default

    def extract_account_holder(self, structured_data: Dict[str, Any]) -> str:
        """Extract account holder name from document"""
        # Look in first page for name
        page_1 = structured_data.get('page_1', {})
        if 'full_page_text' in page_1:
            text = page_1['full_page_text']
            # Look for name pattern
            name_match = re.search(r'([A-Z]+ [A-Z]+ [A-Z]+)', text)
            if name_match:
                return name_match.group(1)

        return "ACCOUNT HOLDER"  # Default

    def determine_account_type(self, account_num: str) -> str:
        """Determine account type from account number pattern"""
        if account_num.startswith('Z24'):
            return "brokerage"
        elif account_num.startswith('Z27'):
            return "cash_management"
        else:
            return "investment"

    def create_empty_net_account_value(self) -> Dict[str, Optional[str]]:
        """Create empty net account value structure for PDF extraction"""
        return {
            "beg_net_acct_val_period": None,
            "beg_net_acct_val_ytd": None,
            "additions_period": None,
            "additions_ytd": None,
            "deposits_period": None,
            "deposits_ytd": None,
            "exchanges_in_period": None,
            "exchanges_in_ytd": None,
            "subtractions_period": None,
            "subtractions_ytd": None,
            "withdrawals_period": None,
            "withdrawals_ytd": None,
            "exchanges_out_period": None,
            "exchanges_out_ytd": None,
            "transaction_costs_period": None,
            "transaction_costs_ytd": None,
            "taxes_withheld_period": None,
            "taxes_withheld_ytd": None,
            "change_in_inc_val_period": None,
            "change_in_inc_val_ytd": None,
            "ending_net_acct_val_period": None,
            "ending_net_acct_val_ytd": None,
            "accrued_interest": None,
            "ending_net_acct_val_incl_ai": None
        }

    def create_empty_income_summary(self) -> Dict[str, Optional[str]]:
        """Create empty income summary structure for PDF extraction"""
        return {
            "taxable_total_period": None,
            "taxable_total_ytd": None,
            "divs_taxable_period": None,
            "divs_taxable_ytd": None,
            "stcg_taxable_period": None,
            "stcg_taxable_ytd": None,
            "int_taxable_period": None,
            "int_taxable_ytd": None,
            "ltcg_taxable_period": None,
            "ltcg_taxable_ytd": None,
            "tax_exempt_total_period": None,
            "tax_exempt_total_ytd": None,
            "divs_tax_exempt_period": None,
            "divs_tax_exempt_ytd": None,
            "stcg_tax_ex_period": None,
            "stcg_tax_ex_ytd": None,
            "int_tax_exempt_period": None,
            "int_tax_exempt_ytd": None,
            "ltcg_tax_ex_period": None,
            "ltcg_tax_ex_ytd": None,
            "roc_period": None,
            "roc_ytd": None,
            "incsumm_total_period": None,
            "incsumm_total_ytd": None
        }

    def create_empty_realized_gains(self) -> Dict[str, Optional[str]]:
        """Create empty realized gains structure for PDF extraction"""
        return {
            "netstgl_period": None,
            "netstgl_ytd": None,
            "stg_period": None,
            "stg_ytd": None,
            "netltgl_period": None,
            "netltgl_ytd": None,
            "ltg_period": None,
            "ltg_ytd": None,
            "net_gl_period": None,
            "net_gl_ytd": None
        }

    def calculate_field_completeness(self, accounts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate what percentage of fields were successfully extracted"""
        total_fields = 0
        populated_fields = 0

        for account in accounts:
            for holding in account['holdings']:
                for key, value in holding.items():
                    total_fields += 1
                    if value is not None:
                        populated_fields += 1

        return {
            'basic_holdings_fields': populated_fields / total_fields if total_fields > 0 else 0,
            'pdf_only_fields': 0.0,  # These would be null in structured text approach
            'total_completeness': populated_fields / total_fields if total_fields > 0 else 0
        }

    def generate_complete_json(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the complete holdings JSON"""
        # Extract metadata and document info
        extraction_metadata, document_data = self.extract_document_metadata(structured_data)

        # Extract accounts and holdings
        accounts = self.extract_account_data(structured_data)

        # Calculate field completeness
        self.processing_stats['field_completeness'] = self.calculate_field_completeness(accounts)

        # Build final JSON structure
        output_json = {
            "extraction_metadata": extraction_metadata,
            "document_data": document_data,
            "accounts": accounts
        }

        # Calculate MD5 hash of the JSON content
        json_content = json.dumps(output_json, sort_keys=True, indent=2)
        md5_hash = hashlib.md5(json_content.encode()).hexdigest()
        output_json["extraction_metadata"]["json_output_md5_hash"] = md5_hash

        return output_json

    def save_output(self, output_json: Dict[str, Any]):
        """Save the complete JSON to output file"""
        with open(self.output_file, 'w') as f:
            json.dump(output_json, f, indent=2)

    def generate_comparison_report(self) -> Dict[str, Any]:
        """Generate comparison report analyzing the extraction"""
        end_time = datetime.now()
        processing_time = (end_time - self.processing_stats['start_time']).total_seconds()

        # Estimate token usage for this approach vs direct PDF
        input_file_size = 0
        try:
            with open(self.input_file, 'r') as f:
                input_content = f.read()
                input_file_size = len(input_content)
        except:
            pass

        # Rough token estimation (1 token ≈ 4 characters for JSON)
        estimated_tokens = input_file_size // 4

        report = {
            "extraction_summary": {
                "processing_time_seconds": processing_time,
                "accounts_processed": self.processing_stats['accounts_found'],
                "total_holdings_extracted": self.processing_stats['holdings_extracted'],
                "security_types_found": self.processing_stats['security_types']
            },
            "field_completeness": {
                "basic_fields_from_structured_text": self.processing_stats['field_completeness'].get('basic_holdings_fields', 0) * 100,
                "pdf_only_fields_missing": [
                    "estimated_ann_inc", "est_yield", "unrealized_gain_loss",
                    "bond_specific_fields", "options_fields", "complete_document_level_data"
                ],
                "total_completeness_percentage": self.processing_stats['field_completeness'].get('total_completeness', 0) * 100
            },
            "data_quality_issues": {
                "parsing_errors": len(self.processing_stats['parsing_issues']),
                "parsing_details": self.processing_stats['parsing_issues'][:10]  # First 10 issues
            },
            "token_efficiency": {
                "structured_text_input_size_chars": input_file_size,
                "estimated_tokens_for_processing": estimated_tokens,
                "comparison_note": "This is intermediate format - would need additional LLM pass for PDF-only fields"
            },
            "methodology_assessment": {
                "advantages": [
                    "Fast parsing of structured data",
                    "No OCR errors for basic holdings data",
                    "Reduced token usage for basic extraction"
                ],
                "limitations": [
                    "Missing critical fields that require PDF text analysis",
                    "Limited accuracy for complex security parsing",
                    "Still requires LLM pass for complete data",
                    "Table structure parsing challenges"
                ],
                "recommendation": "Hybrid approach beneficial for basic data but direct PDF processing needed for completeness"
            }
        }

        return report

    def process(self) -> Dict[str, Any]:
        """Main processing function"""
        try:
            print("Loading structured text data...")
            structured_data = self.load_structured_data()

            print("Generating complete holdings JSON...")
            output_json = self.generate_complete_json(structured_data)

            print("Saving output...")
            self.save_output(output_json)

            print("Generating comparison report...")
            report = self.generate_comparison_report()

            return {
                "success": True,
                "output_file": self.output_file,
                "report": report
            }

        except Exception as e:
            error_report = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "partial_stats": self.processing_stats
            }
            return error_report


def main():
    """Main execution function"""
    input_file = "/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-08_KernBrok+KernCMA_extracted_text_2025.09.26_16.55.json"
    output_file = "/Users/richkernan/Projects/Finances/documents/4extractions/Fid_Stmnt_2025-08_test_holdings_extraction.json"

    processor = StructuredTextProcessor(input_file, output_file)
    result = processor.process()

    if result["success"]:
        print(f"\n✅ SUCCESS: Holdings JSON generated")
        print(f"📄 Output file: {result['output_file']}")
        print(f"\n📊 EXTRACTION SUMMARY:")

        report = result["report"]
        summary = report["extraction_summary"]
        print(f"  • Processing time: {summary['processing_time_seconds']:.2f} seconds")
        print(f"  • Accounts processed: {summary['accounts_processed']}")
        print(f"  • Holdings extracted: {summary['total_holdings_extracted']}")
        print(f"  • Security types: {', '.join(summary['security_types_found'].keys())}")

        completeness = report["field_completeness"]
        print(f"\n📈 FIELD COMPLETENESS:")
        print(f"  • Basic fields: {completeness['basic_fields_from_structured_text']:.1f}%")
        print(f"  • Total completeness: {completeness['total_completeness_percentage']:.1f}%")

        efficiency = report["token_efficiency"]
        print(f"\n⚡ TOKEN EFFICIENCY:")
        print(f"  • Input size: {efficiency['structured_text_input_size_chars']:,} characters")
        print(f"  • Estimated tokens: {efficiency['estimated_tokens_for_processing']:,}")

        issues = report["data_quality_issues"]
        if issues["parsing_errors"] > 0:
            print(f"\n⚠️  DATA QUALITY ISSUES:")
            print(f"  • Parsing errors: {issues['parsing_errors']}")

        assessment = report["methodology_assessment"]
        print(f"\n💡 ASSESSMENT:")
        print(f"  • Recommendation: {assessment['recommendation']}")

        # Save detailed report
        report_file = output_file.replace('.json', '_comparison_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📋 Detailed report saved: {report_file}")

    else:
        print(f"\n❌ ERROR: {result['error']}")
        print(f"\n🔍 Details:\n{result.get('traceback', 'No traceback available')}")

        # Save error report
        error_file = output_file.replace('.json', '_error_report.json')
        with open(error_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📋 Error details saved: {error_file}")


if __name__ == "__main__":
    main()