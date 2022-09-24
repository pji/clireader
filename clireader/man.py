"""
man
~~~

A parser for documents formatted with the man troff macros.
"""
from dataclasses import dataclass, field
from typing import Optional


# Base token classes.
@dataclass
class Token:
    """A superclass for lexical tokens."""
    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        return True


@dataclass
class Text(Token):
    text: str


@dataclass
class MultilineFontStyleToken(Text):
    text: str = ''


# Common lexing functions.
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
        token = _build_multiline_font_style_token(Italics, stripped)
    elif stripped.startswith('.RB'):
        token = _build_singleline_font_style_token(RomanBold, stripped)
    elif stripped.startswith('.RI'):
        token = _build_singleline_font_style_token(RomanItalic, stripped)
    elif stripped.startswith('.SB'):
        token = _build_multiline_font_style_token(SmallBold, stripped)
    elif stripped.startswith('.SM'):
        token = _build_multiline_font_style_token(Small, stripped)
    return token


# Specific token classes.
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


@dataclass
class RelativeIndentEnd(Token):
    indent: str = '1'


@dataclass
class RelativeIndentStart(Token):
    indent: str = '1'


@dataclass
class Section(Token):
    heading_text: str = ''

    def process_next(self, line: str) -> bool:
        """Process the next line of text."""
        self.heading_text = line.rstrip()
        return True


@dataclass
class Subheading(Token):
    subheading_text: str = ''

    def process_line(self, line: str) -> None:
        """Process the next line of text."""
        self.subheading_text = line.rstrip()


@dataclass
class Title(Token):
    title: str
    section: str = ''
    footer_middle: str = ''
    footer_inside: str = ''
    header_middle: str = ''


# Paragraph tokens.
@dataclass
class AdditionalHeader(Token):
    value: str


@dataclass
class IndentedParagraph(Token):
    tag: str = ''
    indent: str = '1'
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


@dataclass
class TaggedParagraph(Token):
    indent: str = '1'
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


# Command synopsis tokens.
@dataclass
class Option(Token):
    option_name: str
    option_argument: str = ''


@dataclass
class Synopsis(Token):
    command: str
    contents: list[Token] = field(default_factory=list)

    def process_next(self, line: str) -> bool:
        if line.startswith('.YS'):
            return True

        if line.startswith('.OP'):
            args = line.rstrip().split(' ')
            token = Option(*args[1:])
            self.contents.append(token)

        return False


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


# Font style macros.
@dataclass
class Bold(MultilineFontStyleToken):
    text: str = ''


@dataclass
class Italics(MultilineFontStyleToken):
    text: str = ''


@dataclass
class Small(MultilineFontStyleToken):
    text: str = ''


@dataclass
class SmallBold(MultilineFontStyleToken):
    text: str = ''


@dataclass
class BoldItalic(Text):
    text: str = ''


@dataclass
class BoldRoman(Text):
    text: str = ''


@dataclass
class ItalicBold(Text):
    text: str = ''


@dataclass
class ItalicRoman(Text):
    text: str = ''


@dataclass
class RomanBold(Text):
    text: str = ''


@dataclass
class RomanItalic(Text):
    text: str = ''


# Lexer functions.
def lex(text: str) -> tuple[Token, ...]:
    """Lex the given document."""
    lines = text.split('\n')
    tokens: list[Token] = []
    state: Optional[Token] = None
    buffer = ''
    for line in lines:
        token: Optional[Token] = None

        # Handle multiline macros.
        if state and state.process_next(line):
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
            args = line.split(' ')
            if args[1:]:
                token = Section(*args[1:])
            else:
                state = Section()

        elif line.startswith('.SS'):
            args = line.split(' ')
            if args[1:]:
                token = Subheading(*args[1:])
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

        # Add the token to the lexed document.
        if token:
            tokens.append(token)
    else:
        if state:
            tokens.append(state)
            state = None

    return tuple(tokens)
