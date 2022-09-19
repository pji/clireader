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

    def test_example(self):
        """When encountering an example begin macro (.EX), the Lexer
        should begin collecting the following lines into a token until
        an example end macro (.EE) is encountered. Then return the
        correct token.
        """
        exp = (man.Example('spam'),)
        text = (
            '.EX\n'
            f'{exp[0].text}\n'
            '.EE\n'
        )
        self.lex_test(exp, text)

    def test_paragraph(self):
        """When encountering a paragraph macro (.P), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph('spam eggs\nbacon ham'),)
        text = (
            '.P\n'
            f'{exp[0].text[:9]}\n'
            f'{exp[0].text[10:]}'
        )
        self.lex_test(exp, text)

    def test_paragraph_lp(self):
        """When encountering a paragraph macro (.LP), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph('spam eggs\nbacon ham'),)
        text = (
            '.LP\n'
            f'{exp[0].text[:9]}\n'
            f'{exp[0].text[10:]}'
        )
        self.lex_test(exp, text)

    def test_paragraph_pp(self):
        """When encountering a paragraph macro (.PP), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph('spam eggs\nbacon ham'),)
        text = (
            '.PP\n'
            f'{exp[0].text[:9]}\n'
            f'{exp[0].text[10:]}'
        )
        self.lex_test(exp, text)

    def test_relative_indent_end(self):
        """When encountering a relative indent start header macro (.RE)
        and up to one parameter, the Lexer should return the correct
        token.
        """
        exp = (man.RelativeIndentEnd('2'),)
        text = f'.RE {exp[0].indent}'
        self.lex_test(exp, text)

    def test_relative_indent_end_without_param(self):
        """When encountering a relative indent start header macro (.RE)
        without a parameter, the Lexer should return the correct token.
        """
        exp = (man.RelativeIndentEnd('1'),)
        text = f'.RE'
        self.lex_test(exp, text)

    def test_relative_indent_start(self):
        """When encountering a relative indent start header macro (.RS)
        without a parameter, the Lexer should return the correct token.
        """
        exp = (man.RelativeIndentStart('2'),)
        text = f'.RS {exp[0].indent}'
        self.lex_test(exp, text)

    def test_relative_indent_start_without_param(self):
        """When encountering a relative indent start header macro (.RS)
        and up to one parameter, the Lexer should return the correct
        token.
        """
        exp = (man.RelativeIndentStart('1'),)
        text = f'.RS'
        self.lex_test(exp, text)

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

    def test_taged_paragraph(self):
        """When encountering a tagged paragraph macro (.TP), the Lexer
        should collect an optional parameter on the same line as the
        indentation level, a parameter on the next line as a tag, and
        the following lines as the paragraph. It should then return a
        TaggedParagraph token.
        """
        exp = (man.TaggedParagraph('1\nspam\neggs bacon ham'),)
        text = (
            f'.TP {exp[0].indent}\n'
            f'{exp[0].tag}\n'
            f'{exp[0].text}'
        )
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
