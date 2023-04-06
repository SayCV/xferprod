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

from .exceptions import XferprodException

XFERPROD_ROOT = path(__file__).resolve().parent

class XferFileConfig(object):
    def __init__(self, src_dir: path=None, src_file: path=None, dst_dir: path=None, dst_file: path=None):
        self.src_dir = src_dir
        self.src_file = src_file
        self.dst_dir = dst_dir
        self.dst_file = dst_file

    def __str__(self):
        return f"{str(self.src_dir/self.src_file):64} -> {self.dst_dir/self.dst_file}"

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

def get_dict_subkey(data: dict, sub: str=None) -> list:
    sub_field = data.get(sub) if sub else data
    fields = []
    for k, v in sub_field.items():
        if isinstance(v, dict):
            fields.append(k)
    return fields

def collection_devops_items(devops: dict, val: str='files') -> list:
    files = []
    _items = get_dict_subkey(devops)

    for _item in _items:
        _class = devops.get(_item)
        _target: path = _class.get('target')
        _files = _class.get(val)
        for file in _files:
            if len(file) > 2 or len(file) < 1:
                raise XferprodException(f"Value invalid raised at {path(__file__).name} line {sys._getframe().f_lineno}")
            elif len(file) == 2 and not file[1] == '':
                __sub_target = _target / file[1]
            else:
                __sub_target = _target
            src_dir = path(file[0]).parent
            src_file = path(file[0]).name
            _dst_dir = __sub_target
            dst_dir = path(_dst_dir).parent
            dst_file = path(_dst_dir).name
            files.append(XferFileConfig(src_dir, src_file, dst_dir, dst_file))
            pass
    return files
