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
    toml = rtoml.dumps(data)

    print(toml)
