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

    # Parse the arguments.
    args = p.parse_args()
    clireader.main(args.filename)


if __name__ == '__main__':
    parse_cli()
