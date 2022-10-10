"""
__main__
~~~~~~~~

The mainline of the clireader package when run from the comand line.
"""
from argparse import ArgumentParser
import sys

from clireader import clireader


def parse_cli() -> bool:
    """Parse the arguments used to invoke clireader."""
    # Create the parser.
    p = ArgumentParser(
        prog='clireader',
        description='Read text files from the command line.'
    )
    p.add_argument(
        'filename',
        help='The path to the file to read.',
        nargs='?',
        action='store',
        type=str,
    )
    p.add_argument(
        '-l', '--longwrap',
        help='Only rewrap the long lines.',
        action='store_true'
    )
    p.add_argument(
        '-m', '--man',
        help='Use manlike formatting.',
        action='store_true'
    )
    p.add_argument(
        '-M', '--manhelp',
        help='Help for writing manlike formatting.',
        action='store_true'
    )
    p.add_argument(
        '-n', '--nowrap',
        help='Do not rewrap the text.',
        action='store_true'
    )

    # Parse the arguments.
    args = p.parse_args()

    # Unless invoking manhelp a filepath must be given.
    if not args.filename and not args.manhelp:
        p.print_usage()
        print('clireader: error: must be given either a filename or -M')
        return False

    # Display the help for writing man-like format.
    if args.manhelp:
        wrap_mode = 'man'
        args.filename = ''
        clireader.view_file(
            args.filename,
            wrap_mode=wrap_mode,
            manhelp=args.manhelp
        )
        return True

    # Otherwise, open the file using the wrapping mode.
    wrap_mode = 'detect'
    if args.nowrap:
        wrap_mode = 'no_wrap'
    if args.man:
        wrap_mode = 'man'
    if args.longwrap:
        wrap_mode = 'long'
    if args.manhelp:
        wrap_mode = 'man'
        args.filename = ''
    return clireader.view_file(
        args.filename,
        wrap_mode=wrap_mode,
        manhelp=args.manhelp
    )


if __name__ == '__main__':
    parse_cli()
