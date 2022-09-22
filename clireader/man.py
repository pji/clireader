"""
man
~~~

A parser for documents formatted with the man troff macros.
"""
from dataclasses import dataclass, field
from typing import Optional


# Token classes.
class Token:
    """A superclass for lexical tokens."""
    def process_line(self, line: str) -> None:
        """Process the next line of text."""


# Document structure tokens.
@dataclass
class Example(Token):
    text: str = ''

    def process_line(self, line: str) -> None:
        """Process the next line of text."""
        if not self.text:
            self.text = f'{line}\n'
        elif line:
            self.text = f'{self.text}{line}\n'


@dataclass
class RelativeIndentEnd(Token):
    indent: str = '1'


@dataclass
class RelativeIndentStart(Token):
    indent: str = '1'


@dataclass
class Section(Token):
    heading_text: str = ''

    def process_line(self, line: str) -> None:
        """Process the next line of text."""
        self.heading_text = line.rstrip()


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
class IndentedParagraph(Token):
    tag: str = ''
    indent: str = '1'
    text: str = ''

    def process_line(self, line: str) -> None:
        """Process the next line of text."""
        if not self.text:
            self.text = f'{line}\n'
        elif line:
            self.text = f'{self.text}{line}\n'


@dataclass
class Paragraph(Token):
    text: str = ''

    def process_line(self, line: str) -> None:
        """Process the next line of text."""
        if not self.text:
            self.text = f'{line}\n'
        elif line:
            self.text = f'{self.text}{line}\n'


@dataclass
class TaggedParagraph(Token):
    indent: str = '1'
    tag: str = ''
    text: str = ''
    additional_tags: list[str] = field(default_factory=list)
    _tag_flag: bool = False

    def process_line(self, line: str) -> None:
        """Process the next line of text."""
        if not self.tag:
            self.tag = line.rstrip()
        elif self._tag_flag:
            self.additional_tags.append(line.rstrip())
            self._tag_flag = False
        elif not self.text:
            self.text = f'{line}\n'
        elif line:
            self.text = f'{self.text}{line}\n'


# Command synopsis tokens.
@dataclass
class Synopsis(Token):
    command: str


# Lexer functions.
def lex(text: str) -> tuple[Token, ...]:
    """Lex the given document."""
    lines = text.split('\n')
    tokens: list[Token] = []
    state: Optional[Token] = None
    buffer = ''
    for line in lines:
        # Handle multiline macros.
        if state and not line.startswith('.'):
            state.process_line(line)
        elif isinstance(state, Synopsis) and line.startswith('.YS'):
            tokens.append(state)
            state = None
        elif isinstance(state, TaggedParagraph) and line.startswith('.TQ'):
            state._tag_flag = True
        elif state:
            tokens.append(state)
            state = None

        token: Optional[Token] = None

        # Determine the relevant macro for the line and create
        # the token for that macro.
        if line.startswith('.EE'):
            token = None

        elif line.startswith('.EX'):
            state = Example()

        elif line.startswith('.IP'):
            args = line.rstrip().split(' ')
            if len(args) > 1:
                state = IndentedParagraph(*args[1:])
            else:
                state = IndentedParagraph()

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
            state = Synopsis(*args[1:])

        elif line.startswith('.TH'):
            args = line.split(' ')
            token = Title(*args[1:])

        elif line.startswith('.TP'):
            args = line.rstrip().split(' ')
            if len(args) > 1:
                state = TaggedParagraph(args[1])
            else:
                state = TaggedParagraph()

        # Add the token to the lexed document.
        if token:
            tokens.append(token)
    else:
        if state:
            tokens.append(state)
            state = None

    return tuple(tokens)
