"""
__main__
~~~~~~~~

The mainline of the clireader package when run from the comand line.
"""
from argparse import ArgumentParser
import sys

from clireader import clireader


def parse_cli() -> None:
    """Parse the arguments used to invoke clireader."""
    # Create the parser.
    p = ArgumentParser(
        prog='clireader',
        description='Read text files from the command line.'
    )
    p.add_argument(
        'filename',
        help='The path to the file to read.',
        action='store',
        type=str
    )
    p.add_argument(
        '-l', '--longwrap',
        help='Only rewrap the long lines.',
        action='store_true'
    )
    p.add_argument(
        '-n', '--nowrap',
        help='Do not rewrap the text.',
        action='store_true'
    )

    # Parse the arguments.
    args = p.parse_args()
    wrap_mode = 'detect'
    if args.nowrap:
        wrap_mode = 'no_wrap'
    if args.longwrap:
        wrap_mode = 'long'
    clireader.main(args.filename, wrap_mode=wrap_mode)


if __name__ == '__main__':
    parse_cli()
