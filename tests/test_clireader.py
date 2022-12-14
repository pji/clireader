"""
test_clireader
~~~~~~~~~~~~~~

Unit tests for the clireader.clireader module.
"""
import unittest as ut
from unittest.mock import call, Mock, patch, PropertyMock

from blessed import Terminal
from blessed.keyboard import Keystroke

from clireader import clireader


# Base test class.
class TerminalTestCase(ut.TestCase):
    topleft = '\x1b[1;2H'
    bold = '\x1b[1m'
    nml = '\x1b(B\x1b[m'
    rev = '\x1b[7m'
    loc = '\x1b[{};{}H'

    def setUp(self):
        self.height = 8
        self.width = 24
        self.command_list = [
            clireader.Command('f', 'flow'),
            clireader.Command('j', 'jump'),
            clireader.Command('n', 'next'),
            clireader.Command('x', 'exit'),
        ]

        self.print_frame_calls = [
            call(self.loc.format(1, 1) + '┌──────────────────────┐', end=''),
            call(self.loc.format(2, 1) + '│                      │', end=''),
            call(self.loc.format(3, 1) + '│                      │', end=''),
            call(self.loc.format(4, 1) + '│                      │', end=''),
            call(self.loc.format(5, 1) + '│                      │', end=''),
            call(self.loc.format(6, 1) + '│                      │', end=''),
            call(self.loc.format(7, 1) + '│                      │', end=''),
            call(self.loc.format(8, 1) + '└──────────────────────┘', end=''),
        ]
        self.print_commands_calls_first = [
            call(
                self.loc.format(self.height, 2) + '┤Flow├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 8) + '┤Jump├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 14) + '┤Next├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 20) + '┤eXit├',
                end='',
                flush=True
            ),
        ]
        self.print_commands_calls_middle = [
            call(
                self.loc.format(self.height, 2) + '┤Back├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 8) + '┤Flow├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 14) + '┤Jump├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 20) + '┤Next├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 26) + '┤eXit├',
                end='',
                flush=True
            ),
        ]
        self.print_commands_calls_last = [
            call(
                self.loc.format(self.height, 2) + '┤Back├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 8) + '┤Flow├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 14) + '┤Jump├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(self.height, 20) + '┤eXit├',
                end='',
                flush=True
            ),
        ]


