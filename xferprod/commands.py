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

    data = helper.toml_load([args.metadata_file])
    target_flows = helper.get_dict_subkey(data, 'target')
    model = args.model if args.model else target_flows[0]
    logger.debug(f"Found available flows: {target_flows} current used: {model}")

    owner = data.get('owner')
    meta_root = owner.get(f"root")
    meta_exportdir = owner.get(f"{model}_exportdir")
    target_root = args.output_dir if args.output_dir else meta_exportdir if meta_exportdir else path.cwd()
    logger.debug(f"Found meta_exportdir: {meta_exportdir}")
    logger.debug(f"Set target_root: {target_root}")

    if meta_root:
        logger.debug(f"Found root class.")
        target = data.get('target').get(model)
        if not target:
            raise XferprodException(f"Invalid value raised at {path(__file__).name} line {sys._getframe().f_lineno}")
        link_dirs = []
        for subdir in target.get('subdir'):
            len_item = len(subdir)
            if len_item < 1:
                raise XferprodException(f"Invalid value raised at {path(__file__).name} line {sys._getframe().f_lineno}")
            elif len_item > 1:
                project_srcdir_part = subdir[0]
                project_dstdir_part = subdir[1]
            else:
                project_srcdir_part = subdir[0]
                project_dstdir_part = subdir[0]
            sub_data = helper.toml_load([path(project_srcdir_part) / 'metadata.toml'])
            sub_meta_srcdir = path(project_srcdir_part) / sub_data.get('owner').get(f"{model}_exportdir")
            sub_meta_dstdir = path(project_dstdir_part)
            link_dirs.append([sub_meta_srcdir, sub_meta_dstdir])
            pass
        #print(*(item for item in link_dirs), sep='\n')
        for link_srcdir, link_dstdir in link_dirs:
            srcdir: path = path(link_srcdir)
            dstdir: path = path(target_root) / link_dstdir
            dstdir_depth = len(dstdir.parts) - 1
            relative_srcdir = path(('../' * dstdir_depth).rstrip('/')) / srcdir
            path(dstdir).parent.mkdir(parents=True, exist_ok=True)
            try:
                dstdir.symlink_to(relative_srcdir, target_is_directory=True)
                print(f"  Linked done: {str(dstdir):32} <<===>> {relative_srcdir}")
            except FileExistsError as e:
                print(f"  Link failed: {str(dstdir):32} ------> {e.args[1]}")
        return

    devops = data.get('devops').get(model)
    flow_files = helper.collection_devops_items(devops)
    copy_succeed_files = []
    copy_failed_files = []
    hidden_files = []
    for file in flow_files:
        #logger.debug(file)
        if not args.hidden and file.src_file.startswith('.'):
            hidden_files.append(f"  {file.src_dir / file.src_file} -> {file.dst_dir / file.dst_file}")
            continue
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
    logger.info(f"Processed total {len(flow_files)} files: {len(copy_succeed_files)} succeed, {len(copy_failed_files)} failed.")
    logger.info(f"Includes {'ignoring' if not args.hidden else 'copy'} {len(hidden_files)} hidden files.")
    print('\n\n')
    logger.info(f"Try copy succeed for following {len(copy_succeed_files)} files:\n")
    print(*(item for item in copy_succeed_files), sep='\n')
    print('\n')
    logger.info(f"Try copy failed for following {len(copy_failed_files)} files:\n")
    print(*(item for item in copy_failed_files), sep='\n')
    print('\n\n')

