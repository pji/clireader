"""
clireader
~~~~~~~~~

A module for paging through text in the terminal.
"""
from textwrap import wrap
from time import sleep
from typing import Generator, Optional

from blessed import Terminal


# Utility classes.
class Box:
    """A class to track the characters used to draw a box in a
    terminal.

    It has fifteen properties that return the character used for
    that part of the box:

    * top: The top
    * bot: The bottom
    * side: The sides
    * mhor: Interior horizontal lines
    * mver: Interior vertical lines
    * ltop: The top-left corner
    * mtop: Top mid-join
    * rtop: The top-right corner
    * lside: Left side mid-join
    * mid: Interior join
    * rside: Right side mid-join
    * lbot: Bottom-left corner
    * mbot: Bottom mid-join
    * rbot: Bottom-right corner
    """
    def __init__(self, kind: str = 'light', custom: str = None) -> None:
        self._names = [
            'top', 'bot', 'side',
            'mhor', 'mver',
            'ltop', 'mtop', 'rtop',
            'lside', 'mid', 'rside',
            'lbot', 'mbot', 'rbot',
        ]
        self._light = '──│─│┌┬┐├┼┤└┴┘'
        self._heavy = '━━┃━┃┏┳┓┣╋┫┗┻┛'
        self._light_double_dash = '╌╌╎╌╎' + self._light[3:]
        self._heavy_double_dash = '╍╍╏╍╏' + self._heavy[3:]
        self._light_triple_dash = '┄┄┆┄┆' + self._light[3:]
        self._heavy_triple_dash = '┅┅┇┅┇' + self._heavy[3:]
        self._light_quadruple_dash = '┈┈┊┈┊' + self._light[3:]
        self._heavy_quadruple_dash = '┉┉┋┉┋' + self._heavy[3:]
        if kind:
            self.kind = kind
        else:
            self.kind = 'light'
        if custom:
            self.custom = custom
            self.kind = 'custom'

    def __getattr__(self, name):
        try:
            index = self._names.index(name)
        except ValueError:
            return self.__dict__[name]
        return self._chars[index]

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value
        self._chars = getattr(self, f'_{value}')

    @property
    def custom(self):
        return self._custom

    @custom.setter
    def custom(self, value):
        strvalue = str(value)
        if len(strvalue) == 14:
            self._custom = str(strvalue)
            self._kind = 'custom'
        else:
            reason = 'The custom string must be 14 characters.'
            raise ValueError(reason)


class Pager:
    """Manage the text being displayed."""
    def __init__(
        self,
        text: str = '',
        title: str = '',
        height: int = 20,
        width: int = 76
    ) -> None:
        self.height = height
        self.width = width
        self.title = title
        self.text = text

    @property
    def pages(self) -> tuple[tuple[str, ...], ...]:
        """The paged text."""
        if '_pages' not in self.__dict__:
            self._pages = self._pagenate()
        return self._pages

    @property
    def page_count(self) -> int:
        """The number of pages in the paged text."""
        return len(self.pages)

    def _pagenate(self) -> tuple[tuple[str, ...], ...]:
        """Paginate the text."""
        wrapped = wrap(self.text, self.width)
        pages = []
        for i in range(0, len(wrapped), self.height):
            page = wrapped[i: i + self.height]
            pages.append(tuple(page))
        return tuple(pages)


class Viewer:
    """Manage the terminal."""
    def __init__(self, term: Terminal = Terminal()) -> None:
        self.term = term

    def draw_frame(self, frame_type: str = 'light') -> None:
        """Draw the frame around the page."""
        frame = Box(frame_type)
        top = (
            frame.ltop
            + frame.top * (self.term.width - 2)
            + frame.rtop
        )
        mid = (
            frame.mver
            + ' ' * (self.term.width - 2)
            + frame.mver
        )
        bot = (
            frame.lbot
            + frame.bot * (self.term.width - 2)
            + frame.rbot
        )

        print(self.term.move(0, 0) + top)
        for y in range(1, self.term.height):
            print(self.term.move(y, 0) + mid)
        print(self.term.move(self.term.height, 0) + bot)


# Terminal controller.
class Page:
    """View pages of text in a terminal."""
    def __init__(
            self,
            text: str = '',
            title: str = '',
            frame: str = 'light',
            padding: int = 1,
            term: Optional[Terminal] = None
    ) -> None:
        self.frame = Box(kind=frame)
        self.padding = padding
        self.text = text
        self.title = title
        self.current_page = 0
        if not term:
            self.term = Terminal()

    @property
    def pages(self) -> list[list[str]]:
        if '_pages' not in self.__dict__:
            width = self.term.width + 1 - 2 - self.padding * 2
            lines_per_page = self.term.height + 1 - 2 - self.padding * 2
            wrapped = wrap(self.text, width)
            self._pages = []
            for i in range(0, len(wrapped), lines_per_page):
                self._pages.append(wrapped[i: i + lines_per_page])
        return self._pages

    def _draw_command_hints(self) -> None:
        hints = []
        if len(self.pages) > 1:
            hints.append(self.term.reverse + '>' + self.term.reverse + 'Next')
        if len(self.pages) > 1 and self.current_page != 0:
            hints.append(self.term.reverse + '<' + self.term.reverse + 'Back')
        for i, hint in enumerate(hints):
            y = self.term.height
            x = self.term.width - 5 - 3 - 6 * i
            print(self.term.move(y, x) + hint)

    def _draw_frame(self) -> None:
        """Draw the frame around the page."""
        top = (
            self.frame.ltop
            + self.frame.top
            + self.title
            + self.frame.top * (self.term.width - len(self.title) - 3)
            + self.frame.rtop
        )
        mid = (
            self.frame.mver
            + (' ' * (self.term.width - 2))
            + self.frame.mver
        )
        bot = (
            self.frame.lbot
            + (self.frame.bot * (self.term.width - 2))
            + self.frame.rbot
        )

        print(self.term.move(0, 0) + top)
        for y in range(1, self.term.height):
            print(self.term.move(y, 0) + mid)
        print(self.term.move(self.term.height, 0) + bot)

    def back(self) -> None:
        """Go back to the previous page of text."""
        self.current_page -= 1
        self.draw()

    def draw(self) -> None:
        """Draw the page of text."""
        # Draw the frame.
        self._draw_frame()
        self._draw_command_hints()

        # Draw the text.
        text = self.pages[self.current_page]
        y = self.padding + 1
        x = self.padding + 1
        for line in text:
            print(self.term.move(y, x) + line)
            y += 1

    def input(self) -> str:
        """Receive key presses from the user."""
        with self.term.cbreak():
            raw = self.term.inkey()
        resp = str(raw)
        return resp

    def load(self, text: str, title: str = '') -> None:
        """Update the text pages being shown."""
        self.text = text
        self.title = title
        self.current_page = 0
        if '_pages' in self.__dict__:
            del self._pages
        self.draw()

    def next(self) -> None:
        """Advance to the next page of text."""
        self.current_page += 1
        self.draw()
