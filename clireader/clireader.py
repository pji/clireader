"""
clireader
~~~~~~~~~

A module for paging through text in the terminal.
"""
from pathlib import Path
from re import match
from textwrap import wrap
from time import sleep
from typing import Generator, NamedTuple, Optional, Sequence

from blessed import Terminal
from blessed.keyboard import Keystroke

from clireader import man


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
    """A command for interacting with the document being viewed."""
    key: str
    name: str


# Text manager class.
class Pager:
    """Manage the text being displayed.

    :attr height: The height in rows of a page in the display.
    :attr text: The raw text being paginated.
    :attr title: The title of the document.
    :attr width: The width in characters of a page in the display.
    :prop pages: The paginated document. It is a tuple of tuples, where
        each page is a tuple of the text lines that make up the page.
    :prop page_count: The number of pages in the document.
    """
    def __init__(
        self,
        text: str = '',
        title: str = '',
        height: int = 20,
        width: int = 76,
        wrap_mode: str = 'detect'
    ) -> None:
        """Initialize an instance of the class.

        :param text: (Optional.) The raw text to paginate.
        :param title: (Optional.) The title of the document.
        :param height: (Optional.) The height of a page in the display.
        :param width: (Optional.) The width of a page in the display.
        :param wrap_mode: (Optional.) How the text is wrapped.
        :return: None.
        :rtype: NoneType
        """
        self.height = height
        self.width = width
        self.wrap_mode = wrap_mode
        self.title = title
        self.text = text

    @property
    def pages(self) -> tuple[tuple[str, ...], ...]:
        """The paged text."""
        if '_pages' not in self.__dict__:
            self._pages = self._paginate()
        return self._pages

    @property
    def page_count(self) -> int:
        """The number of pages in the paged text."""
        return len(self.pages)

    # Public methods.
    def reflow(self, wrap_mode: str) -> None:
        """Reflow and repaginate the document.

        :param wrap_mode: (Optional.) How the text is wrapped.
        :return: None.
        :rtype: NoneType
        """
        self.wrap_mode = wrap_mode
        del self._pages

    # Utility methods.
    def _paginate(self) -> tuple[tuple[str, ...], ...]:
        """Paginate the text.

        :return: The pagenated text.
        :rtype: tuple
        """
        # Flow the text based on the wrapping mode.
        if self.wrap_mode == 'detect':
            wrapped = self._detect()
        elif self.wrap_mode == 'long':
            wrapped = self._long()
        elif self.wrap_mode == 'man':
            wrapped = self._man()
        elif self.wrap_mode == 'no_wrap':
            wrapped = self._no_wrap()

        # Paginate the text.
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

    def _remove_hard_wrapping(self, text: str) -> str:
        """Remove any hard wrapping from a given string. Single
        newlines are considered hard wrapping. Doubled newlines are
        considered paragraph breaks.

        :param text: The text to remove the wrapping from.
        :return: The cleaned text.
        :rtype: str
        """
        # We only need to do work if there are newlines in the text.
        if '\n' not in text:
            return text

        # Because we are watching for bulleted lists, we have to go
        # through the text line by line.
        lines = text.split('\n')
        result = ''
        for line in lines:
            if not line:
                result = result.rstrip()
                result += '\n'
            elif match(r'^\s*[*]\s', line):
                result += line
                result += '\n'
            else:
                result += line
                result += ' '
        return result

    # Wrap modes.
    def _detect(self) -> tuple[str, ...]:
        unwrapped = self._remove_hard_wrapping(self.text)
        paragraphed = unwrapped.split('\n')
        pwrapped = []
        blist = []
        for p in paragraphed:
            if match(r'^\s*[*]\s', p):
                blist.append(p)
            else:
                if blist:
                    pwrapped.append(blist)
                    blist = []
                pwrapped.append(wrap(p, width=self.width))
        wrapped = []
        for paragraph in pwrapped:
            wrapped.extend(paragraph)
            wrapped.append('')
        return tuple(wrapped)

    def _long(self) -> tuple[str, ...]:
        split_ = self.text.split('\n')
        wrapped = []
        for line in split_:
            if len(line) <= self.width:
                wrapped.append(line)
            else:
                wline = wrap(line, self.width)
                wrapped.extend(wline)
        return tuple(wrapped)

    def _man(self) -> tuple[str, ...]:
        wrapped = man.main(self.text, width=self.width)
        split = wrapped.split('\n')
        return tuple(split)

    def _no_wrap(self) -> tuple[str, ...]:
        wrapped = self.text.split('\n')
        trunced = [line[0:self.width].rstrip() for line in wrapped]
        return tuple(trunced)


