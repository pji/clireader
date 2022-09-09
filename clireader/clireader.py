"""
clireader
~~~~~~~~~

A module for paging through text in the terminal.
"""
from re import sub
from textwrap import wrap
from time import sleep
from typing import Generator, NamedTuple, Optional, Sequence

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


class Command(NamedTuple):
    key: str
    name: str


# Text manager class.
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

    def _remove_hard_wrapping(self, text: str) -> str:
        """Remove any hard wrapping from a given string. Single
        newlines are considered hard wrapping. Doubled newlines are
        considered paragraph breaks.
        """
        # We only need to do work if there are newlines in the text.
        if '\n' not in text:
            return text

        # Remove the single newlines.
        pattern = r'\n(?!\n)'
        nosingles = sub(pattern, ' ', text)

        # Turn doubled newlines into single newlines.
        pattern = r'\n '
        return sub(pattern, '\n', nosingles)

    def _pagenate(self) -> tuple[tuple[str, ...], ...]:
        """Paginate the text."""
        unwrapped = self._remove_hard_wrapping(self.text)
        paragraphed = unwrapped.split('\n')
        pwrapped = [wrap(p, self.width) for p in paragraphed]
        wrapped = []
        for paragraph in pwrapped:
            wrapped.extend(paragraph)
            wrapped.append('')

        pages = []
        page: list[str] = []
        count = 0
        for line in wrapped:
            if count == self.height:
                pages.append(tuple(page))
                page = []
                count = 0
            if count == 0 and not line:
                continue
            page.append(line)
            count += 1
        else:
            if page:
                try:
                    if not page[-1]:
                        page = page[:-1]
                except IndexError:
                    pass
                pages.append(tuple(page))

        return tuple(pages)


# Terminal controller class.
class Viewer:
    """Manage the terminal."""
    def __init__(self, term: Terminal = Terminal()) -> None:
        self.term = term

    # Screen output methods.
    def clear(self) -> None:
        """Clear the text area."""
        line = ' ' * (self.term.width - 4)
        for y in range(2, self.term.height - 1):
            print(self.term.move(y, 2) + line)

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

    def draw_commands(
        self,
        commands: Sequence[Command],
        frame_type: str = 'light'
    ) -> None:
        """Draw the command hints."""
        for i, command in enumerate(commands):
            # Create the command hint.
            frame = Box(frame_type)
            cmd_char_index = command.name.index(command.key)
            hint = (
                frame.rside
                + command.name[0:cmd_char_index]
                + command.name[cmd_char_index: cmd_char_index + 1].upper()
                + command.name[cmd_char_index + 1:]
                + frame.lside
            )

            # Print the command.
            x = i * len(hint) + 1
            y = self.term.height
            print(self.term.move(y, x) + hint)

    def draw_page(self, text: Sequence[str]) -> None:
        """Draw the text for the page."""
        for i, line in enumerate(text):
            y = i + 2
            print(self.term.move(y, 2) + line)

    def draw_status(
        self,
        title: str = '',
        page_num: int = 0,
        count_pages: int = 0,
        frame_type: str = 'light'
    ) -> None:
        """Draw the status on top of the page."""
        frame = Box(frame_type)
        field_tmp = frame.rside + '{}' + frame.lside
        if title:
            print(self.term.move(0, 1) + field_tmp.format(title))
        if page_num:
            field = field_tmp.format(f'{page_num}/{count_pages}')
            x = self.term.width - len(field) - 1
            print(self.term.move(0, x) + field)

    # User input methods.
    def get_key(self) -> str:
        """Return the character for the next key pressed."""
        with self.term.cbreak():
            key = self.term.inkey()
        return str(key)
