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
                buffer = f'{buffer} {line}'
        elif state is Paragraph:
            token = state(buffer)
            tokens.append(token)
            state = None
        elif state:
            args = [s for s in buffer.split(' ') if s]
            token = state(*args)
            tokens.append(token)
            state = None

        # Determine the relevant macro for the line and create
        # the token for that macro.
        if line.startswith('.EE'):
            token = None

        elif line.startswith('.EX'):
            state = Example

        elif line.startswith('.P'):
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

        # Add the token to the lexed document.
        if token:
            tokens.append(token)
    else:
        if state is Paragraph:
            token = state(buffer)
            tokens.append(token)
            state = None
        elif state:
            args = [s for s in buffer.split(' ') if s]
            token = state(*args)
            tokens.append(token)
            state = None

    return tuple(tokens)