# Terminal controller class.
class Viewer:
    """Manage the terminal.

    :attr term: The terminal the text is being displayed in.
    :prop page_height: The displayable height of the page in rows.
    :prop page_width: The displayable width of the page in characters.
    """
    def __init__(self, term: Terminal = Terminal()) -> None:
        """Initialize an instance of the class.

        :param term: (Optional.) The terminal the text is being
            displayed in.
        :return: None.
        :rtype: NoneType
        """
        self.term = term

    # Properties.
    @property
    def page_height(self) -> int:
        """The displayable height of a page."""
        return self.term.height - 4

    @property
    def page_width(self) -> int:
        """The displayable width of a page."""
        return self.term.width - 4

    # Screen output methods.
    def clear(self) -> None:
        """Clear the text area."""
        line = ' ' * (self.page_width)
        for y in range(2, self.term.height - 2):
            print(self.term.move(y, 2) + line)

    def draw_frame(self, frame_type: str = 'light') -> None:
        """Draw the frame around the page.

        :param frame_type: (Optional.) The thickness of the frame. It
            defaults to 'light'.
        around the page.
        :return: None.
        :rtype: NoneType
        """
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

        print(self.term.move(0, 0) + top, end='')
        for y in range(1, self.term.height - 1):
            print(self.term.move(y, 0) + mid, end='')
        print(self.term.move(self.term.height - 1, 0) + bot, end='')

    def draw_commands(
        self,
        commands: Sequence[Command],
        frame_type: str = 'light'
    ) -> None:
        """Draw the command hints.

        :param commands: A sequence of the commands that should be
            displayed in the terminal.
        :param frame_type: (Optional.) The thickness of the frame. It
            defaults to 'light'.
        :return: None.
        :rtype: NoneType
        """
        x = 1
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
            y = self.term.height - 1
            print(self.term.move(y, x) + hint, end='', flush=True)
            x += len(hint)

    def draw_page(self, text: Sequence[str]) -> None:
        """Draw the text for the page.

        :param text: A sequence of text lines to display in the
            terminal.
        :return: None.
        :rtype: NoneType
        """
        for i, line in enumerate(text):
            y = i + 2
            print(self.term.move(y, 2) + line)

    def draw_prompt(
        self,
        prompt: str = '',
        frame_type: str = 'light'
    ) -> tuple[int, int]:
        """Draw an input prompt at the bottom of the terminal.

        :param prompt: (Optional.) A prompt to explain the type of
            input needed to the user.
        :param frame_type: (Optional.) The thickness of the frame. It
            defaults to 'light'.
        :return: None.
        :rtype: NoneType
        """
        frame = Box(frame_type)
        y = self.term.height - 1
        x = len(prompt) + 6
        field_tmp = (
            frame.rside
            + '{} > '
            + self.term.reverse
            + ' '
            + self.term.normal
            + frame.lside
        )
        print(
            self.term.move(y, 0)
            + frame.lbot
            + frame.bot * (self.term.width - 2)
            + frame.rbot,
            end=''
        )
        print(
            self.term.move(y, 2) + field_tmp.format(prompt),
            end='',
            flush=True
        )
        return y, x

    def draw_status(
        self,
        title: str = '',
        page_num: int = 0,
        page_count: int = 0,
        frame_type: str = 'light'
    ) -> None:
        """Draw the status on top of the page.

        :param title: (Optional.) The title of the document being
            viewed. It defaults to an empty string. If no title is
            given, no title will be displayed.
        :param page_num: (Optional.) The current number of the page
            being viewed. It defaults to zero. If no number is given,
            no page number will be displayed.
        :param page_count: (Optional.) The total number of pages in
            the documents. It defaults to zero.
        :param frame_type: (Optional.) The thickness of the frame. It
            defaults to 'light'.
        :return: None.
        :rtype: NoneType
        """
        frame = Box(frame_type)
        field_tmp = frame.rside + '{}' + frame.lside
        if title:
            print(self.term.move(0, 1) + field_tmp.format(title))
        if page_num:
            field = field_tmp.format(f'{page_num}/{page_count}')
            x = self.term.width - len(field) - 1
            print(self.term.move(0, x) + field)

    # User input methods.
    def get_key(self) -> str:
        """Return the character for the next key pressed.

        :return: The key pressed as a string.
        :rtype: str
        """
        with self.term.cbreak():
            key = self.term.inkey()
        return str(key)

    def get_str(self, prompt: str = '', frame_type: str = 'light') -> str:
        """Return a character sequence given by the user.

        :param prompt: (Optional.) A prompt to explain the type of
            input needed to the user.
        :param frame_type: (Optional.) The thickness of the frame. It
            defaults to 'light'.
        :return: None.
        :rtype: NoneType
        """
        keys = []
        with self.term.cbreak():
            if prompt:
                frame = Box(frame_type)
                y, x = self.draw_prompt(prompt, frame_type)
            while (key := self.term.inkey()) != Keystroke('\n'):
                keys.append(key)
                if prompt:
                    print(
                        self.term.move(y, x)
                        + str(key)
                        + self.term.reverse
                        + ' '
                        + self.term.normal
                        + frame.lside,
                        end='',
                        flush=True
                    )
                    x += 1
        return ''.join(str(k) for k in keys)


# Basic command functions.
def back_page(viewer: Viewer, pager: Pager, page: int) -> int:
    """Advance to the next page of the document.

    :param viewer: The Viewer controlling the terminal display.
    :param pager: The Pager managing the document being viewed.
    :param page: The page number currently being viewed.
    :return: The new page number being viewed.
    :rtype: int
    """
    if page > 0:
        page -= 1
        return update_page(viewer, pager, page)
    return page


