"""
man
~~~

A parser for documents formatted with the man troff macros.
"""
from dataclasses import dataclass


# Token classes.
class Token:
    """A superclass for lexical tokens."""


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
    tokens = []
    state = None
    buffer = ''
    for line in lines:
        token = None

        if state and not line.startswith('.'):
            buffer = f'{buffer} {line}'
        elif state:
            args = [s for s in buffer.split(' ') if s]
            token = state(*args)
            tokens.append(token)
            state = None

        # Determine the relevant macro for the line and create
        # the token for that macro.
        if line.startswith('.SH'):
            args = line.split(' ')
            if args[1:]:
                token = Section(*args[1:])
            else:
                state = Section

        if line.startswith('.SS'):
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
        if state:
            args = [s for s in buffer.split(' ') if s]
            token = state(*args)
            tokens.append(token)
            state = None

    return tuple(tokens)
