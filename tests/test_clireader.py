"""
test_clireader
~~~~~~~~~~~~~~

Unit tests for the clireader.clireader module.
"""
import unittest as ut
from unittest.mock import call, Mock, patch, PropertyMock

from blessed import Terminal

from clireader import clireader


class PageTestCase(ut.TestCase):
    topleft = '\x1b[1;2H'
    bold = '\x1b[1m'
    rev = '\x1b[7m'
    loc = '\x1b[{};{}H'

    """A UI for paging through text."""
    def setUp(self):
        self.term = Terminal()
        self.term_h = 8
        self.term_w = 14
        self.text_long = 'This is longer text.'
        self.text_overflow = (
            'This text should over flow the very small box used for '
            'testing. That is good. We want to use it to test how '
            'the box handles over-flowing text.'
        )
        self.text_short = 'Eggs.'
        self.title = 'spam'

        # Common expected values.
        self.draw_frame = [
            call(self.loc.format(1, 1) + '┌─spam───────┐'),
            call(self.loc.format(2, 1) + '│            │'),
            call(self.loc.format(3, 1) + '│            │'),
            call(self.loc.format(4, 1) + '│            │'),
            call(self.loc.format(5, 1) + '│            │'),
            call(self.loc.format(6, 1) + '│            │'),
            call(self.loc.format(7, 1) + '│            │'),
            call(self.loc.format(8, 1) + '│            │'),
            call(self.loc.format(9, 1) + '└────────────┘'),
        ]
        self.draw_long = [
            *self.draw_frame,
            call(self.loc.format(3, 3) + 'This is'),
            call(self.loc.format(4, 3) + 'longer'),
            call(self.loc.format(5, 3) + 'text.'),
        ]
        self.draw_overflow = [
            *self.draw_frame,
            call(self.loc.format(9, 7) + self.rev + '>' + self.rev + 'Next'),
            call(self.loc.format(3, 3) + 'This text'),
            call(self.loc.format(4, 3) + 'should over'),
            call(self.loc.format(5, 3) + 'flow the'),
            call(self.loc.format(6, 3) + 'very small'),
            call(self.loc.format(7, 3) + 'box used'),
        ]
        self.draw_overflow_pg2 = [
            *self.draw_frame,
            call(self.loc.format(9, 7) + self.rev + '>' + self.rev + 'Next'),
            call(self.loc.format(9, 1) + self.rev + '<' + self.rev + 'Back'),
            call(self.loc.format(3, 3) + 'for'),
            call(self.loc.format(4, 3) + 'testing.'),
            call(self.loc.format(5, 3) + 'That is'),
            call(self.loc.format(6, 3) + 'good. We'),
            call(self.loc.format(7, 3) + 'want to use'),
        ]
        self.draw_short = [
            *self.draw_frame,
            call(self.loc.format(3, 3) + self.text_short),
        ]

    # Test Page.__init__().
    def test_init(self):
        """When called, a Page() object is properly initialized and
        returned.
        """
        exp_class = clireader.Page
        exp_text = ''
        act_obj = clireader.Page()
        act_text = act_obj.text
        self.assertIsInstance(act_obj, exp_class)
        self.assertEqual(exp_text, act_text)

    def test_text(self):
        """When called with text, a Page() object is properly initialized
        and returned.
        """
        exp_class = clireader.Page
        exp_text = 'spam'
        act_obj = clireader.Page(exp_text)
        act_text = act_obj.text
        self.assertIsInstance(act_obj, exp_class)
        self.assertEqual(exp_text, act_text)

    def test_set_frame(self):
        """When initialized with a frame parameter, the page will store
        the appropriate frame to use when drawing the page.
        """
        exp = 'heavy'
        page = clireader.Page('spam', frame=exp)
        act = page.frame.kind
        self.assertEqual(exp, act)

    def test_set_title(self):
        """When initialized with a title parameter, the page will store
        the title to use when displaying the page.
        """
        exp = 'eggs'
        page = clireader.Page('spam', title=exp)
        act = page.title
        self.assertEqual(exp, act)

    def test_set_padding(self):
        """When initialized with a padding parameter, the page will store
        the padding to use around the text when displaying the page.
        """
        exp = 2
        page = clireader.Page('spam', padding=exp)
        act = page.padding
        self.assertEqual(exp, act)

    # Test Page.back()
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_back(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Page.back() should decrement the current page
        and draw the page in the terminal.
        """
        # Expected value.
        exp = [
            call(self.loc.format(1, 1) + '┌─spam───────┐'),
            call(self.loc.format(2, 1) + '│            │'),
            call(self.loc.format(3, 1) + '│            │'),
            call(self.loc.format(4, 1) + '│            │'),
            call(self.loc.format(5, 1) + '│            │'),
            call(self.loc.format(6, 1) + '│            │'),
            call(self.loc.format(7, 1) + '│            │'),
            call(self.loc.format(8, 1) + '│            │'),
            call(self.loc.format(9, 1) + '└────────────┘'),
            call(self.loc.format(9, 7) + self.rev + '>' + self.rev + 'Next'),
            call(self.loc.format(3, 3) + 'This text'),
            call(self.loc.format(4, 3) + 'should over'),
            call(self.loc.format(5, 3) + 'flow the'),
            call(self.loc.format(6, 3) + 'very small'),
            call(self.loc.format(7, 3) + 'box used'),
        ]

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_overflow,
            title=self.title,
            frame='light'
        )
        page.current_page = 1

        # Run test and gather actuals.
        page.back()
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    # Test Page.draw()
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw(self, mock_print, mock_height, mock_width):
        """When called, Page.draw() should draw the page in the terminal.
        """
        # Expected value.
        exp = self.draw_short

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_short,
            title=self.title,
            frame='light'
        )

        # Run test and gather actuals.
        page.draw()
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_text_wrap(self, mock_print, mock_height, mock_width):
        """When called, Page.draw() should draw the page in the terminal.
        """
        # Expected value.
        exp = self.draw_long

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_long,
            title=self.title,
            frame='light'
        )

        # Run test and gather actuals.
        page.draw()
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_text_overflow(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Page.draw() should draw the page in the terminal.
        """
        # Expected value.
        exp = self.draw_overflow

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_overflow,
            title=self.title,
            frame='light'
        )

        # Run test and gather actuals.
        page.draw()
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_draw_text_overflow_page_2(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Page.draw() should draw the page in the terminal.
        """
        # Expected value.
        exp = self.draw_overflow_pg2

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_overflow,
            title=self.title,
            frame='light'
        )
        page.current_page = 1

        # Run test and gather actuals.
        page.draw()
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    # Test Page.inout()
    @patch('clireader.clireader.Terminal.inkey', return_value='.')
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    def test_input(self, mock_height, mock_width, mock_inkey):
        """When called, Page.input() will wait for keyboard input.
        When the input is received, it will return that input.
        """
        # Expected value.
        exp = mock_inkey()

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_overflow,
            title=self.title,
            frame='light'
        )

        # Run test.
        act = page.input()

        # Determine test result.
        self.assertEqual(exp, act)

    # Test Page.load()
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_load(self, mock_print, mock_height, mock_width):
        """When called with new text and title, Page.load() should
        update the text stored, reset the current page to zero, and
        redraw the screen.
        """
        # Expected value.
        exp = self.draw_overflow

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_short,
            title='bacon',
            frame='light'
        )
        _ = page.pages

        # Run test and gather actuals.
        page.load(text=self.text_overflow, title=self.title)
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_load_without_previous_draw(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called without the Page having drawn to the screen before,
        Page.load() should not error.
        """
        # Expected value.
        exp = self.draw_overflow

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_short,
            title='bacon',
            frame='light'
        )

        # Run test and gather actuals.
        page.load(text=self.text_overflow, title=self.title)
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)

    # Test Page.next()
    @patch('clireader.clireader.Terminal.width', new_callable=PropertyMock)
    @patch('clireader.clireader.Terminal.height', new_callable=PropertyMock)
    @patch('clireader.clireader.print')
    def test_next(
        self,
        mock_print,
        mock_height,
        mock_width
    ):
        """When called, Page.next() should increment the current page
        and draw the page in the terminal.
        """
        # Expected value.
        exp = self.draw_overflow_pg2

        # Test data and state.
        mock_height.return_value = self.term_h
        mock_width.return_value = self.term_w
        page = clireader.Page(
            self.text_overflow,
            title=self.title,
            frame='light'
        )
        page.current_page = 0

        # Run test and gather actuals.
        page.next()
        act = mock_print.mock_calls

        # Determine test result.
        self.assertListEqual(exp, act)
