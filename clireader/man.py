"""
man
~~~

A parser for documents formatted with the man troff macros.
"""
from dataclasses import dataclass, field
from textwrap import wrap
from typing import Iterable, Optional, Sequence

from blessed import Terminal


# Base token classes.
@dataclass
class Token:
    """A superclass for lexical tokens."""
    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        return True

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        return str(self)


@dataclass
class Text(Token):
    text: str

    def __str__(self) -> str:
        return f'{self.text}'


@dataclass
class AlternatingFontStyleToken(Text):
    text: str = ''

    def _alternate_style(self, style_a: str, style_b: str) -> str:
        term = Terminal()
        words = self.text.split(' ')
        style = style_a
        formatteds = []
        for word in words:
            formatted = f'{style}{word}{term.normal}'
            formatteds.append(formatted)
            if style == style_a:
                style = style_b
            else:
                style = style_a
        return ' '.join(formatteds)


@dataclass
class MultilineFontStyleToken(Text):
    text: str = ''


# Document structure tokens.
@dataclass
class Example(Token):
    contents: list[Text] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        if line.startswith('.EE'):
            return True

        token = Text(line)
        self.contents.append(token)
        return False

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        text = f'{self.contents[0].text[:width]}\n'
        for token in self.contents[1:]:
            text = f'{text}{token.text[:width]}\n'
        return text


@dataclass
class RelativeIndentEnd(Token):
    indent: str = '1'


@dataclass
class RelativeIndentStart(Token):
    indent: str = '1'


@dataclass
class Section(Token):
    heading_text: str = ''
    contents: list[Text] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        stripped = line.rstrip()
        if not self.heading_text:
            self.heading_text = stripped
            return False
        if not stripped:
            return False
        token: Optional[Text] = _process_font_style_macro(line, self.contents)
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        term = Terminal()
        text = f'{term.bold}{self.heading_text}{term.normal}'
        if not any(isinstance(token, Synopsis) for token in self.contents):
            contents = _parse_contents(self.contents, width, '', 4)
            return f'{text}\n{contents}\n'
        else:
            content_width = width
            if content_width is not None:
                content_width -= 4
            synopses = (t.parse(content_width) for t in self.contents)
            indent = ' ' * 4
            lines = []
            for synopsis in synopses:
                lines.extend(synopsis.split('\n'))
            for line in lines:
                if line:
                    text = f'{text}\n{indent}{line}'
                else:
                    text = f'{text}\n'
        return f'{text}\n'


@dataclass
class Subheading(Token):
    subheading_text: str = ''
    contents: list[Text] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        stripped = line.rstrip()
        if not self.subheading_text:
            self.subheading_text = stripped
            return False
        if not stripped:
            return False
        token: Optional[Text] = _process_font_style_macro(line, self.contents)
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        term = Terminal()
        text = f'  {term.bold}{self.subheading_text}{term.normal}\n'
        text = _parse_contents(self.contents, width, text)
        return f'{text}\n'


