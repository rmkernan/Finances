"""
Unit Tests for Validator Module

Created: 09/23/25 11:07AM
Purpose: Test JSON validation functions
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import validator

class TestValidator(unittest.TestCase):

    def test_validate_json_structure_positions_valid(self):
        """Test valid positions JSON structure."""
        data = {
            "extraction_metadata": {
                "file_hash": "abc123",
                "file_path": "/test/file.pdf",
                "extraction_date": "2024-09-23"
            },
            "holdings": []
        }
        result = validator.validate_json_structure(data, "positions")
        self.assertTrue(result)

    def test_validate_json_structure_activities_valid(self):
        """Test valid activities JSON structure."""
        data = {
            "extraction_metadata": {
                "file_hash": "abc123",
                "file_path": "/test/file.pdf",
                "extraction_date": "2024-09-23"
            },
            "activities": []
        }
        result = validator.validate_json_structure(data, "activities")
        self.assertTrue(result)

    def test_validate_json_structure_missing_metadata(self):
        """Test validation fails when metadata is missing."""
        data = {"holdings": []}
        with self.assertRaises(ValueError) as context:
            validator.validate_json_structure(data, "positions")
        self.assertIn("Missing extraction_metadata", str(context.exception))

    def test_validate_json_structure_missing_file_hash(self):
        """Test validation fails when file_hash is missing."""
        data = {
            "extraction_metadata": {
                "file_path": "/test/file.pdf",
                "extraction_date": "2024-09-23"
            },
            "holdings": []
        }
        with self.assertRaises(ValueError) as context:
            validator.validate_json_structure(data, "positions")
        self.assertIn("Missing metadata field: file_hash", str(context.exception))

if __name__ == '__main__':
    unittest.main()