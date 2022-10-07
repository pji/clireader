"""
test_main
~~~~~~~~~

Unit tests for the __main__ module of the clireader package.
"""
import unittest as ut
from unittest.mock import call, patch
import sys

from clireader import __main__ as main


# Test cases.
class ParseCliTestCase(ut.TestCase):
    def setUp(self):
        self.argv = sys.argv
        self.filename = 'tests/data/spam.txt'
        self.error = (
            'Error: clireader must be invoked with a file.\n'
            f'Syntax: {self.argv[0]} path/to/file'
        )

    def tearDown(self):
        sys.argv = self.argv

    # Tests.
    @patch('clireader.clireader.main')
    def test_with_filename_arg(self, mock_main):
        """When given a filename as an option, parse_cli should load
        that file in the viewer.
        """
        # Expected value.
        exp = [
            call(self.filename, wrap_mode='detect'),
        ]

        # Test data and state.
        sys.argv = [
            'python -m clireader',
            self.filename,
        ]

        # Run test and gather actuals.
        main.parse_cli()
        act = mock_main.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.main')
    def test_with_filename_and_long_wrap_arg(self, mock_main):
        """When given a filename and '-l' as an option, parse_cli
        should load that file in the viewer only rewrapping the long
        lines.
        """
        # Expected value.
        exp = [
            call(self.filename, wrap_mode='long'),
        ]

        # Test data and state.
        sys.argv = [
            'python -m clireader',
            self.filename,
            '-l',
        ]

        # Run test and gather actuals.
        main.parse_cli()
        act = mock_main.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.main')
    def test_with_filename_and_man_wrap_arg(self, mock_main):
        """When given a filename and '-l' as an option, parse_cli
        should load that file in the viewer only rewrapping the long
        lines.
        """
        # Expected value.
        exp = [
            call(self.filename, wrap_mode='man'),
        ]

        # Test data and state.
        sys.argv = [
            'python -m clireader',
            self.filename,
            '-m',
        ]

        # Run test and gather actuals.
        main.parse_cli()
        act = mock_main.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.main')
    def test_with_filename_and_no_wrap_arg(self, mock_main):
        """When given a filename and '-n' as an option, parse_cli
        should load that file in the viewer without rewrapping the
        text.
        """
        # Expected value.
        exp = [
            call(self.filename, wrap_mode='no_wrap'),
        ]

        # Test data and state.
        sys.argv = [
            'python -m clireader',
            self.filename,
            '-n',
        ]

        # Run test and gather actuals.
        main.parse_cli()
        act = mock_main.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)
