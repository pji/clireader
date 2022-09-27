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

    def test_section_with_following_text(self):
        """When encountering a section header macro (.SH) with a
        parameter on the next line and following text lines, the
        lexer should return the correct token.
        """
        exp = (man.Section(
            'spam',
            [
                man.Text('eggs bacon'),
                man.Text('ham baked beans'),
            ]
        ),)
        text = (
            '.SH\n'
            f'{exp[0].heading_text}\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
        )
        self.lex_test(exp, text)

    def test_subheading(self):
        """When encountering a title header macro (.TH) and up to
        five parameters, the Lexer should return the correct token.
        """
        exp = (man.Subheading('spam'),)
        text = f'.SS {exp[0].subheading_text}'
        self.lex_test(exp, text)

    def test_subheading_with_following_text(self):
        """When encountering a subheading macro (.SS) with a
        parameter on the next line and following text lines, the
        lexer should return the correct token.
        """
        exp = (man.Subheading(
            'spam',
            [
                man.Text('eggs bacon'),
                man.Text('ham baked beans'),
            ]
        ),)
        text = (
            '.SS\n'
            f'{exp[0].subheading_text}\n'
            f'{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
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

    def test_paragraph_with_empty_token(self):
        """When encountering a paragraph macro (.P), the Lexer
        should begin collecting the following lines into a token then
        return a Paragraph token containing the collected text.
        """
        exp = (man.Paragraph([
            man.Empty('baked beans'),
            man.Text('spam eggs'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'.{exp[0].contents[0].text}\n'
            f'{exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
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

    def test_synopsis_with_option_and_multiple_synopses(self):
        """When encountering a synopsis begin macro (.SY) after a
        synopsis begin macro (.SY) but before a synopsis end macro
        (.YS), the lexer should then return a Synopsis token
        containing the collected tokens.
        """
        exp = (man.Synopsis('spam', [
            man.Option('-e', 'eggs'),
            man.Option('-b', 'bacon'),
            man.Synopsis('ham', []),
            man.Option('-f', 'flapjacks'),
        ]),)
        text = (
            f'.SY {exp[0].command}\n'
            f'.OP {exp[0].contents[0].option_name} '
            f'{exp[0].contents[0].option_argument}\n'
            f'.OP {exp[0].contents[1].option_name} '
            f'{exp[0].contents[1].option_argument}\n'
            f'.SY {exp[0].contents[2].command}\n'
            f'.OP {exp[0].contents[3].option_name} '
            f'{exp[0].contents[3].option_argument}\n'
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

    def test_bold_italics(self):
        """When encountering a bold italics macro (.BI) while collecting
        lines for a multiline macro, the lexer should create a
        BoldItalic token with the given text and add the token to the
        token for the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.BoldItalic('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.BI {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_bold_roman(self):
        """When encountering a bold roman macro (.BR) while collecting
        lines for a multiline macro, the lexer should create a
        BoldRoman token with the given text and add the token to the
        token for the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.BoldRoman('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.BR {exp[0].contents[1].text}\n'
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

    def test_italic_bold(self):
        """When encountering a italics bold macro (.IB) while collecting
        lines for a multiline macro, the lexer should create a
        ItalicBold token with the given text and add the token to the
        token for the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.ItalicBold('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.IB {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_italic_roman(self):
        """When encountering a italics roman macro (.IR) while collecting
        lines for a multiline macro, the lexer should create a
        ItalicRoman token with the given text and add the token to the
        token for the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.ItalicRoman('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.IR {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_roman_bold(self):
        """When encountering a roman bold macro (.RB) while collecting
        lines for a multiline macro, the lexer should create a
        RomanBold token with the given text and add the token to the
        token for the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.RomanBold('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.RB {exp[0].contents[1].text}\n'
            f'{exp[0].contents[2].text}\n'
        )
        self.lex_test(exp, text)

    def test_roman_italic(self):
        """When encountering a roman italic macro (.RI) while collecting
        lines for a multiline macro, the lexer should create a
        RomanItalic token with the given text and add the token to the
        token for the multiline macro.
        """
        exp = (man.Paragraph([
            man.Text('spam eggs'),
            man.RomanItalic('baked beans'),
            man.Text('bacon ham'),
        ]),)
        text = (
            '.P\n'
            f'{exp[0].contents[0].text}\n'
            f'.RI {exp[0].contents[1].text}\n'
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

    def test_text(self):
        """When encountering a line that doesn't start with a macro,
        the lexer should create a Text token with the given text.
        """
        exp = (
            man.Text('spam eggs'),
            man.Text('bacon ham'),
        )
        text = (
            f'{exp[0].text}\n'
            f'{exp[1].text}\n'
        )
        self.lex_test(exp, text)

    # Other macros.
    def test_empty(self):
        """When encountering a line that starts with a period but
        doesn't contain a recognized macro, the lexer should
        collect the line and return it in a Empty token.
        """
        exp = (man.Empty('spam'),)
        text = (
            '.spam\n'
        )
        self.lex_test(exp, text)


class ParseTestCase(ut.TestCase):
    def setUp(self):
        self.width = 24

    def parse_test(self, exp, tokens):
        """Determine if parsing the given tokens returns the expected
        result.
        """
        # Run test.
        act = man.parse(tokens, self.width)

        # Determine test result.
        self.assertEqual(exp, act)

    # Parsing test.
    def test_simplest_doc(self):
        """Given the simplest document, the parse should return a
        string containing its contents.
        """
        exp = 'spam\n'
        tokens = (man.Text('spam'),)
        self.parse_test(exp, tokens)

    def test_doc_with_simple_title(self):
        """Given the simplest document, the parser should return a
        string containing its contents.
        """
        exp = (
            'SPAM                SPAM\n'
            '\n'
            '\n'
            '\n'
            'eggs\n'
            '\n'
            '\n'
            '\n'
            '                    SPAM\n'
        )
        tokens = (
            man.Title('spam'),
            man.Text('eggs'),
        )
        self.parse_test(exp, tokens)

    def test_doc_with_complex_title(self):
        """Given a document with a complex title, the parser should
        return a string containing its contents.
        """
        exp = (
            'SPAM(1)  bacon   SPAM(1)\n'
            '\n'
            '\n'
            '\n'
            'eggs\n'
            '\n'
            '\n'
            '\n'
            'ham    1/1/70    SPAM(1)\n'
        )
        tokens = (
            man.Title('spam', '1', '1/1/70', 'ham', 'bacon'),
            man.Text('eggs'),
        )
        self.parse_test(exp, tokens)


class ParseTokenTestCase(ut.TestCase):
    def setUp(self):
        self.width = 24

        self.bold = '\x1b[1m'
        self.nml = '\x1b(B\x1b[m'
        self.udln = '\x1b[4m'

    def parse_test(self, exp, token):
        """Determine if parsing the given tokens returns the expected
        result.
        """
        # Run test.
        act = token.parse(self.width)

        # Determine test result.
        self.assertEqual(exp, act)

    # Document structure tokens.
    def test_example(self):
        """Given a terminal width, Example.parse() should return a
        string representing the object. Since filling is disabled,
        the contents are not reflowed for the given width but are
        instead truncated.
        """
        exp = (
            'spam eggs bacon ham bake\n'
            'spam\n'
            'spam eggs\n'
            'spam eggs bacon ham bake\n'
        )
        token = man.Example([
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    def test_section(self):
        """Given a terminal width, Section.parse() should return a
        string representing the object.
        """
        exp = (
            f'{self.bold}spam{self.nml}\n'
            '    spam eggs bacon ham\n'
            '    baked beans spam\n'
            '    spam eggs spam eggs\n'
            '    bacon ham baked\n'
            '    beans tomato\n'
        )
        token = man.Section('spam', [
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    def test_subheading(self):
        """Given a terminal width, Subheading.parse() should return
        a string representing the object.
        """
        exp = (
            f'  {self.bold}spam{self.nml}\n'
            '    spam eggs bacon ham\n'
            '    baked beans spam\n'
            '    spam eggs spam eggs\n'
            '    bacon ham baked\n'
            '    beans tomato\n'
        )
        token = man.Subheading('spam', [
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    # Paragraph tokens.
    def test_indented_paragraph(self):
        """Given a terminal width, IndentedParagraph.parse() should
        return a string representing the object.
        """
        exp = (
            '    spam eggs bacon ham\n'
            '    baked beans spam\n'
            '    spam eggs spam eggs\n'
            '    bacon ham baked\n'
            '    beans tomato\n'
        )
        token = man.IndentedParagraph(contents=[
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    def test_indented_paragraph_with_tag(self):
        """Given a terminal width, IndentedParagraph.parse() should
        return a string representing the object.
        """
        exp = (
            'spam\n'
            '    spam eggs bacon ham\n'
            '    baked beans spam\n'
            '    spam eggs spam eggs\n'
            '    bacon ham baked\n'
            '    beans tomato\n'
        )
        token = man.IndentedParagraph('spam', '4', [
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    def test_paragraph(self):
        """Given a terminal width, Paragraph.parse() should return
        a string representing the object.
        """
        exp = (
            '    spam eggs bacon ham\n'
            '    baked beans spam\n'
            '    spam eggs spam eggs\n'
            '    bacon ham baked\n'
            '    beans tomato\n'
        )
        token = man.Paragraph([
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    def test_tagged_paragraph(self):
        """Given a terminal width, TaggedParagraph.parse() should
        return a string representing the object.
        """
        exp = (
            'spam\n'
            '    spam eggs bacon ham\n'
            '    baked beans spam\n'
            '    spam eggs spam eggs\n'
            '    bacon ham baked\n'
            '    beans tomato\n'
        )
        token = man.TaggedParagraph('4', 'spam', [
            man.Text('spam eggs bacon ham baked beans'),
            man.Text('spam'),
            man.Text('spam eggs'),
            man.Text('spam eggs bacon ham baked beans tomato'),
        ])
        self.parse_test(exp, token)

    # Command synopsis tokens.
    def test_option(self):
        """Given a terminal width, Option.parse() should
        return a string representing the object.
        """
        exp = f'[{self.bold}-s{self.nml} {self.udln}spam{self.nml}]'
        token = man.Option('-s', 'spam')
        self.parse_test(exp, token)

    def test_synopsis(self):
        """Given a terminal width, Synopsis.parse() should
        return a string representing the object.
        """
        exp = (
            f'{self.bold}spam{self.nml} '
            f'[{self.bold}-s{self.nml} {self.udln}spam{self.nml}] '
            f'[{self.bold}-e{self.nml} {self.udln}eggs{self.nml}]\n'
            f'     [{self.bold}-b{self.nml} {self.udln}bacon{self.nml}]\n'
        )
        token = man.Synopsis('spam', [
            man.Option('-s', 'spam'),
            man.Option('-e', 'eggs'),
            man.Option('-b', 'bacon')
        ])
        self.parse_test(exp, token)

    def test_synopsis_with_multiple_synopses(self):
        """Given a terminal width, Synopsis.parse() should
        return a string representing the object. If there are
        multiple commands within the Synopsis, the string should
        not contain a blank line between the end of the last
        option of the last command and the next command.
        """
        exp = (
            f'{self.bold}spam{self.nml} '
            f'[{self.bold}-s{self.nml} {self.udln}spam{self.nml}] '
            f'[{self.bold}-e{self.nml} {self.udln}eggs{self.nml}]\n'
            f'     [{self.bold}-b{self.nml} {self.udln}bacon{self.nml}]\n'
            f'{self.bold}ham{self.nml} '
            f'[{self.bold}-f{self.nml} {self.udln}flapjack{self.nml}]\n'
        )
        token = man.Synopsis('spam', [
            man.Option('-s', 'spam'),
            man.Option('-e', 'eggs'),
            man.Option('-b', 'bacon'),
            man.Synopsis('ham', []),
            man.Option('-f', 'flapjack')
        ])
        self.parse_test(exp, token)

#           '012345678901234567890123'
