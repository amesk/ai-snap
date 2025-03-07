#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Alexei Eskenazi. All rights reserved
#
# AI-Snap utility
#
# Author: amesk <alexei.eskenazi@gmail.com>
#

import os, sys
import shutil
from pathlib import Path

from os.path import (
    join,
    dirname,
    realpath,
)

root_dir = realpath(join(dirname(__file__), ".."))

def delete_directory(path):
    try:
        path = Path(path)
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
            print(f"'{path}' removed")
        else:
            print(f"'{path}' doesn't exist or not a directory")
    except Exception as e:
        print(f"Error while removing '{path}': {e}")


def delete_files_by_mask(directory, pattern):
    try:
        directory = Path(directory)
        files_to_delete = list(directory.glob(pattern))
        
        if not files_to_delete:
            print(f"No files matching '{pattern}' found in directory '{directory}'.")
            return

        for file_path in files_to_delete:
            try:
                file_path.unlink()
                print(f"File '{file_path}' successfully deleted.")
            except Exception as e:
                print(f"Error deleting file '{file_path}': {e}")

    except Exception as e:
        print(f"Error during file search or deletion: {e}")


if __name__ == "__main__":
    if os.getcwd() != root_dir:
        print("Please run from root directory")
        sys.exit(1)

    delete_directory(Path(join(root_dir, "dist")))
    delete_directory(Path(join(root_dir, "build")))
    delete_directory(Path(join(root_dir, "ai_snap.egg-info")))
    delete_files_by_mask(root_dir, "*.spec")
    delete_files_by_mask(root_dir, "Changelog.txt")

