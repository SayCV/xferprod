"""
Various helper functions that xferprod uses. Mostly for interacting with
users in a nice way.
"""

import functools
import logging
import re
import sys
from pathlib import Path as path
from string import Template

import colorama
import rtoml

XFERPROD_ROOT = path(__file__).resolve().parent

def logger_init(args=None):

    # Setup logging for displaying background information to the user.
    logging.basicConfig(
        style="{", format="[{levelname:<7}] {message}", level=logging.INFO
    )
    # Add a custom status level for logging.
    logging.addLevelName(25, "STATUS")
    logging.Logger.status = functools.partialmethod(logging.Logger.log, 25)
    logging.status = functools.partial(logging.log, 25)

    # Change logging level if `--debug` was supplied.
    if args and args.debug:
        logging.getLogger("").setLevel(logging.DEBUG)

def set_terminal_title(title):
    if sys.stdout.isatty():
        sys.stdout.write(colorama.ansi.set_title(title))
        sys.stdout.flush()

def get_variables_recursive(data: dict):
    lookup = r'.*\${(.*)}.*'
    pattern = re.compile(lookup)
    d = {}
    for k, v in data.items():
        if isinstance(v, dict):
            get_variables_recursive(data[k])
        elif isinstance(v, list):
            continue
        else:
            matched = pattern.findall(v)
            if len(matched) > 0:
                t = Template(v)
                vv = t.substitute(d)
                v = vv
                pass
            globals()[f"__lol__{k}"] = v # vars()
            d[k] = v
        pass

def update_variables_recursive(data: dict) -> str:
    get_variables_recursive(data)
    data_str = rtoml.dumps(data)
    t = Template(data_str)
    d = {}
    for v in globals():
        if v.startswith('__lol__'):
            d[v[7:]] = globals()[v]
    data_str = t.substitute(d)
    return rtoml.loads(data_str)
