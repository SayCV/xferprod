#!/usr/bin/env python3

"""
### Main command line interface for xferprod.

Each `xferprod` command is mapped to a function which calls the correct
xferprod class function. 
"""

import argparse
import atexit
import logging
import sys
from pathlib import Path as path

import argcomplete

from xferprod import helper

from . import commands
from ._version import __version__
from .exceptions import XferprodException

logger = logging.getLogger(__name__)

################################################################################
# Setup and parse command line arguments
################################################################################

def command_info(args):
    print("xferprod version: {}".format(__version__))
    commands.run_info(args)

def command_xfer(args):
    print("xferprod version: {}".format(__version__))
    commands.run_xfer(args)

def main():
    """
    Read in command line arguments and call the correct command function.
    """

    # Cleanup any title the program may set
    atexit.register(helper.set_terminal_title, "")

    # Create a common parent parser for arguments shared by all subparsers. In
    # practice there are very few of these since xferprod supports a range of
    # operations.
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--debug", action="store_true", help="Print additional debugging information"
    )
    parent.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print xferprod version and exit",
    )
    parent.add_argument(
        "--output-dir",
        type=path,
        help="The export target root directory",
        default=None,
    )
    parent.add_argument(
        "--metadata-file",
        type=path,
        help="Provided the metadata file",
        default=None,
    )

    # Get the list of arguments before any command
    before_command_args = parent.parse_known_args()

    # The top-level parser object
    parser = argparse.ArgumentParser(parents=[parent])

    # Parser for all output formatting related flags shared by multiple
    # commands.
    parent_format = argparse.ArgumentParser(add_help=False)
    parent_format.add_argument(
        "--model",
        help="model",
        default=None,
    )
    parent_format.add_argument(
        "--hidden",
        action="store_true",
        help="hidden files",
    )
    parent_format.add_argument(
        "--link",
        action="store_true",
        help="Link files for save spaces",
    )


    # Support multiple commands for this tool
    subparser = parser.add_subparsers(title="Commands", metavar="")

    # Command Groups
    #
    # Python argparse doesn't support grouping commands in subparsers as of
    # January 2021 :(. The best we can do now is order them logically.

    info = subparser.add_parser(
        "info",
        parents=[parent, parent_format],
        help="Verbose information",
    )
    info.set_defaults(func=command_info)

    xfer = subparser.add_parser(
        "xfer",
        parents=[parent, parent_format],
        help="xfer docs to the target dirctory",
    )
    xfer.set_defaults(func=command_xfer)

    argcomplete.autocomplete(parser)
    args, unknown_args = parser.parse_known_args()

    # Warn about unknown arguments, suggest xferprod update.
    if len(unknown_args) > 0:
        logger.warning(
            "Unknown arguments passed. You may need to update xferprod.")
        for unknown_arg in unknown_args:
            logger.warning('Unknown argument "{}"'.format(unknown_arg))

    # Concat the args before the command with those that were specified
    # after the command. This is a workaround because for some reason python
    # won't parse a set of parent options before the "command" option
    # (or it is getting overwritten).
    for key, value in vars(before_command_args[0]).items():
        if getattr(args, key) != value:
            setattr(args, key, value)

    helper.logger_init(args)

    # Handle deprecated arguments.

    if hasattr(args, "func"):
        try:
            args.func(args)
        except XferprodException as e:
            logger.error(e)
            sys.exit(1)
    else:
        logger.error("Missing Command.\n")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
