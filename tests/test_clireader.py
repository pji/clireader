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
    rev = '\x1b[7m'
    loc = '\x1b[{};{}H'

    def setUp(self):
        self.height = 8
        self.width = 24


# Test classes.
class MainTestCase(TerminalTestCase):
    def setUp(self):
        super().setUp()
        self.filename = 'tests/data/spam.txt'
        self.title = self.filename.split('/')[-1]
        with open(self.filename) as handle:
            self.text = handle.read()
        self.page_num = 1
        self.count_pages = 39
        self.command_list = (
            clireader.Command('j', 'jump'),
            clireader.Command('n', 'next'),
            clireader.Command('x', 'exit'),
        )

        self.print_frame_calls = [
            call(self.loc.format(1, 1) + '┌──────────────────────┐'),
            call(self.loc.format(2, 1) + '│                      │'),
            call(self.loc.format(3, 1) + '│                      │'),
            call(self.loc.format(4, 1) + '│                      │'),
            call(self.loc.format(5, 1) + '│                      │'),
            call(self.loc.format(6, 1) + '│                      │'),
            call(self.loc.format(7, 1) + '│                      │'),
            call(self.loc.format(8, 1) + '│                      │'),
            call(self.loc.format(9, 1) + '└──────────────────────┘'),
        ]
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
        self.print_commands_calls_first = [
            call(self.loc.format(self.height + 1, 2) + '┤Jump├'),
            call(self.loc.format(self.height + 1, 8) + '┤Next├'),
            call(self.loc.format(self.height + 1, 14) + '┤eXit├'),
        ]
        self.print_commands_calls_middle = [
            call(self.loc.format(self.height + 1, 2) + '┤Back├'),
            call(self.loc.format(self.height + 1, 8) + '┤Jump├'),
            call(self.loc.format(self.height + 1, 14) + '┤Next├'),
            call(self.loc.format(self.height + 1, 20) + '┤eXit├'),
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

    @patch('blessed.Terminal.inkey')
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def main_test(
        self,
        exp,
        user_input,
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
        loop = clireader.main(filename)
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    # Tests.
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
        self.main_test(exp, user_input)

    def test_jump_to_page(self):
        """When called with a file name, retreat to the previous page of
        the document.
        """
        exp = [
            *self.print_calls_1,
            self.print_frame_calls[-1],
            call(
                self.loc.format(9, 3)
                + '┤Jump to page > '
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
            call(
                self.loc.format(9, 19)
                + '3'
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
            *self.print_calls_3,
        ]
        user_input = [
            Keystroke('j'),
            Keystroke('3'),
            Keystroke('\n'),
            Keystroke('x'),
        ]
        self.main_test(exp, user_input)

    def test_open_document(self):
        """When called with a file name, open that file and display the
        first page.
        """
        exp = self.print_calls_1
        user_input = [
            Keystroke('x'),
        ]
        self.main_test(exp, user_input)

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
        self.main_test(exp, user_input)


class PagerTestCase(ut.TestCase):
    def setUp(self):
        self.attrs = {
            'height': 20,
            'pages': (),
            'page_count': 0,
            'text': '',
            'title': '',
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

    def test_pagination(self):
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

    def test_pagination_with_newlines(self):
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
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
            '6789 1234 6789 '
            '1234 6789 1234 '
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

    def test_pagination_with_doubled_newlines(self):
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


class ViewerTestCase(TerminalTestCase):
    def setUp(self):
        super().setUp()

        # Common test data.
        self.command_list = (
            clireader.Command('b', 'back'),
            clireader.Command('n', 'next'),
            clireader.Command('x', 'exit'),
        )
        self.count_pages = 10
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
        self.commands = [
            call(self.loc.format(self.height + 1, 2) + '┤Back├'),
            call(self.loc.format(self.height + 1, 8) + '┤Next├'),
            call(self.loc.format(self.height + 1, 14) + '┤eXit├'),
        ]
        self.frame = [
            call(self.loc.format(1, 1) + '┌──────────────────────┐'),
            call(self.loc.format(2, 1) + '│                      │'),
            call(self.loc.format(3, 1) + '│                      │'),
            call(self.loc.format(4, 1) + '│                      │'),
            call(self.loc.format(5, 1) + '│                      │'),
            call(self.loc.format(6, 1) + '│                      │'),
            call(self.loc.format(7, 1) + '│                      │'),
            call(self.loc.format(8, 1) + '│                      │'),
            call(self.loc.format(9, 1) + '└──────────────────────┘'),
        ]
        self.page = [
            call(self.loc.format(3, 3) + self.text[0]),
        ]
        self.status = [
            call(self.loc.format(1, 2) + '┤spam├'),
            call(
                self.loc.format(1, 18)
                + f'┤{self.page_num}/{self.count_pages}├'
            ),
        ]

    # Basic drawing tests.
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_clear(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Viewer.clear should clear the page area of the
        terminal.
        """
        # Expected value.
        exp = self.clear

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        viewer = clireader.Viewer()

        # Run test and gather actuals.
        viewer.clear()
        act = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_command(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Viewer.draw_command should draw the command
        hints on the bottom of the frame.
        """
        # Expected value.
        exp = self.commands

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        viewer = clireader.Viewer()

        # Run test and gather actuals.
        viewer.draw_commands(self.command_list)
        act = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_frame(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Viewer.draw_frame should draw the frame
        around the page.
        """
        # Expected value.
        exp = self.frame

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        viewer = clireader.Viewer()

        # Run test and gather actuals.
        viewer.draw_frame()
        act = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_page(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Viewer.draw_page should draw the page within the
        frame in the terminal.
        """
        # Expected value.
        exp = self.page

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        text = self.text
        viewer = clireader.Viewer()

        # Run test and gather actuals.
        viewer.draw_page(text)
        act = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

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
                self.loc.format(9, 3)
                + '┤spam > '
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
        ]
        exp_loc = (8, 10)

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

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_status(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Viewer.draw_status should draw the status on
        the top frame of the page.
        """
        # Expected value.
        exp = self.status

        # Test data and state.
        mock_height.return_value = self.height
        mock_width.return_value = self.width
        page_num = self.page_num
        count_pages = self.count_pages
        title = self.title
        viewer = clireader.Viewer()

        # Run test and gather actuals.
        viewer.draw_status(
            title=title,
            page_num=page_num,
            count_pages=count_pages,
        )
        act = mock_print.mock_calls

        # Determine test results.
        self.assertListEqual(exp, act)

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
                self.loc.format(9, 3)
                + '┤spam > '
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
            call(
                self.loc.format(9, 11)
                + 's'
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
            call(
                self.loc.format(9, 12)
                + 'p'
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
            call(
                self.loc.format(9, 13)
                + 'a'
                + self.rev
                + ' '
                + self.rev
                + '├'
            ),
            call(
                self.loc.format(9, 14)
                + 'm'
                + self.rev
                + ' '
                + self.rev
                + '├'
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
