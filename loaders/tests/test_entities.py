"""
Unit Tests for Entities Module

Created: 09/23/25 11:07AM
Purpose: Test entity creation and caching functions
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import entities
from src import transform

class TestEntities(unittest.TestCase):

    def test_infer_account_type_ira(self):
        """Test inferring IRA account type."""
        result = transform.infer_account_type("Traditional IRA")
        self.assertEqual(result, "ira")

    def test_infer_account_type_roth_ira(self):
        """Test inferring Roth IRA account type."""
        result = transform.infer_account_type("Roth IRA")
        self.assertEqual(result, "roth_ira")

    def test_infer_account_type_401k(self):
        """Test inferring 401k account type."""
        result = transform.infer_account_type("401(k) Plan")
        self.assertEqual(result, "401k")

    def test_infer_account_type_cash_management(self):
        """Test inferring cash management account type."""
        result = transform.infer_account_type("Cash Management Account")
        self.assertEqual(result, "cash_management")

    def test_infer_account_type_default_brokerage(self):
        """Test default account type is brokerage."""
        result = transform.infer_account_type("Investment Account")
        self.assertEqual(result, "brokerage")

    # Note: Database-dependent tests would require mock database connection
    # These tests focus on the logic that doesn't require database access

if __name__ == '__main__':
    unittest.main()