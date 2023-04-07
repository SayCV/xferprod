"""

"""

import logging
import shutil
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
    target_flows = helper.get_dict_subkey(data, 'target')
    model = args.model if args.model else target_flows[0]
    logger.debug(f"Found available flows: {target_flows} current used: {model}")
    devops = data.get('devops').get(model)
    flow_files = helper.collection_devops_items(devops)

    meta_exportdir = data.get('owner').get(f"{model}_exportdir")
    target_root = args.output_dir if args.output_dir else meta_exportdir if meta_exportdir else path.cwd()
    logger.debug(f"Found meta_exportdir: {meta_exportdir}")
    logger.debug(f"Set target_root: {target_root}")

    copy_succeed_files = []
    copy_failed_files = []
    for file in flow_files:
        #logger.debug(file)
        src = file.src_dir / file.src_file
        dst = file.dst_dir / file.dst_file
        if not path(src).is_absolute():
            src = path.cwd() / file.src_dir / file.src_file
        if not path(dst).is_absolute():
            dst = target_root / file.dst_dir / file.dst_file

        try:
            if file.dst_file == '' or file.dst_file == '.':
                path(dst).mkdir(parents=True, exist_ok=True)
                new_filename = helper.auto_renamed_filename(file.src_file)
                dst = target_root / file.dst_dir / new_filename
            else:
                path(dst.parent).mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copy_succeed_files.append(f"  {file.src_dir / file.src_file} -> {file.dst_dir / file.dst_file}")
        except Exception as e:
            copy_failed_files.append(f"  {file.src_dir / file.src_file} -> {file.dst_dir / file.dst_file} failed: {e.args[1]}")
            continue

    print('\n')
    logger.info(f"Processed {flow_files.count()} total files: {copy_succeed_files.count()} succeed, {copy_failed_files.count()} failed.")
    print('\n')
    logger.info(f"Try copy succeed for following files:")
    print(*(item for item in copy_succeed_files), sep='\n')
    print('\n')
    logger.info(f"Try copy failed for following files:")
    print(*(item for item in copy_failed_files), sep='\n')
    print('\n')