@dataclass
class Title(Token):
    title: str
    section: str = ''
    footer_middle: str = ''
    footer_inside: str = ''
    header_middle: str = ''

    def __str__(self) -> str:
        if self.section:
            return f'{self.title.upper()}({self.section})'
        return self.title.upper()

    def footer(self, width: Optional[int] = None) -> str:
        l_text = self.footer_inside
        m_text = self.footer_middle
        r_text = str(self)
        total_text = len(l_text) + len(m_text) + len(r_text)
        if width is None:
            width = total_text + 2
        total_gap = width - total_text
        l_gap = ' ' * (total_gap // 2)
        r_gap = ' ' * (-(-total_gap // 2))
        text = f'\n\n\n{l_text}{l_gap}{m_text}{r_gap}{r_text}\n'
        return text

    def parse(self, width: Optional[int] = None) -> str:
        title = str(self)
        total_text = len(title) * 2 + len(self.header_middle)
        if width is None:
            width = total_text + 2
        total_gap = width - total_text
        l_gap = ' ' * (total_gap // 2)
        r_gap = ' ' * (-(-total_gap // 2))
        text = f'{title}{l_gap}{self.header_middle}{r_gap}{title}\n\n\n\n'
        return text


# Paragraph tokens.
@dataclass
class IndentedParagraph(Token):
    tag: str = ''
    indent: str = '4'
    contents: list[Text] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if not line:
            return False
        token: Optional[Text] = _process_font_style_macro(line)
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        term = Terminal()
        text = ''
        if self.tag:
            text = f'{self.tag}\n'
        return _parse_contents(self.contents, width, text, int(self.indent))


@dataclass
class Paragraph(Token):
    contents: list[Text] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if not line:
            return False
        token: Optional[Text] = _process_font_style_macro(line, self.contents)
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        parsed = _parse_contents(self.contents, width)
        return f'{parsed}\n'


@dataclass
class TaggedParagraph(Token):
    indent: str = '4'
    tag: list[str] = field(default_factory=list)
    contents: list[Text] = field(default_factory=list)
    _tag_flag: bool = False

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        token: Optional[Text] = None
        end = False

        if not self.tag:
            self.tag.append(line.rstrip())
        elif line.startswith('.TQ'):
            self._tag_flag = True
        elif self._tag_flag:
            self.tag.append(line.rstrip())
            self._tag_flag = False
        elif line:
            token = _process_font_style_macro(line, self.contents)
            if line and not token:
                end = True

        if token:
            self.contents.append(token)
        return end

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        term = Terminal()
        indent = int(self.indent)
        contents = _parse_contents(self.contents, width, '', indent)
        if len(self.tag) < int(self.indent):
            text = f'{self.tag: <{indent}}{contents[indent:]}\n'
        else:
            text = f'{self.tag}\n{contents}\n'
        return text


# Command synopsis tokens.
@dataclass
class Option(Token):
    option_name: str
    option_argument: str = ''

    def __str__(self) -> str:
        term = Terminal()
        if self.option_argument:
            return (
                f'[{term.bold}{self.option_name}{term.normal} '
                f'{term.underline}{self.option_argument}{term.normal}]'
            )
        return f'[{term.bold}{self.option_name}{term.normal}]'


@dataclass
class Synopsis(Token):
    command: str
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        token: Optional[Token] = None
        if line.startswith('.YS'):
            return True

        elif line.startswith('.OP'):
            args = line.rstrip().split(' ')
            token = Option(*args[1:])
            self.contents.append(token)

        elif line.startswith('.SY'):
            args = line.rstrip().split(' ')
            token = Synopsis(args[1])
            self.contents.append(token)

        return False

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        if any(isinstance(token, Synopsis) for token in self.contents):
            return self._parse_multiple_synopsis(width)
        return self._parse_single_synopsis(width)

    def _parse_multiple_synopsis(self, width: Optional[int] = None) -> str:
        # Split contents into multiple synopses.
        synopses = []
        synopsis = Synopsis(self.command)
        for token in self.contents:
            if isinstance(token, Synopsis):
                synopses.append(synopsis)
                synopsis = token
            else:
                synopsis.contents.append(token)
        else:
            synopses.append(synopsis)

        # Get the text for each synopsis, concatenate, and return.
        text = synopses[0].parse(width)
        for synopsis in synopses[1:]:
            text = f'{text}{synopsis.parse()}'
        return text

    def _parse_single_synopsis(self, width: Optional[int] = None) -> str:
        term = Terminal()
        text = f'{term.bold}{self.command}{term.normal} '
        indent = ' ' * (len(self.command) + 1)
        opt_width = width
        if width is not None:
            opt_width = width - len(indent)
        options = ' '.join(t.parse(opt_width) for t in self.contents).rstrip()
        lines = term.wrap(options, opt_width)
        text = f'{text}{lines[0]}\n'
        for line in lines[1:]:
            text = f'{text}{indent}{line}\n'
        return text


# Hyperlink and email tokens.
@dataclass
class EmailAddress(Token):
    address: str
    contents: list[Token] = field(default_factory=list)
    punctuation: str = ''

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if line.startswith('.ME'):
            args = line.rstrip().split(' ')
            if len(args) > 1:
                self.punctuation = args[1]
            return True

        if line:
            token = Text(line.rstrip())
            self.contents.append(token)

        return False

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        term = Terminal()
        addr = f'mailto:{self.address}'
        text = _parse_contents(self.contents, width, '', 0).rstrip()
        link = term.link(addr, text)
        return f'{link}{self.punctuation}'


@dataclass
class Url(Token):
    address: str
    contents: list[Token] = field(default_factory=list)
    punctuation: str = ''

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if line.startswith('.UE'):
            args = line.rstrip().split(' ')
            if len(args) > 1:
                self.punctuation = args[1]
            return True

        if line:
            token = Text(line.rstrip())
            self.contents.append(token)

        return False

    def parse(self, width: Optional[int] = None) -> str:
        """Parse the token into text."""
        term = Terminal()
        addr = f'{self.address}'
        text = _parse_contents(self.contents, width, '', 0).rstrip()
        link = term.link(addr, text)
        return f'{link}{self.punctuation}'


# Font style macros.
@dataclass
class Bold(MultilineFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return f'{term.bold}{self.text}{term.normal}'


@dataclass
class Italic(MultilineFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return f'{term.underline}{self.text}{term.normal}'


@dataclass
class Small(MultilineFontStyleToken):
    text: str = ''


@dataclass
class SmallBold(MultilineFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return f'{term.bold}{self.text}{term.normal}'


# Alternating font style macros
@dataclass
class BoldItalic(AlternatingFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return self._alternate_style(term.bold, term.underline)


@dataclass
class BoldRoman(AlternatingFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return self._alternate_style(term.bold, '')


@dataclass
class ItalicBold(AlternatingFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return self._alternate_style(term.underline, term.bold)


@dataclass
class ItalicRoman(AlternatingFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return self._alternate_style(term.underline, '')


@dataclass
class RomanBold(AlternatingFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return self._alternate_style('', term.bold)


@dataclass
class RomanItalic(AlternatingFontStyleToken):
    text: str = ''

    def __str__(self) -> str:
        term = Terminal()
        return self._alternate_style('', term.underline)


# Other tokens.
@dataclass
class Empty(Text):
    text: str = ''


# Token collections.
STRUCTURE_TOKENS: dict[str, Optional[type]] = {
    '.ee': None,
    '.ex': Example,
    '.re': RelativeIndentEnd,
    '.ri': RelativeIndentStart,
    '.sh': Section,
    '.ss': Subheading,
    '.th': Title,
}
PARAGRAPH_TOKENS: dict[str, Optional[type]] = {
    '.ip': IndentedParagraph,
    '.lp': Paragraph,
    '.p': Paragraph,
    '.pp': Paragraph,
    '.tp': TaggedParagraph,
}
COMMAND_SYNOPSIS_TOKENS: dict[str, Optional[type]] = {
    '.sy': Synopsis,
    '.op': Option,
    '.ys': None,
}


# Lexer functions.
def _build_multiline_font_style_token(
    class_: type,
    line: str
) -> MultilineFontStyleToken:
    token = class_()
    if ' ' in line:
        split_ = line.split(' ', 1)
        token.text = split_[1]
    return token


def _build_singleline_font_style_token(
    class_: type,
    line: str
) -> Text:
    split_ = line.split(' ', 1)
    return class_(split_[1])


def is_macro_type(macros: Iterable[str], line: str) -> bool:
    """Does the given line match a non-font style macro."""
    for macro in macros:
        if line.startswith(macro):
            return True
    return False


def _process_font_style_macro(
    line: str,
    contents: Optional[list[Text]] = None
) -> Optional[Text]:
    """Process a font style macro discovered while processing a
    multiline macro.
    """
    token: Optional[Text] = None
    stripped = line.rstrip()
    if (
        not stripped.startswith('.')
        and contents
        and not contents[-1].text
    ):
        token = contents.pop()
        if isinstance(token, MultilineFontStyleToken):
            token.text = stripped
    elif not stripped.startswith('.'):
        token = Text(stripped)
    elif stripped.startswith('.BI'):
        token = _build_singleline_font_style_token(BoldItalic, stripped)
    elif stripped.startswith('.BR'):
        token = _build_singleline_font_style_token(BoldRoman, stripped)
    elif stripped.startswith('.B'):
        token = _build_multiline_font_style_token(Bold, stripped)
    elif stripped.startswith('.IB'):
        token = _build_singleline_font_style_token(ItalicBold, stripped)
    elif stripped.startswith('.IR'):
        token = _build_singleline_font_style_token(ItalicRoman, stripped)
    elif stripped.startswith('.I'):
        token = _build_multiline_font_style_token(Italic, stripped)
    elif stripped.startswith('.RB'):
        token = _build_singleline_font_style_token(RomanBold, stripped)
    elif stripped.startswith('.RI'):
        token = _build_singleline_font_style_token(RomanItalic, stripped)
    elif stripped.startswith('.SB'):
        token = _build_multiline_font_style_token(SmallBold, stripped)
    elif stripped.startswith('.SM'):
        token = _build_multiline_font_style_token(Small, stripped)
    elif (
        not is_macro_type(STRUCTURE_TOKENS, stripped)
        and not is_macro_type(PARAGRAPH_TOKENS, stripped)
        and not is_macro_type(COMMAND_SYNOPSIS_TOKENS, stripped)
    ):
        token = Empty(stripped[1:])
    return token


def lex(text: str) -> tuple[Token, ...]:
    """Lex the given document."""
    lines = text.split('\n')
    tokens: list[Token] = []
    state: Optional[Token] = None
    buffer = ''
    for line in lines:
        token: Optional[Token] = None

        # Handle multiline macros.
        if state:
            if state.process_next(line):
                tokens.append(state)
                state = None

        # Determine the relevant macro for the line and create
        # the token for that macro.
        elif line.startswith('.EE'):
            token = None

        elif line.startswith('.EX'):
            state = Example()

        elif line.startswith('.IP'):
            args = line.rstrip().split(' ')
            if len(args) == 2:
                state = IndentedParagraph(args[1])
            elif len(args) > 2:
                state = IndentedParagraph(args[1], args[2])
            else:
                state = IndentedParagraph()

        elif line.startswith('.MT'):
            args = line.split(' ')
            state = EmailAddress(args[1])

        elif (
            line.startswith('.P')
            or line.startswith('.LP')
            or line.startswith('.PP')
        ):
            state = Paragraph()

        elif line.startswith('.RE'):
            args = line.split(' ')
            if args[1:]:
                token = RelativeIndentEnd(args[1])
            else:
                token = RelativeIndentEnd()

        elif line.startswith('.RS'):
            args = line.split(' ')
            if args[1:]:
                token = RelativeIndentStart(args[1])
            else:
                token = RelativeIndentStart()

        elif line.startswith('.SH'):
            args = line.split(' ', 1)
            if len(args) > 1:
                token = Section(args[1])
            else:
                state = Section()

        elif line.startswith('.SS'):
            args = line.split(' ', 1)
            if len(args) > 1:
                token = Subheading(args[1])
            else:
                state = Subheading()

        elif line.startswith('.SY'):
            args = line.split(' ')
            state = Synopsis(args[1])

        elif line.startswith('.TH'):
            args = line.split(' ')
            token = Title(*args[1:])

        elif line.startswith('.TP'):
            args = line.rstrip().split(' ')
            if len(args) == 2:
                state = TaggedParagraph(args[1])
            elif len(args) > 2:
                state = TaggedParagraph(args[1], [args[2],])
            else:
                state = TaggedParagraph()

        elif line.startswith('.UR'):
            args = line.split(' ')
            state = Url(args[1])

        elif line.startswith('.'):
            token = Empty(line[1:])

        elif line:
            token = Text(line.rstrip())

        # Add the token to the lexed document.
        if token:
            tokens.append(token)

    else:
        if state:
            tokens.append(state)
            state = None

    return tuple(tokens)


# Parsing.
def _parse_contents(
    contents: Iterable[Token],
    width: Optional[int] = None,
    text: str = '',
    indent_size: int = 4
) -> str:
    """Parse the given list of tokens into text."""
    term = Terminal()

    # Remove pre-existing hard wrapping.
    lines = [token.parse(width).rstrip() for token in contents]
    paragraph = ' '.join(line for line in lines)

    # Wrap the text for the given terminal width.
    indent = ' ' * indent_size
    wrapped = [f'{indent}{paragraph}',]
    if width is not None:
        wrapped = term.wrap(paragraph, width - indent_size)

    # Add any line indentation and return.
    for line in wrapped:
        text = f'{text}{indent}{line.rstrip()}\n'
    return text


def parse(tokens: Sequence[Token], width: int = 80) -> str:
    """Parse the tokens into a string."""
    text = ''
    footer = ''
    indent_size = 0
    for token in tokens:
        if isinstance(token, Title):
            footer = token.footer(width)

        if isinstance(token, RelativeIndentStart):
            indent_size += int(token.indent)
        else:
            indent = ' ' * indent_size
            parsed = token.parse(width - indent_size)
            split = parsed.split('\n')
            indented = [f'{indent}{line}'.rstrip() for line in split]
            joined = '\n'.join(indented)
            if text:
                text = f'{text}{joined}'
            else:
                text = joined

    if footer:
        text = f'{text}{footer}'

    return text
