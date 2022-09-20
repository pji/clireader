"""
man
~~~

A parser for documents formatted with the man troff macros.
"""
from dataclasses import dataclass
from typing import Optional


# Token classes.
class Token:
    """A superclass for lexical tokens."""


@dataclass
class Example(Token):
    text: str


@dataclass
class Paragraph(Token):
    text: str


@dataclass
class RelativeIndentEnd(Token):
    indent: str = '1'


@dataclass
class RelativeIndentStart(Token):
    indent: str = '1'


@dataclass
class Section(Token):
    heading_text: str


@dataclass
class Subheading(Token):
    subheading_text: str


@dataclass
class TaggedParagraph(Token):
    _original_text: str

    def __post_init__(self) -> None:
        split = self._original_text.split('\n')
        self.indent = '1'
        if split[0]:
            self.indent = split[0]
        self.tag = split[1]
        self.text = ''
        if len(split) > 2:
            self.text = '\n'.join(split[2:])


@dataclass
class Title(Token):
    title: str
    section: str = ''
    footer_middle: str = ''
    footer_inside: str = ''
    header_middle: str = ''


# Lexer functions.
def lex(text: str) -> tuple[Token, ...]:
    """Lex the given document."""
    lines = text.split('\n')
    tokens: list[Token] = []
    state: Optional[type] = None
    buffer = ''
    for line in lines:
        token = None
        if state and not line.startswith('.'):
            if not buffer:
                buffer = line
            else:
                buffer = f'{buffer}\n{line}'
        elif state in [Paragraph, TaggedParagraph]:
            token = state(buffer)
            tokens.append(token)
            state = None
            token = None
        elif state:
            args = [s for s in buffer.split(' ') if s]
            token = state(*args)
            tokens.append(token)
            state = None
            token = None

        # Determine the relevant macro for the line and create
        # the token for that macro.
        if line.startswith('.EE'):
            token = None

        elif line.startswith('.EX'):
            state = Example

        elif (
            line.startswith('.P')
            or line.startswith('.LP')
            or line.startswith('.PP')
        ):
            state = Paragraph

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
                state = Section

        elif line.startswith('.SS'):
            args = line.split(' ')
            if args[1:]:
                token = Subheading(*args[1:])
            else:
                state = Subheading

        elif line.startswith('.TH'):
            args = line.split(' ')
            token = Title(*args[1:])

        elif (
            line.startswith('.TP')
            or line.startswith('.TQ')
        ):
            args = line.rstrip().split(' ')
            buffer = '1'
            if len(args) > 1:
                buffer = f'{args[1]}'
            state = TaggedParagraph

        # Add the token to the lexed document.
        if token:
            tokens.append(token)
    else:
        if state in [Paragraph, TaggedParagraph]:
            token = state(buffer)
            tokens.append(token)
            state = None
        elif state:
            args = [s for s in buffer.split(' ') if s]
            token = state(*args)
            tokens.append(token)
            state = None

    return tuple(tokens)