def flow(viewer: Viewer, pager: Pager, page: int) -> int:
    """Change how the text in the document is flowed.

    :param viewer: The Viewer controlling the terminal display.
    :param pager: The Pager managing the document being viewed.
    :param page: The page number currently being viewed.
    :return: The new page number being viewed.
    :rtype: int
    """
    mode_list = [
        Command('n', 'none'),
        Command('d', 'detect'),
        Command('m', 'man'),
    ]
    viewer.draw_frame()
    viewer.draw_status(
        pager.title,
        page + 1,
        pager.page_count
    )
    viewer.draw_commands(mode_list)
    viewer.clear()
    viewer.draw_page(pager.pages[page])
    key = viewer.get_key()
    wrap_mode = 'detect'
    if key == 'n':
        wrap_mode = 'no_wrap'
    elif key == 'm':
        wrap_mode = 'man'
    pager.reflow(wrap_mode)
    return update_page(viewer, pager, 0)


def jump_to_page(viewer: Viewer, pager: Pager, page: int) -> int:
    """Jump to a given page in the document.

    :param viewer: The Viewer controlling the terminal display.
    :param pager: The Pager managing the document being viewed.
    :param page: The page number currently being viewed.
    :return: The new page number being viewed.
    :rtype: int
    """
    prompt = 'Jump to page'
    page = int(viewer.get_str(prompt)) - 1
    return update_page(viewer, pager, page)


def next_page(viewer: Viewer, pager: Pager, page: int) -> int:
    """Advance to the next page of the document.

    :param viewer: The Viewer controlling the terminal display.
    :param pager: The Pager managing the document being viewed.
    :param page: The page number currently being viewed.
    :return: The new page number being viewed.
    :rtype: int
    """
    if page < pager.page_count - 1:
        page += 1
        return update_page(viewer, pager, page)
    return page


# Utility functions
def build_commands(page_count: int, page: int) -> list[Command]:
    """Return the available commands.

    :param page_count: The number of pages in the document.
    :param page: The current page being viewed.
    :return: A list of the commands available for the given page.
    :rtype: list
    """
    commands = []
    if page > 0:
        commands.append(Command('b', 'back'))
    commands.append(Command('f', 'flow'))
    commands.append(Command('j', 'jump'))
    if page < page_count - 1:
        commands.append(Command('n', 'next'))
    commands.append(Command('x', 'exit'))
    return commands


def load_document(
    filename: str,
    height: int,
    width: int,
    wrap_mode: str = 'detect'
) -> Pager:
    """Load a document from a file.

    :param filename: The path to the file to load.
    :param height: The height in rows of the page display area in the
        terminal.
    :param width: The width in columns of the page display area in the
        terminal.
    :param wrap_mode: Set how the Pager wraps the text.
    :return: A Pager containing the contents of the file.
    :rtype: Pager
    """
    # Validate file.
    path = Path(filename)
    if not path.exists():
        msg = f'File {filename} does not exist.'
        raise FileNotFoundError(msg)
    if path.is_dir():
        msg = f'{filename} is a directory.'
        raise IsADirectoryError(msg)

    # Open and return file.
    text = read_file(path)
    title = filename.split('/')[-1]
    return Pager(text, title, height, width, wrap_mode)


def read_file(filename: str | Path) -> str:
    """Read the contents of a file.

    :param filename: The path to the file to read.
    :return: The contents of the file as a string.
    :rtype: str
    """
    with open(filename) as fh:
        text = fh.read()
    return text


def update_page(viewer: Viewer, pager: Pager, page: int) -> int:
    """Jump to a given page in the document.

    :param viewer: The Viewer controlling the terminal display.
    :param pager: The Pager managing the document being viewed.
    :param page: The page number currently being viewed.
    :return: The new page number being viewed.
    :rtype: int
    """
    # Build the command list.
    commands = build_commands(pager.page_count, page)

    # Update frame.
    viewer.draw_frame()
    viewer.draw_status(
        pager.title,
        page + 1,
        pager.page_count
    )
    viewer.draw_commands(commands)

    # Update page.
    viewer.clear()
    viewer.draw_page(pager.pages[page])
    return page


# The main loop.
def main(filename: str, wrap_mode: str = 'detect') -> None:
    """The main program loop for clireader.

    :param filename: The path to the file to display.
    :return: None.
    :rtype: NoneType
    """
    current_page = 0
    viewer = Viewer()
    pager = load_document(
        filename,
        viewer.page_height,
        viewer.page_width,
        wrap_mode
    )

    with viewer.term.fullscreen(), viewer.term.hidden_cursor():
        update_page(viewer, pager, current_page)
        while True:
            command = viewer.get_key().casefold()
            if command == 'b':
                current_page = back_page(viewer, pager, current_page)
            elif command == 'f':
                current_page = flow(viewer, pager, current_page)
            elif command == 'j':
                current_page = jump_to_page(viewer, pager, current_page)
            elif command == 'n':
                current_page = next_page(viewer, pager, current_page)
            elif command == 'x':
                break
