"""
Unit Tests for Transform Module

Created: 09/23/25 11:07AM
Purpose: Test data transformation functions
"""

import unittest
from datetime import date
from decimal import Decimal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import transform

class TestTransform(unittest.TestCase):

    def test_parse_date_iso(self):
        """Test parsing ISO format dates."""
        result = transform.parse_date("2024-09-23")
        self.assertEqual(result, date(2024, 9, 23))

    def test_parse_date_mmddyyyy(self):
        """Test parsing MM/DD/YYYY dates."""
        result = transform.parse_date("09/23/2024")
        self.assertEqual(result, date(2024, 9, 23))

    def test_parse_date_mmdd_with_year(self):
        """Test parsing MM/DD with provided year."""
        result = transform.parse_date("09/23", tax_year=2024)
        self.assertEqual(result, date(2024, 9, 23))

    def test_parse_amount_simple(self):
        """Test parsing simple amounts."""
        result = transform.parse_amount("1234.56")
        self.assertEqual(result, Decimal("1234.56"))

    def test_parse_amount_with_symbols(self):
        """Test parsing amounts with $ and commas."""
        result = transform.parse_amount("$1,234.56")
        self.assertEqual(result, Decimal("1234.56"))

    def test_parse_amount_negative(self):
        """Test parsing negative amounts with parentheses."""
        result = transform.parse_amount("(1234.56)")
        self.assertEqual(result, Decimal("-1234.56"))

    def test_infer_transaction_type_dividend(self):
        """Test inferring dividend transaction type."""
        result = transform.infer_transaction_type("ORDINARY DIVIDEND")
        self.assertEqual(result, "dividend")

    def test_infer_transaction_type_buy(self):
        """Test inferring buy transaction type."""
        result = transform.infer_transaction_type("YOU BOUGHT 100 SHARES")
        self.assertEqual(result, "buy")

if __name__ == '__main__':
    unittest.main()