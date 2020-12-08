import argparse
import sys
from pathlib import Path

from .core import Thumbnail
from .exceptions import (
    InvalidIDError,
    InvalidURLError,
    NotFetchedError,
    NotFoundError
)


def cli():

    def error(*msg, exc=None):
        _exc = f'{type(exc).__name__}: {e}' if exc else None
        if _exc:
            print(_exc)
        if msg:
            print(*msg, sep='\n')
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

    parser = argparse.ArgumentParser(
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
        choices=(0, 1, 2, 3, 4),
        default=0,
        metavar='{0-4}',
        type=int,
        help='thumbnail size from 0 (largest) to 4 (smallest)'
    )
    args_fetch.add_argument(
        '-t',
        '--timeout',
        type=float,
        default=3.0,
        metavar='<timeout>',
        help='initial connection timeout in seconds; default: %(default)s'
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
        metavar='<dir>',
        help='output directory'
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
    args = parser.parse_args()


    try:
        use_id = Thumbnail._id_re.match(args.input)
        t = Thumbnail(id=args.input) if use_id else Thumbnail(args.input)
    except (InvalidIDError, InvalidURLError):
        error(f"Error: '{args.input}' is not a valid YouTube video URL or ID")

    print(f'Requesting thumbnail for video ID: {t.id}')

    try:
        t.fetch(
            args.size,
            args.webp,
            args.no_fallback,
            args.timeout
        )
    except NotFoundError as e:
        error(
            "Error: Failed to find thumbnail for video ID "
            f"'{e.args[1]}' with size '{e.args[2]}'"
        )

    print(f'Found thumbnail with size: {t.size}')

    try:
        t.save(
            args.dir,
            args.filename,
            args.overwrite,
            args.no_mkdir
        )
    except NotADirectoryError as e:
        error(f'Error: Invalid path: {e.filename}')
    except FileExistsError as e:
        error(f'Error: File already exists: {e.filename}')
    except FileNotFoundError as e:
        error(f'Error: Specified path does not exist: {e.filename}')
    except PermissionError as e:
        error(f'Error: Permission denied: {e.filename}')
    except OSError as e:
        error(exc=e)
    
    print(f'Successfully saved thumbnail to: {t.filepath}')


def main():
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(1)
