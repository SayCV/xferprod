"""

"""

import logging
import sys
from pathlib import Path as path

import rtoml

from . import helper
from .exceptions import XferprodException

logger = logging.getLogger(__name__)


def run_info(args):
    logger.info(f"Info Command Unimplemented!")


def run_xfer(args):
    logger.info(f"Xfer Command Unimplemented!")

    metadata_file_lookup = [
        args.metadata_file,
    ]
    key_field = data = None
    for metadata_file in metadata_file_lookup:
        try:
            data = rtoml.load(metadata_file)
            key_field = data.get('title')
            logger.info(f"Try lookup {metadata_file} succeeded.")
            break
        except Exception as e:
            logger.debug(f"Try lookup {metadata_file} failed: {e.args[1]}")
            continue
    if not data:
        raise XferprodException(f"Metadata file non exist raised at {path(__file__).name} line {sys._getframe().f_lineno}")
    if not key_field:
        raise XferprodException(f"Metadata file corrupted raised at {path(__file__).name} line {sys._getframe().f_lineno}")
    
    data = helper.update_variables_recursive(data)

    prodflow = data.get('hwdev').get('prodflow')
    prodflow_fields = []
    for k, v in prodflow.items():
        if isinstance(v, dict):
            prodflow_fields.append(k)
    logger.debug(f"Found prodflow fields: {prodflow_fields}")

    prodflow_files = []
    for sub_dir in prodflow_fields:
        sub_target: path = None
        sub_fields = prodflow.get(sub_dir)
        _sub_target = sub_fields.get('target')
        if _sub_target and not _sub_target == '':
            sub_target = path(_sub_target)
        files = sub_fields.get('files')
        for file in files:
            if len(file) > 2 or len(file) < 1:
                raise XferprodException(f"Value invalid raised at {path(__file__).name} line {sys._getframe().f_lineno}")
            elif len(file) == 2 and not file[1] == '':
                __sub_target = sub_target / file[1]
            else:
                __sub_target = sub_target
            src_dir = path(file[0]).parent
            src_file = path(file[0]).name
            _dst_dir = __sub_target
            dst_dir = path(_dst_dir).parent
            dst_file = path(_dst_dir).name
            prodflow_files.append(XferFileConfig(src_dir, src_file, dst_dir, dst_file))
            pass

    for file in prodflow_files:
        print(file)

class XferFileConfig(object):
    def __init__(self, src_dir: path=None, src_file: path=None, dst_dir: path=None, dst_file: path=None):
        self.src_dir = src_dir
        self.src_file = src_file
        self.dst_dir = dst_dir
        self.dst_file = dst_file

    def __str__(self):
        return f"{str(self.src_dir/str(self.src_file)):64} -> {self.dst_dir/self.dst_file}"
