import argparse
import requests.exceptions
import shutil
import sys

from .core import Thumbnail
from .exceptions import (
    InvalidIDError,
    InvalidURLError,
    NotFoundError
)
from ._version import __version__


def cli():

    def error(msg):
        print(msg, file=sys.stderr)
        sys.exit(1)

    class CustomHelpFormatter(argparse.HelpFormatter):

        def __init__(self, prog):
            super().__init__(prog, max_help_position=32)

        def _format_action_invocation(self, action):
            if not action.option_strings or action.nargs == 0:
                return super()._format_action_invocation(action)
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            return f"{', '.join(action.option_strings)} {args_string}"

    version_parser = argparse.ArgumentParser(add_help=False)
    version_parser.add_argument(
        '-v',
        '--version',
        help='print the current version and exit',
        action='store_true'
    )
    version_args, remaining_args = version_parser.parse_known_args()

    if version_args.version:
        print(f'pythumb {__version__}')
        sys.exit(0)

    parser = argparse.ArgumentParser(
        parents=[version_parser],
        formatter_class=CustomHelpFormatter,
        prog='pythumb',
        usage='%(prog)s [options] <input>'
    )
    args_fetch = parser.add_argument_group('fetch')
    args_save = parser.add_argument_group('save')

    parser.add_argument(
        'input',
        help='YouTube video URL or ID'
    )
    args_fetch.add_argument(
        '-F',
        '--no-fallback',
        action='store_false',
        help="don't fall back to lower sizes if the requested size is not found"
    )
    args_fetch.add_argument(
        '-s',
        '--size',
        default='maxresdefault',
        metavar='<size>',
        type=str,
        help='thumbnail size'
    )
    args_fetch.add_argument(
        '-t',
        '--timeout',
        type=float,
        default=5.0,
        metavar='<timeout>',
        help='server response timeout in seconds; default: %(default)s'
    )
    args_fetch.add_argument(
        '-w',
        '--webp',
        action='store_true',
        help='use higher quality WebP instead of JPEG format'
    )
    args_save.add_argument(
        '-d',
        '--dir',
        default='.',
        metavar='<dir>',
        help="output directory; '-' outputs to stdout"
    )
    args_save.add_argument(
        '-f',
        '--filename',
        metavar='<filename>',
        help='custom filename; defaults to the video ID'
    )
    args_save.add_argument(
        '-m',
        '--no-mkdir',
        action='store_false',
        help="don't create missing directories"
    )
    args_save.add_argument(
        '-o',
        '--overwrite',
        action='store_true',
        help='overwrite if the file exists'
    )
    args = parser.parse_args(remaining_args)

    output_stdout = True if args.dir == '-' else False
    def log(msg):
        if not output_stdout:
            print(msg)

    try:
        if len(args.input) == 11:
            t = Thumbnail(id=args.input)
        else:
            t = Thumbnail(url=args.input)
    except (InvalidIDError, InvalidURLError):
        error(f"'{args.input}' is not a valid YouTube video URL or ID")

    log(f'Requesting thumbnail for video ID: {t.id}')

    try:
        t.fetch(
            args.size,
            args.webp,
            args.no_fallback,
            args.timeout
        )
    except (ValueError, NotFoundError, requests.exceptions.RequestException) as e:
        error(f'{type(e).__name__}: {e}')

    log(f'Found thumbnail with size: {t.size}')

    if output_stdout:
        try:
            sys.stdout.buffer.write(t.image)
            sys.stdout.buffer.flush()
        except OSError as e:
            error(f'{type(e).__name__}: {e}')
    else:
        try:
            dest = t.save(
                args.dir,
                args.filename,
                args.overwrite,
                args.no_mkdir
            )
        except OSError as e:
            error(f'{type(e).__name__}: {e}')

        log(f'Successfully saved thumbnail to: {dest}')


def main():
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(1)
