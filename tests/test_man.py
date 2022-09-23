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

    # Document structure macros.
    def test_example(self):
        """When encountering an example begin macro (.EX), the Lexer
        should begin collecting the following lines into a token until
        an example end macro (.EE) is encountered. Then return the
        correct token.
        """
        exp = (man.Example([
            man.Text('spam'),
            man.Text('eggs bacon'),
        ]),)
        text = (
            '.EX\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
            '.EE\n'
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

    # Paragraph macros.
    def test_indented_paragraph(self):
        """When encountering an indented paragraph macro (.IP), the
        Lexer should begin collecting the following lines into a token
        then return a Paragraph token containing the collected text.
        """
        exp = (
            man.IndentedParagraph(
                'spam',
                '1',
                [
                    man.Text('eggs'),
                    man.Text('bacon ham'),
                    man.Bold('tomato'),
                ],
            ),
        )
        text = (
            f'.IP {exp[0].tag} {exp[0].indent}\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
            f'.B {exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_paragraph(self):
        """When encountering a paragraph macro (.P), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
        )
        self.lex_test(exp, text)

    def test_paragraph_lp(self):
        """When encountering a paragraph macro (.LP), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
        )
        self.lex_test(exp, text)

    def test_paragraph_pp(self):
        """When encountering a paragraph macro (.PP), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
        )
        self.lex_test(exp, text)

    def test_tagged_paragraph(self):
        """When encountering a tagged paragraph macro (.TP), the Lexer
        should collect an optional parameter on the same line as the
        indentation level, a parameter on the next line as a tag, and
        the following lines as the paragraph. It should then return a
        TaggedParagraph token.
        """
        exp = (
            man.TaggedParagraph(
                '1',
                ['spam',],
                [
                    man.Text('eggs bacon ham'),
                    man.Text('baked beans'),
                    man.Bold('tomato'),
                ]
            ),
        )
        text = (
            f'.TP {exp[0].indent}\n'
            f'{exp[0].tag[0]}\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
            f'.B {exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_tagged_paragraph_with_TQ(self):
        """When encountering a tagged paragraph macro (.TQ), the Lexer
        should collect an optional parameter on the same line as the
        indentation level, a parameter on the next line as a tag, and
        the following lines as the paragraph. It should then return a
        TaggedParagraph token.
        """
        exp = (
            man.TaggedParagraph(
                '1',
                ['spam', 'tomato', 'flapjacks'],
                [
                    man.Text('eggs bacon ham'),
                    man.Text('baked beans'),
                ]
            ),
        )
        text = (
            f'.TP {exp[0].indent}\n'
            f'{exp[0].tag[0]}\n'
            '.TQ\n'
            f'{exp[0].tag[1]}\n'
            '.TQ\n'
            f'{exp[0].tag[2]}\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
        )
        self.lex_test(exp, text)

    # Command synopsis macros.
    def test_synopsis(self):
        """When encountering a synopsis begin macro (.SY), the lexer
        should begin collecting lines and tokens until it reaches a
        synopsis end macro (.YS) macro. The lexer should then return
        a Synopsis token containing the collected tokens.
        """
        exp = (man.Synopsis('spam'),)
        text = (
            f'.SY {exp[0].command}\n'
            '.YS'
        )
        self.lex_test(exp, text)

    def test_synopsis_with_option(self):
        """When encountering an option macro (.OP) after a synopsis
        begin macro (.SY) but before a synopsis end macro (.YS), the
        lexer should. The lexer should then return a Synopsis token
        containing the collected tokens.
        """
        exp = (man.Synopsis('spam', [man.Option('-e', 'eggs'),]),)
        text = (
            f'.SY {exp[0].command}\n'
            f'.OP {exp[0].contents[0].option_name} '
            f'{exp[0].contents[0].option_argument}\n'
            '.YS'
        )
        self.lex_test(exp, text)

    # Hyperlink and email macros.
    def test_email_address(self):
        """When encountering an email address begin macro (.MT), the
        lexer should collect the email address from the parameter and
        the following lines as hypertext until it reaches an email
        address end macro (.ME). It should then return an EmailAddress
        token with the collected data.
        """
        exp = (man.EmailAddress(
            'fred.foonly@fubar.net',
            [man.Text('Fred Foonly'),],
            '!'
        ),)
        text = (
            f'.MT {exp[0].address}\n'
            f'{exp[0].contents[0].text}\n'
            f'.ME {exp[0].punctuation}\n'
        )
        self.lex_test(exp, text)

    def test_url(self):
        """When encountering a URL begin macro (.UR), the lexer should
        collect the URL from the parameter and the following lines as
        hypertext until it reaches an URL end macro (.UE). It should
        then return a Url token with the collected data.
        """
        exp = (man.Url(
            'https://www.gnu.org/software/groff',
            [man.Text('groff'),],
            '!'
        ),)
        text = (
            f'.UR {exp[0].address}\n'
            f'{exp[0].contents[0].text}\n'
            f'.UE {exp[0].punctuation}\n'
        )
        self.lex_test(exp, text)

    # Font style macros.
    def test_bold(self):
        """When encountering a bold macro (.B) while collecting lines
        for a multiline macro, the lexer should create a Bold token
        with the given text and add the token to the token for the
        multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Bold('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.B {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_bold_with_param_in_next_line(self):
        """When encountering a bold macro (.B) while collecting lines
        for a multiline macro, the lexer should create a Bold token
        with the given text and add the token to the token for the
        multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Bold('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.B\n'
            f'{exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_italics(self):
        """When encountering an italics macro (.I) while collecting
        lines for a multiline macro, the lexer should create a Italics
        token with the given text and add the token to the token for
        the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Italics('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.I {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_italics_with_param_in_next_line(self):
        """When encountering an italics macro (.I) while collecting
        lines for a multiline macro, the lexer should create an Italics
        token with the given text and add the token to the token for
        the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Italics('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.I\n'
            f'{exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_small(self):
        """When encountering an small macro (.SM) while collecting
        lines for a multiline macro, the lexer should create a Small
        token with the given text and add the token to the token for
        the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Small('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.SM {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_small_with_param_in_next_line(self):
        """When encountering a small macro (.SM) while collecting
        lines for a multiline macro, the lexer should create a Small
        token with the given text and add the token to the token for
        the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.Small('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.SM\n'
            f'{exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_small_bold(self):
        """When encountering an small bold macro (.SB) while collecting
        lines for a multiline macro, the lexer should create a SmallBold
        token with the given text and add the token to the token for
        the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.SmallBold('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.SB {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_small_bold_with_param_in_next_line(self):
        """When encountering a small bold macro (.SB) while collecting
        lines for a multiline macro, the lexer should create a SmallBold
        token with the given text and add the token to the token for
        the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.SmallBold('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.SB\n'
            f'{exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)
