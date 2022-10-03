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

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        return str(self), margin, indent


@dataclass
class NonPrinting(Token):

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        return '', margin, indent


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


@dataclass
class ContainerToken(Token):
    """A superclass for tokens that contain other tokens."""
    def _parse_contents(
        self,
        contents: list[Token],
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> str:
        """Parse the text tokens of the token."""
        # Remove pre-existing hard wrapping.
        text_like = (Text, Option, EmailAddress, Url)
        if all(isinstance(token, text_like) for token in contents):
            lines = [token.parse(width)[0].rstrip() for token in contents]
            paragraph = ' '.join(line for line in lines)

            # Wrap the text for the width, margin, and indent.
            wrapped = [paragraph,]
            if width is not None:
                term = Terminal()
                wrap_width = width - margin - indent
                wrapped = term.wrap(paragraph, wrap_width)

            # Add indentation and return.
            lead = ' ' * (margin + indent)
            text = '\n'.join(f'{lead}{line}' for line in wrapped)
            return f'{text}\n'

        else:
            text = ''
            for token in contents:
                parsed, *_ = token.parse(width, margin, indent)
                text += parsed
            return f'{text.rstrip()}\n'


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

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        act_width = width
        if width is not None:
            act_width = width - margin - indent
        lead = ' ' * (margin + indent)
        text = f'{lead}{self.contents[0].text[:act_width]}\n'
        for token in self.contents[1:]:
            text = f'{text}{lead}{token.text[:act_width]}\n'
        return text, margin, indent


@dataclass
class RelativeIndentEnd(NonPrinting):
    indent: str = '1'

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        return '', margin - int(self.indent), indent


@dataclass
class RelativeIndentStart(NonPrinting):
    indent: str = '1'

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        return '', margin + int(self.indent), indent


@dataclass
class Section(ContainerToken):
    heading_text: str = ''
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        stripped = line.rstrip()
        if not self.heading_text:
            self.heading_text = stripped
            return False
        if not stripped:
            return False
        token: Optional[Token] = _process_font_style_macro(
            line,
            self.contents
        )
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        margin = 0
        indent = 4
        term = Terminal()
        header = f'{term.bold}{self.heading_text}{term.normal}\n'
        contents = self._parse_contents(self.contents, width, margin, indent)
        text = f'{header}{contents}\n'
        return text, margin, indent


@dataclass
class Subheading(ContainerToken):
    subheading_text: str = ''
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        stripped = line.rstrip()
        if not self.subheading_text:
            self.subheading_text = stripped
            return False
        if not stripped:
            return False
        token: Optional[Token] = _process_font_style_macro(
            line,
            self.contents
        )
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        margin = 0
        indent = 4
        term = Terminal()
        head = f'  {term.bold}{self.subheading_text}{term.normal}\n'
        contents = self._parse_contents(self.contents, width, margin, indent)
        text = f'{head}{contents}'
        return f'{text}\n', margin, indent


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

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        title = str(self)
        total_text = len(title) * 2 + len(self.header_middle)
        if width is None:
            width = total_text + 2
        total_gap = width - total_text
        l_gap = ' ' * (total_gap // 2)
        r_gap = ' ' * (-(-total_gap // 2))
        text = f'{title}{l_gap}{self.header_middle}{r_gap}{title}\n\n\n\n'
        return text, margin, indent


# Paragraph tokens.
@dataclass
class Paragraph(ContainerToken):
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if not line:
            return False
        token: Optional[Token] = _process_font_style_macro(
            line,
            self.contents
        )
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        indent = 4
        parsed = self._parse_contents(self.contents, width, margin, indent)
        return f'{parsed}\n', margin, indent


@dataclass
class IndentedParagraph(ContainerToken):
    tag: str = ''
    indent: str = ''
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if not line:
            return False
        token: Optional[Token] = _process_font_style_macro(line)
        if token:
            self.contents.append(token)
            return False
        return True

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        # .IP doesn't change the margin, but it will change the indent.
        if self.indent:
            indent = int(self.indent)

        # Build the paragraph.
        contents = self._parse_contents(self.contents, width, margin, indent)

        # If the paragraph is tagged, add the tag.
        lead = ' ' * margin
        if len(self.tag) < indent:
            gap = margin + indent
            text = f'{lead}{self.tag: <{indent}}{contents[gap:]}\n'
        else:
            text = f'{lead}{self.tag}\n{contents}\n'

        # Return the text, margin, and new indent.
        return text, margin, indent


@dataclass
class TaggedParagraph(ContainerToken):
    indent: str = ''
    tag: list[str] = field(default_factory=list)
    contents: list[Token] = field(default_factory=list)
    _tag_flag: bool = False

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        token: Optional[Token] = None
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

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        # .TP doesn't change the margin, but it will change the indent.
        if self.indent:
            indent = int(self.indent)

        # Build the paragraph.
        contents = self._parse_contents(self.contents, width, margin, indent)

        # If the paragraph is tagged, add the tag.
        lead = ' ' * margin
        if len(self.tag) == 1 and len(self.tag[0]) < indent:
            gap = margin + indent
            text = f'{lead}{self.tag[0]: <{indent}}{contents[gap:]}\n'
        else:
            text = f'{lead}{self.tag[0]}\n{contents}\n'

        # Return the text, margin, and new indent.
        return text, margin, indent


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
class Synopsis(ContainerToken):
    command: str
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        token: Optional[Token] = None
        if (
            is_macro_type(STRUCTURE_TOKENS, line)
            or is_macro_type(PARAGRAPH_TOKENS, line)
        ):
            return True

        if line.startswith('.YS'):
            pass

        elif line.startswith('.OP'):
            args = line.rstrip().split(' ')
            token = Option(*args[1:])
            self.contents.append(token)

        elif line.startswith('.SY'):
            args = line.rstrip().split(' ')
            token = Synopsis(args[1])
            self.contents.append(token)

        return False

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        if any(isinstance(token, Synopsis) for token in self.contents):
            text = self._parse_multiple_synopsis(width, margin, indent)
            return text, margin, indent
        text = self._parse_single_synopsis(width, margin, indent)
        return text, margin, indent

    def _parse_multiple_synopsis(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 0
    ) -> str:
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
        text = ''
        for synopsis in synopses:
            parsed, *_ = synopsis.parse(width, margin, indent)
            text = f'{text}{parsed.rstrip()}\n'
        return f'{text}\n'

    def _parse_single_synopsis(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> str:
        # Build the command label.
        term = Terminal()
        lead = ' ' * (margin + indent)
        command = f'{lead}{term.bold}{self.command}{term.normal}'

        # Build the options list.
        opt_indent = len(self.command) + 1 + margin + indent
        options = self._parse_contents(
            self.contents,
            width,
            margin,
            opt_indent
        )

        # Build the final output and return.
        text = f'{command} {options[opt_indent:]}\n'
        return text


# Hyperlink and email tokens.
@dataclass
class EmailAddress(ContainerToken):
    address: str
    contents: list[Token] = field(default_factory=list)
    punctuation: str = ''

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if (
            is_macro_type(STRUCTURE_TOKENS, line)
            or is_macro_type(PARAGRAPH_TOKENS, line)
            or is_macro_type(COMMAND_SYNOPSIS_TOKENS, line)
        ):
            return True

        if line.startswith('.ME'):
            args = line.rstrip().split(' ')
            if len(args) > 1:
                self.punctuation = args[1]

        elif line:
            token = Text(line.rstrip())
            self.contents.append(token)

        return False

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        term = Terminal()
        addr = f'mailto:{self.address}'
        text = self._parse_contents(self.contents, None, 0, 0).rstrip()
        link = term.link(addr, text)
        return f'{link}{self.punctuation}', margin, indent


@dataclass
class Url(ContainerToken):
    address: str
    contents: list[Token] = field(default_factory=list)
    punctuation: str = ''

    def process_next(self, line: str) -> bool:
        """Process the next line."""
        if (
            is_macro_type(STRUCTURE_TOKENS, line)
            or is_macro_type(PARAGRAPH_TOKENS, line)
            or is_macro_type(COMMAND_SYNOPSIS_TOKENS, line)
        ):
            return True

        if line.startswith('.UE'):
            args = line.rstrip().split(' ')
            if len(args) > 1:
                self.punctuation = args[1]

        elif line:
            token = Text(line.rstrip())
            self.contents.append(token)

        return False

    def parse(
        self,
        width: Optional[int] = None,
        margin: int = 0,
        indent: int = 4
    ) -> tuple[str, int, int]:
        """Parse the token into text."""
        term = Terminal()
        text = self._parse_contents(self.contents, None, 0, 0).rstrip()
        link = term.link(self.address, text)
        return f'{link}{self.punctuation}', margin, indent


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
    '.rs': RelativeIndentStart,
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
        folded = line.casefold()
        if folded.startswith(macro.casefold()):
            return True
    return False


def _process_font_style_macro(
    line: str,
    contents: Optional[list[Token]] = None
) -> Optional[Token]:
    """Process a font style macro discovered while processing a
    multiline macro.
    """
    token: Optional[Token] = None
    stripped = line.rstrip()
    if (
        is_macro_type(STRUCTURE_TOKENS, stripped)
        or is_macro_type(PARAGRAPH_TOKENS, stripped)
        or is_macro_type(COMMAND_SYNOPSIS_TOKENS, stripped)
    ):
        pass
    elif (
        not stripped.startswith('.')
        and contents
        and isinstance(contents[-1], Text)
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
    else:
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
        if state:
            pass

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
def parse(tokens: Sequence[Token], width: Optional[int] = 80) -> str:
    """Parse the tokens into a string."""
    text = ''
    footer = ''
    margin = 0
    indent = 4

    for token in tokens:
        if isinstance(token, Title):
            footer = token.footer(width)
        parsed, margin, indent = token.parse(width, margin, indent)
        text += parsed

    if footer:
        text = f'{text}{footer}'

    return text


# Main line.
def main(text: str, width: Optional[int]) -> str:
    """Parse man-style macros."""
    tokens = lex(text)
    return parse(tokens, width)
