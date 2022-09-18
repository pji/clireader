"""
test_man
~~~~~~~~

Unit tests for the clireader.man module.
"""
import unittest as ut

from clireader import man


class LexTestCase(ut.TestCase):
    def lex_test(self, exp, text):
        """The common test for the lex function."""
        # Run test.
        act = man.lex(text)

        # Determine test results.
        self.assertTupleEqual(exp, act)

    def test_section(self):
        """When encountering a section header macro (.SH) and one
        parameter, the Lexer should return the correct token.
        """
        exp = (man.Section('spam'),)
        text = f'.SH {exp[0].heading_text}'
        self.lex_test(exp, text)

    def test_section_with_params_in_next_line(self):
        """When encountering a section header macro (.SH) with a
        parameter on the next line, the Lexer should return the correct
        token.
        """
        exp = (man.Section('spam'),)
        text = f'.SH\n{exp[0].heading_text}'
        self.lex_test(exp, text)

    def test_subheading(self):
        """When encountering a title header macro (.TH) and up to
        five parameters, the Lexer should return the correct token.
        """
        exp = (man.Subheading('spam'),)
        text = f'.SS {exp[0].subheading_text}'
        self.lex_test(exp, text)

    def test_title(self):
        """When encountering a title header macro (.TH) and up to
        five parameters, the Lexer should return the correct token.
        """
        exp = (
            man.Title('spam', '1', 'eggs', 'bacon', 'ham'),
        )
        text = (
            f'.TH {exp[0].title}'
            f' {exp[0].section}'
            f' {exp[0].footer_middle}'
            f' {exp[0].footer_inside}'
            f' {exp[0].header_middle}'
        )
        self.lex_test(exp, text)
