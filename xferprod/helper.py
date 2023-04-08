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

logger = logging.getLogger(__name__)


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
        elif isinstance(v, str):
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

def collection_devops_items(devops: dict, files_key: str='files') -> list:
    files = []
    _items = get_dict_subkey(devops)

    for _item in _items:
        _class = devops.get(_item)
        _target: path = path(_class.get('target'))
        _files = _class.get(files_key)
        for file in _files:
            if not isinstance(file, list):
                raise XferprodException(f"Invalid list raised at {path(__file__).name} line {sys._getframe().f_lineno}")
            # file:[] = [srcfile, dstfile] | [srcfile]
            filelist_count = len(file) # choice = [1, 2]
            if filelist_count > 2 or filelist_count < 1:
                raise XferprodException(f"Invalid value raised at {path(__file__).name} line {sys._getframe().f_lineno}")

            srcfile = path(file[0])
            #srcdir = path.cwd() if not path(srcfile).is_absolute() else path(srcfile).parent
            srcdir = path(srcfile).parent

            if filelist_count == 2 and not file[1] == '':
                if file[1].endswith('/.'):
                    dstfile = ''
                    dstdir = _target / path(file[1])
                else:
                    dstfile =  path(file[1]).name
                    dstdir = _target / path(file[1]).parent
            else:
                dstfile = ''
                dstdir = _target

            if filename_is_regex(srcfile.name):
                glob_files = []
                dst_dir = dstdir
                for lookup_file in srcdir.glob(srcfile.name):
                    glob_files.append(lookup_file)
                    dst_file = dstfile if not dstfile == '' else lookup_file.name
                    dst_file = auto_renamed_filename(dst_file)
                    files.append(XferFileConfig(lookup_file.parent, lookup_file.name, dst_dir, dst_file))
                    pass
                if len(glob_files) < 1:
                    logger.debug(F"No files found {srcfile.name} in {srcdir}")
                    pass
            else:
                src_dir = srcdir
                src_file = srcfile.name
                dst_dir = dstdir
                dst_file = dstfile if not dstfile == '' else srcfile.name
                dst_file = auto_renamed_filename(dst_file)
                files.append(XferFileConfig(src_dir, src_file, dst_dir, dst_file))
            pass
    return files

def auto_renamed_filename(filename: str) -> str:
    f1_lookup = r'^\d{6}'
    f2_lookup = r'^[a-zA-Z]{4}\d{8}'
    new_filename = filename
    fields = filename.split('-')
    start = len(fields)
    if start > 2:
        pattern = re.compile(f1_lookup)
        f1_matched = pattern.match(fields[0])
        pattern = re.compile(f2_lookup)
        f2_matched = pattern.match(fields[1])
        if f1_matched and f2_matched:
            new_filename = filename[len(fields[0]) + len(fields[1]) + 2:]
    return new_filename

def filename_is_regex(file: str) -> bool:
    is_valid = False
    try :
        open(file, 'r')
    except OSError as e:
        if e.strerror == 'Invalid argument':
            is_valid = True

    return is_valid