# Test classes.
class MainTestCase(TerminalTestCase):
    def setUp(self):
        super().setUp()
        self.filename = 'tests/data/spam.txt'
        self.filename_not_exist = 'tests/data/__spam.txt'
        self.filename_is_dir = 'tests/'
        self.title = self.filename.split('/')[-1]
        with open(self.filename) as handle:
            self.text = handle.read()
        self.page_num = 1
        self.count_pages = 39

        self.print_status_calls_1 = [
            call(self.loc.format(1, 2) + f'┤{self.title}├'),
            call(
                self.loc.format(1, 18)
                + f'┤{self.page_num}/{self.count_pages}├'
            ),
        ]
        self.print_status_calls_2 = [
            call(self.loc.format(1, 2) + f'┤{self.title}├'),
            call(self.loc.format(1, 18) + f'┤2/{self.count_pages}├'),
        ]
        self.print_status_calls_3 = [
            call(self.loc.format(1, 2) + f'┤{self.title}├'),
            call(self.loc.format(1, 18) + f'┤3/{self.count_pages}├'),
        ]
        self.print_status_calls_39 = [
            call(self.loc.format(1, 2) + f'┤{self.title}├'),
            call(self.loc.format(1, 17) + f'┤39/{self.count_pages}├'),
        ]
        self.print_status_calls_1_no_wrap = [
            call(self.loc.format(1, 2) + f'┤{self.title}├'),
            call(self.loc.format(1, 18) + f'┤1/12├'),
        ]
        self.print_clear_calls = [
            call(self.loc.format(3, 3) + ' ' * (self.width - 4)),
            call(self.loc.format(4, 3) + ' ' * (self.width - 4)),
            call(self.loc.format(5, 3) + ' ' * (self.width - 4)),
            call(self.loc.format(6, 3) + ' ' * (self.width - 4)),
        ]
        self.print_page_calls_1 = [
            call(self.loc.format(3, 3) + 'Good evening.'),
            call(self.loc.format(4, 3) + ''),
            call(self.loc.format(5, 3) + 'The last scene was'),
            call(self.loc.format(6, 3) + 'interesting from the'),
        ]
        self.print_page_calls_2 = [
            call(self.loc.format(3, 3) + 'point of view of a'),
            call(self.loc.format(4, 3) + 'professional'),
            call(self.loc.format(5, 3) + 'logician because it'),
            call(self.loc.format(6, 3) + 'contained a number'),
        ]
        self.print_page_calls_3 = [
            call(self.loc.format(3, 3) + 'of logical'),
            call(self.loc.format(4, 3) + 'fallacies; that is,'),
            call(self.loc.format(5, 3) + 'invalid'),
            call(self.loc.format(6, 3) + 'propositional'),
        ]
        self.print_page_calls_39 = [
            call(self.loc.format(3, 3) + 'Goodnight.'),
        ]
        self.print_page_calls_1_no_wrap = [
            call(self.loc.format(3, 3) + 'Good evening.'),
            call(self.loc.format(4, 3) + ''),
            call(self.loc.format(5, 3) + 'The last scene was i'),
            call(self.loc.format(6, 3) + 'logician because it'),
        ]
        self.print_calls_1 = [
            *self.print_frame_calls,
            *self.print_status_calls_1,
            *self.print_commands_calls_first,
            *self.print_clear_calls,
            *self.print_page_calls_1,
        ]
        self.print_calls_2 = [
            *self.print_frame_calls,
            *self.print_status_calls_2,
            *self.print_commands_calls_middle,
            *self.print_clear_calls,
            *self.print_page_calls_2,
        ]
        self.print_calls_3 = [
            *self.print_frame_calls,
            *self.print_status_calls_3,
            *self.print_commands_calls_middle,
            *self.print_clear_calls,
            *self.print_page_calls_3,
        ]
        self.print_calls_39 = [
            *self.print_frame_calls,
            *self.print_status_calls_39,
            *self.print_commands_calls_last,
            *self.print_clear_calls,
            *self.print_page_calls_39,
        ]
        self.print_calls_1_no_wrap = [
            *self.print_frame_calls,
            *self.print_status_calls_1_no_wrap,
            *self.print_commands_calls_first,
            *self.print_clear_calls,
            *self.print_page_calls_1_no_wrap,
        ]

    @patch('blessed.Terminal.inkey')
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def main_test(
        self,
        exp,
        user_input,
        main_kwargs,
        mock_print,
        mock_height,
        mock_width,
        mock_inkey
    ):
        # Expected value.
        exp = exp

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        mock_inkey.side_effect = user_input
        filename = self.filename

        # Run test and gather actuals.
        loop = clireader.view_file(filename, **main_kwargs)
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    # Initialization tests.
    def test_open_document(self):
        """When called with a file name, open that file and display the
        first page.
        """
        exp = self.print_calls_1
        user_input = [
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_open_document_with_wrap_mode(self):
        """When called with a file name and a wrap_mode, open that
        file, paginate it with the given wrap modem and display the
        first page.
        """
        exp = self.print_calls_1_no_wrap
        user_input = [
            Keystroke('x'),
        ]
        main_kwargs = {
            'wrap_mode': 'no_wrap',
        }
        self.main_test(exp, user_input, main_kwargs)

    # Basic command tests.
    def test_back_page(self):
        """When called, retreat to the previous page of the document."""
        exp = [
            *self.print_calls_1,
            *self.print_calls_2,
            *self.print_calls_1,
        ]
        user_input = [
            Keystroke('n'),
            Keystroke('b'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_flow(self):
        """When called, prompt for a wrap mode. Then reflow the text
        using the new wrap mode.
        """
        exp = [
            *self.print_calls_1,
            *self.print_frame_calls,
            *self.print_status_calls_1,
            call(
                self.loc.format(8, 2) + '┤None├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 8) + '┤Detect├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 16) + '┤Man├',
                end='',
                flush=True
            ),
            *self.print_clear_calls,
            *self.print_page_calls_1,
            *self.print_calls_1_no_wrap,
        ]
        user_input = [
            Keystroke('f'),
            Keystroke('n'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_jump_to_page(self):
        """When called with a file name, retreat to the previous page of
        the document.
        """
        exp = [
            *self.print_calls_1,
            self.print_frame_calls[-1],
            call(
                self.loc.format(8, 3)
                + '┤Jump to page > '
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 19)
                + '3'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            *self.print_calls_3,
        ]
        user_input = [
            Keystroke('j'),
            Keystroke('3'),
            Keystroke('\n'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_next_page(self):
        """When called, advance to the next page of the document."""
        exp = [
            *self.print_calls_1,
            *self.print_calls_2,
        ]
        user_input = [
            Keystroke('n'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    # Detail tests.
    def test_last_page_should_not_have_a_next_option(self):
        """When drawn, the last page of the document should not show
        the next command.
        """
        exp = [
            *self.print_calls_1,
            self.print_frame_calls[-1],
            call(
                self.loc.format(8, 3)
                + '┤Jump to page > '
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 19)
                + '3'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 20)
                + '9'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            *self.print_calls_39,
        ]
        user_input = [
            Keystroke('j'),
            Keystroke('3'),
            Keystroke('9'),
            Keystroke('\n'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_next_on_last_page_does_nothing(self):
        """Hitting 'n' on the last page should not do anything."""
        exp = [
            *self.print_calls_1,
            self.print_frame_calls[-1],
            call(
                self.loc.format(8, 3)
                + '┤Jump to page > '
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 19)
                + '3'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 20)
                + '9'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            *self.print_calls_39,
        ]
        user_input = [
            Keystroke('j'),
            Keystroke('3'),
            Keystroke('9'),
            Keystroke('\n'),
            Keystroke('n'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_back_on_first_page_does_nothing(self):
        """Hitting 'b' on the first page should not do anything."""
        exp = [
            *self.print_calls_1,
        ]
        user_input = [
            Keystroke('b'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {})

    def test_error_if_path_does_not_exist(self):
        """If the path given doesn't exist, raise a FileDoesNotExist
        exception.
        """
        # Expected value.
        exp_ex = FileNotFoundError
        exp_msg = f'File {self.filename_not_exist} does not exist.'

        # Run test and determine result.
        with self.assertRaisesRegex(exp_ex, exp_msg):
            clireader.load_document(
                self.filename_not_exist,
                self.height,
                self.width
            )

    def test_error_if_path_is_directory(self):
        """If the path given is a directory, raise a IsADirectoryError
        exception.
        """
        # Expected value.
        exp_ex = IsADirectoryError
        exp_msg = f'{self.filename_is_dir} is a directory.'

        # Run test and determine result.
        with self.assertRaisesRegex(exp_ex, exp_msg):
            clireader.load_document(
                self.filename_is_dir,
                self.height,
                self.width
            )

    def test_load_manhelp(self):
        """If the manhelp parameter is True, load the manhelp file
        into the viewer.
        """
        exp = [
            *self.print_frame_calls,
            call(self.loc.format(1, 2) + f'┤manlike_formatting.man├'),
            call(self.loc.format(1, 17) + f'┤1/145├'),
            *self.print_commands_calls_first,
            *self.print_clear_calls,
            call('\x1b[3;3HMANLIKE_FORMATTINGMANLIKE_FORMATTING'),
            call('\x1b[4;3H'),
            call('\x1b[5;3H'),
            call('\x1b[6;3H'),
        ]
        user_input = [
            Keystroke('x'),
        ]
        self.main_test(exp, user_input, {'manhelp': True,})

    # view_text tests.
    @patch('blessed.Terminal.inkey')
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_view_text(
        self,
        mock_print,
        mock_height,
        mock_width,
        mock_inkey
    ):
        """Given a document text, a title for the document, and a text-
        wrapping mode, view_text() should display the document in a
        viewer.
        """
        # Expected value.
        exp = self.print_calls_1

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        mock_inkey.side_effect = (Keystroke('x'),)
        with open('tests/data/spam.txt') as fh:
            text = fh.read()
        title = 'spam.txt'
        wrap_mode = 'detect'

        # Run test and gather actuals.
        loop = clireader.view_text(text, title, wrap_mode)
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)


class PagerTestCase(ut.TestCase):
    def setUp(self):
        self.attrs = {
            'height': 20,
            'pages': (),
            'page_count': 0,
            'text': '',
            'title': '',
            'wrap_mode': 'detect',
            'width': 76,
        }

    # Initialization tests.
    def test_init_defaults(self):
        """When passed no values at initialization, the Pager object
        should have the default attribute values.
        """
        # Expected value.
        exp = self.attrs

        # Run test and gather actuals.
        pager = clireader.Pager()
        act = {key: getattr(pager, key) for key in exp}

        # Determine test results.
        self.assertDictEqual(exp, act)

    def test_init_set_attrs(self):
        """When passed allowed parameters, the Pager object should
        set those parameters as attributes.
        """
        # Expected value.
        exp = self.attrs
        exp['height'] = 10
        exp['pages'] = (('spam',),)
        exp['page_count'] = 1
        exp['text'] = 'spam'
        exp['title'] = 'eggs'
        exp['width'] = 15

        # Run test and gather actuals.
        pager = clireader.Pager(
            text=exp['text'],
            title=exp['title'],
            height=exp['height'],
            width=exp['width'],
        )
        act = {key: getattr(pager, key) for key in exp}

        # Determine test results.
        self.assertDictEqual(exp, act)

    # Pagination tests.
    def test_page_count(self):
        """When called, Pager.page_count should return the number of
        pages in the text at the current height and width.
        """
        # Expected value.
        exp = 3

        # Test data and state.
        text = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
            ),
            (
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )
        height = len(text[0])
        width = len(text[0][0]) + 1
        lines = []
        for page in text:
            lines.extend(page)
        text = ' '.join(lines)
        pager = clireader.Pager(text, height=height, width=width)

        # Run test.
        act = pager.page_count

        # Determine test result.
        self.assertEqual(exp, act)

    def test_detect_pagination(self):
        """When called, Pager.pages should return the text paginated
        to the defined height and width for the object.
        """
        # Expected value.
        exp = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
            ),
            (
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        lines = []
        for page in exp:
            lines.extend(page)
        text = ' '.join(lines)
        pager = clireader.Pager(text, height=height, width=width)

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_detect_pagination_with_bullets(self):
        """When given text with lines that start with an asterisk
        followed by whitespace, those lines should not be wrapped
        as though they are a bulleted list.
        """
        # Expected value.
        exp = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '',
                '* 1234 6789',
                '* 6789 1234',
            ),
            (
                '\t* 1234 6789',
                '',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        text = (
            '1234 6789 1234 '
            '6789 1234 6789\n\n'
            '* 1234 6789\n'
            '* 6789 1234\n'
            '\t* 1234 6789\n\n'
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789'
        )
        pager = clireader.Pager(text, height=height, width=width)

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_detect_pagination_with_newlines(self):
        """When given text that contains single newline characters,
        the newlines should be replaced with a space before the text
        is wrapped.
        """
        # Expected value.
        exp = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
            ),
            (
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        text = (
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789'
        )
        pager = clireader.Pager(text, height=height, width=width)

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_detect_pagination_with_doubled_newlines(self):
        """When given text that contains single newline characters,
        the newlines should be replaced with a space before the text
        is wrapped.
        """
        # Expected value.
        exp = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        text = (
            '1234 6789 1234\n'
            '6789 1234 6789\n\n'
            '1234 6789 1234\n'
            '6789 1234 6789\n\n'
            '1234 6789 1234\n'
            '6789 1234 6789\n\n'
            '1234 6789 1234\n'
            '6789 1234 6789\n\n'
            '1234 6789 1234\n'
            '6789 1234 6789\n\n'
            '1234 6789 1234\n'
            '6789 1234 6789\n\n'
        )
        pager = clireader.Pager(text, height=height, width=width)

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_long_pagination(self):
        """When called with the wrap mode set to long, Pager.pages
        should return the text paginated to the defined height and
        width for the object, with only the long lines wrapped.
        """
        # Expected value.
        exp = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
            ),
            (
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        wrap_mode = 'long'
        text = (
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789\n'
            '1234 6789 1234\n'
            '6789 1234 6789'
        )
        pager = clireader.Pager(text, height=height, width=width)

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_man_pagination(self):
        """When called with mode set to 'man', Pager.pages should
        return the text formatted and paginated using the manlike
        macros.
        """
        # Expected value.
        exp = (
            (
                'SPAM                SPAM',
                '',
                '',
            ),
            (
                '    eggs',
                '',
                '',
            ),
            (
                '                    SPAM',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = 24
        wrap_mode = 'man'
        text = (
            '.TH SPAM\n'
            '.P\n'
            'eggs\n'
        )
        pager = clireader.Pager(
            text,
            height=height,
            width=width,
            wrap_mode=wrap_mode
        )

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_no_wrap_pagination_with_long_line(self):
        """When called with mode set to 'no_wrap', Pager.pages should
        return the text paginated with any long lines truncated to the
        width of the viewing area.
        """
        # Expected value.
        exp = (
            (
                '1234 6789 1234',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        wrap_mode = 'no_wrap'
        text = (
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789\n'
            '1234 6789 1234\n'
            '6789 1234 6789'
        )
        pager = clireader.Pager(
            text,
            height=height,
            width=width,
            wrap_mode=wrap_mode
        )

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_no_wrap_pagination_with_newlines(self):
        """When given text that contains single newline characters,
        the newlines the lines should  not be reflowed.
        """
        # Expected value.
        exp = (
            (
                '1234 6789',
                '1234',
                '6789 1234',
                '6789',
                '1234 6789',
            ),
            (
                '1234',
                '6789 1234',
                '6789',
                '1234 6789',
                '1234',
            ),
            (
                '6789 1234',
                '6789',
                '1234 6789',
                '1234',
                '6789 1234',
            ),
            (
                '6789',
                '1234 6789',
                '1234',
                '6789 1234',
                '6789',
            ),
            (
                '1234 6789',
                '1234',
                '6789 1234',
                '6789',
            ),
        )

        # Test data and state.
        height = len(exp[0])
        width = len(exp[0][0]) + 1
        wrap_mode = 'no_wrap'
        text = (
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789\n'
            '1234 6789\n1234\n'
            '6789 1234\n6789'
        )
        pager = clireader.Pager(
            text,
            height=height,
            width=width,
            wrap_mode=wrap_mode
        )

        # Run test.
        act = pager.pages

        # Determine test result.
        self.assertTupleEqual(exp, act)

    # Text reflow tests.
    def test_reflow_text(self):
        """Given a wrap_mode, Pager.reflow should reflow the text
        with the new attributes.
        """
        # Expected value.
        exp_before = (
            (
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
            ),
            (
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
            (
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )
        exp_after = (
            (
                '1234 6789 1234',
                '1234 6789 1234',
                '6789 1234 6789',
            ),
        )
        exp_wrap_mode = 'no_wrap'

        # Test data and state.
        height = len(exp_before[0])
        width = len(exp_before[0][0]) + 1
        wrap_mode_before = 'detect'
        text = (
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789\n'
            '1234 6789 1234\n'
            '6789 1234 6789'
        )
        pager = clireader.Pager(
            text,
            height=height,
            width=width,
            wrap_mode=wrap_mode_before
        )

        # Run test and gather actuals.
        act_before = pager.pages[:]
        pager.reflow(exp_wrap_mode)
        act_after = pager.pages[:]
        act_wrap_mode = pager.wrap_mode

        # Determine test result.
        self.assertTupleEqual(exp_before, act_before)
        self.assertTupleEqual(exp_after, act_after)
        self.assertEqual(exp_wrap_mode, act_wrap_mode)


class ViewerTestCase(TerminalTestCase):
    def setUp(self):
        super().setUp()

        # Common test data.
        self.page_count = 10
        self.frame_type = 'light'
        self.page_num = 1
        self.text = (
            'Eggs.',
        )
        self.term = Terminal()
        self.title = 'spam'

        # Common expected values.
        self.clear = [
            call(self.loc.format(3, 3) + ' ' * (self.width - 4)),
            call(self.loc.format(4, 3) + ' ' * (self.width - 4)),
            call(self.loc.format(5, 3) + ' ' * (self.width - 4)),
            call(self.loc.format(6, 3) + ' ' * (self.width - 4)),
        ]
        self.frame = self.print_frame_calls
        self.page = [
            call(self.loc.format(3, 3) + self.text[0]),
        ]
        self.status = [
            call(self.loc.format(1, 2) + '┤spam├'),
            call(
                self.loc.format(1, 18)
                + f'┤{self.page_num}/{self.page_count}├'
            ),
        ]

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def drawing_test(
        self,
        exp,
        method,
        kwargs,
        mock_print,
        mock_height,
        mock_width
    ):
        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width

        # Run test and gather actuals.
        method(**kwargs)
        act = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

    # Basic drawing tests.
    def test_clear(self):
        """When called, Viewer.clear should clear the page area of the
        terminal.
        """
        exp = self.clear
        viewer = clireader.Viewer()
        method = viewer.clear
        kwargs = {}
        self.drawing_test(exp, method, kwargs)

    def test_draw_commands(self):
        """When called, Viewer.draw_command should draw the command
        hints on the bottom of the frame.
        """
        exp = self.print_commands_calls_first
        viewer = clireader.Viewer()
        method = viewer.draw_commands
        kwargs = {
            'commands': self.command_list,
        }
        self.drawing_test(exp, method, kwargs)

    def test_draw_frame(self):
        """When called, Viewer.draw_frame should draw the frame
        around the page.
        """
        exp = self.frame
        viewer = clireader.Viewer()
        method = viewer.draw_frame
        kwargs = {}
        self.drawing_test(exp, method, kwargs)

    def test_draw_page(self):
        """When called, Viewer.draw_page should draw the page within the
        frame in the terminal.
        """
        exp = self.page
        viewer = clireader.Viewer()
        method = viewer.draw_page
        kwargs = {
            'text': self.text,
        }
        self.drawing_test(exp, method, kwargs)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_prompt(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called with a string, Viewer.draw_prompt should draw
        the string as a prompt at the bottom of the terminal window.
        It should then return the location of the cursor for text entry.
        """
        # Expected value.
        exp_print_calls = [
            self.frame[-1],
            call(
                self.loc.format(8, 3)
                + '┤spam > '
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
        ]
        exp_loc = (7, 10)

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        prompt = 'spam'
        viewer = clireader.Viewer()

        # Run test and gather actuals.
        act_loc = viewer.draw_prompt(prompt)
        act_print_calls = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp_print_calls, act_print_calls)
        self.assertTupleEqual(exp_loc, act_loc)

    def test_draw_status(self):
        """When called, Viewer.draw_status should draw the status on
        the top frame of the page.
        """
        exp = self.status
        viewer = clireader.Viewer()
        method = viewer.draw_status
        kwargs = {
            'page_num': self.page_num,
            'page_count': self.page_count,
            'title': self.title,
        }
        self.drawing_test(exp, method, kwargs)

    # Basic input tests.
    @patch('blessed.Terminal.inkey')
    def test_get_key(self, mock_inkey):
        """When called, Viewer.get_key should wait for a key press
        from the user then return the character of the pressed key.
        """
        # Expected value.
        exp = 'x'

        # Test data and state.
        mock_inkey.return_value = Keystroke(exp)
        viewer = clireader.Viewer()

        # Run test and gather actual.
        act = viewer.get_key()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('blessed.Terminal.inkey')
    def test_get_str(self, mock_inkey):
        """When called, Viewer.get_str should wait for a sequence of
        key presses from the user, ending with a newline. The method
        should then return the key presses as a string.
        """
        # Expected value.
        exp = 'spam'

        # Test data and state.
        keys = [Keystroke(char) for char in exp]
        mock_inkey.side_effect = [*keys, Keystroke('\n')]
        viewer = clireader.Viewer()

        # Run test and gather actual.
        act = viewer.get_str()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    @patch('blessed.Terminal.inkey')
    def test_get_str_with_prompt(
        self,
        mock_inkey,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Viewer.get_str should wait for a sequence of
        key presses from the user, ending with a newline. The method
        should then return the key presses as a string.
        """
        # Expected value.
        exp = 'spam'
        exp_print_calls = [
            self.frame[-1],
            call(
                self.loc.format(8, 3)
                + '┤spam > '
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 11)
                + 's'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 12)
                + 'p'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 13)
                + 'a'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
            call(
                self.loc.format(8, 14)
                + 'm'
                + self.rev
                + ' '
                + self.nml
                + '├',
                end='',
                flush=True
            ),
        ]

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        keys = [Keystroke(char) for char in exp]
        mock_inkey.side_effect = [*keys, Keystroke('\n')]
        viewer = clireader.Viewer()

        # Run test and gather actual.
        act = viewer.get_str('spam')
        act_print_calls = mock_print.mock_calls

        # Determine test result.
        self.assertEqual(exp, act)
        self.assertListEqual(exp_print_calls, act_print_calls)
